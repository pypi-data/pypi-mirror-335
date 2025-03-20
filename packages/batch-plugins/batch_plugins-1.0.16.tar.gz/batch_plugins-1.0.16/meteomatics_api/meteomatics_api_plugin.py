import meteomatics.api as api
from dateutil import parser
import logging
import os
import re
import numpy as np
import pandas as pd
import ast
from datetime import datetime, timedelta
from dateutil import parser as dt_parser

from datasource import DataSource
from meteomatics_api.env_vars import *
from core.core_env_vars import *

class MeteomaticsApiPlugin(DataSource):

    def __init__(self, object_id: str, batch_id: str, pipeline_conf: dict) -> None:
        # Env vars
        self.pipeline_conf = pipeline_conf
        self.object_id = object_id
        self.batch_id = batch_id
        self.table = object_id.split('.')[-1]
        self.username = meteomatics_username
        self.secret = meteomatics_secret
        self.landing_zone_bucket = self.pipeline_conf['ingestion']['landingZone']

        self.coordinates = None
        self.coordinate_len = None
        self.df_coords = None
        self.weather_parameters = self.pipeline_conf['ingestion']['source']['path']
        self.start_dttm = None
        self.end_dttm = None


    def _read_conf(self, conf_path: str):
        """Read configuration CSV
        Args:
            conf_path (str): Full path with filename and extension
        Returns:
            _type_: Pandas dataframe
        """

        file = os.path.join(conf_path)
        df = pd.read_csv(file)
        return df
    


    def connect(self):
        if None in [self.username, self.secret]:
            raise ValueError('Missing Username or Password')
        logging.info('Credentials loaded')
        self.start_dttm = datetime.strptime(str(dt_parser.parse(env_start_date)), "%Y-%m-%d %H:%M:%S.%f%z").replace(minute=0, second=0, microsecond=0)
        self.end_dttm = datetime.strptime(str(dt_parser.parse(env_end_date)), "%Y-%m-%d %H:%M:%S.%f%z").replace(minute=0, second=0, microsecond=0)
        if self.table == 'districtactual':
            self.start_dttm += timedelta(minutes=30)
        if self.table == 'longtermforecast':
            self.start_dttm = self.start_dttm.replace(hour=0)
            self.end_dttm = self.end_dttm.replace(hour=0)

    def read_data(self):
        try:
            self.df_coords = self._read_conf(meteomatics_conf_path)
            self.coordinates = list(zip(self.df_coords['lat'], self.df_coords['lon']))
            logging.info('Coordinates loaded')
        except Exception as e:
            logging.error(f'Failed to retrieve coordinates || {meteomatics_conf_path}')
            raise ValueError(e)

        self.coordinate_len = len(self.coordinates)
        for parameter in ast.literal_eval(self.weather_parameters):
            logging.info(f'Calling API for: {self.coordinate_len} coordinates | Parameter: {parameter} | Start: {self.start_dttm} | End: {self.end_dttm}')
            param = [parameter]
            data_interval = timedelta(minutes=int(meteomatics_interval))
            logging.info(f'Quantiles set to: {meteomatics_quantiles}')
            try:
                if meteomatics_quantiles == '' or meteomatics_quantiles is None:
                    df = api.query_time_series(self.coordinates,
                                               self.start_dttm,
                                               self.end_dttm,
                                               data_interval,
                                               param,
                                               self.username,
                                               self.secret,
                                               model=meteomatics_model,
                                               request_type='POST'
                                              )
                else:
                    df = api.query_time_series(self.coordinates,
                                               self.start_dttm,
                                               self.end_dttm,
                                               data_interval,
                                               param,
                                               self.username,
                                               self.secret,
                                               model=meteomatics_model,
                                               request_type='POST',
                                               ens_select=meteomatics_quantiles
                                            )
            except Exception as e:
                logging.error('Failed to call Meteomatics API')
                raise ValueError(e)
            df = df.reset_index()
            df_merged = pd.merge(df, self.df_coords, on=['lat', 'lon'], how='left')
            param_name = parameter.split(':')[0]
            dt_str = str(self.start_dttm.date())
            self.dfs[f'{param_name}_{dt_str}.csv'] = df_merged
            return self.dfs



    def transform_data(self):
        for key, df in self.dfs.items():
            df = df.replace({np.nan:None})
            parsed_check = self._validate_parsed_file(df)

            if parsed_check:
                continue

            # --------------------------- Rename column headers -------------------------- #
            # Pull variable column name
            if not self.quantiles:
                var = list(filter(lambda x: x not in ['lat', 'lon', 'validdate'], df.columns))[0]
                logging.info(f'Weather variable found: {var}')
                # rename cols

                df.columns = ['latitude', 'longitude', 'valid_date', var, 'district_code']

                # ------------------------------- Pivot columns ------------------------------ #
                df['variable'] = var
                df.rename(columns={var:'value'}, inplace=True)
                logging.info(f'Columns renamed')

                # ------------------------ Apply datatypes to columns ------------------------ #
                df['valid_date'] = [parser.parse(dttm) for dttm in df['valid_date']]
                df['valid_date'] = df['valid_date'].apply(lambda x: x.replace(second=0, microsecond=0))
                logging.info(f'Datatypes applied')

                # ------------------------------ Add new columns ----------------------------- #
                df['date'] = [dttm.date() for dttm in df['valid_date']]
                logging.info(f'New columns added')
            if self.quantiles:
                var = list(filter(lambda x: x not in ['lat', 'lon', 'validdate'], df.columns))
                logging.info(f'Weather variable found: {var}')
                # rename cols

                df.columns = ['latitude', 'longitude', 'valid_date'] + var
                # ------------------------------- Pivot columns ------------------------------ #
                df = pd.melt(df, id_vars=['latitude', 'longitude', 'valid_date', 'district_code'], var_name='variable', value_name='value')
                logging.info(f'Columns melted')
                
                # ------------------------------- Process columns ------------------------------ #
                df[['variable', 'quantile']] = df['variable'].str.split('-', expand=True)
                df['quantile'] = df['quantile'].apply(lambda x: float(re.findall(r'\d+\.\d+', x)[0]))
                                # ------------------------ Apply datatypes to columns ------------------------ #
                df['valid_date'] = [parser.parse(dttm) for dttm in df['valid_date']]
                logging.info(f'Datatypes applied')

                # ------------------------------ Add new columns ----------------------------- #
                df['date'] = [dttm.date() for dttm in df['valid_date']]

           
            final_df = pd.concat([final_df, df], ignore_index=True)

    def close(self):
        logging.info('Closing Meteomatics connection')
