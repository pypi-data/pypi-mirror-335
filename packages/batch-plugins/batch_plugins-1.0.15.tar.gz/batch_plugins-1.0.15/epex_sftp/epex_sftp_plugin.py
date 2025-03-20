import logging
import re
from datetime import datetime
from dateutil import parser as date_parser
import pandas as pd
from datetime import datetime, timedelta
from datasource import DataSource
from core.sftp_driver import SftpDriver
from core.validate_object import ValidateObject
from core.validate_object_dl import ValidateObjectDl
from core.core_env_vars import *
from epex_sftp.env_vars import *

class EpexSftpPlugin(DataSource):
    def __init__(self, object_id: str, batch_id: str, pipeline_conf: dict) -> None:
        self.pipeline_conf = pipeline_conf
        self.object_id = object_id
        self.batch_id = batch_id
        self.file_extension = self.pipeline_conf['ingestion']['file']['namePattern'].replace('.', '')
        self.file_name_pattern = self.pipeline_conf['ingestion']['file']['namePattern']
        self.file_name_filter = self.pipeline_conf['ingestion']['file']['nameFilter']
        self.remote_path = self.pipeline_conf['ingestion']['source']['path']
        self.data_source_host = self.pipeline_conf['ingestion']['source']['host']
        self.data_source_path = self.pipeline_conf['ingestion']['source']['path']
        self.table_name = self.pipeline_conf['name']
        self.dfs = {}
        self.source_path = None
        self.file_name = None
        self.output_df = pd.DataFrame()
        self.matcher = {}

        self.auth_params = {
                'authentication': self.pipeline_conf['ingestion']['source']['authentication'],
                'host': self.data_source_host,
                'port': int(port),
                'username': username,
                'password': password,
                'privatekey': private_key,
                'passphrase': passphrase
            }
        self.source_path_list = None

    def _adjust_epex_source_path_filename(self, start_dt: datetime = None,
         country_name: str = None, country_code: str = None, year: int = None) -> tuple:
        """
        Replaces variables in Source Path and Filename filter for Epex entities        
        Returns: source path and filename filter in a tuple
        """
        start_year = start_dt.year
        current_year = datetime.now().year

        if country_name is not None:
            # Works for Intraday continuous historical (table = intradayconhistorical)
            # "path": "{country}/Intraday Continuous/EOD/Historical/Results",
            source_path = self.data_source_path.format(country=country_name)
        else:
            if start_year == current_year:
                source_path = self.data_source_path.format(CurrentOrHistorical="Current")
            else:
                source_path = self.data_source_path.format(CurrentOrHistorical='Historical')
        if country_code is not None and year is not None:
            # Works for Intraday continuous historical (table = intradayconhistorical)
            # "nameFilter": "Continuous_Statistics-{country_code}-{year}.zip",
            file_name = self.file_name_filter.format(country_code=country_code, year=year)
        else:
            file_name = self.file_name_filter.format(YYYY=start_year)

        return (source_path, file_name)

    def connect(self) -> None:
        self.sftp = SftpDriver(**self.auth_params)
        self.sftp.connect()
        logging.info('Connected.')

    def read_data(self) -> None:
        start_date_formatted = date_parser.parse(env_start_date).date()
        if self.table_name == "intradayconhistorical":
            self.source_path, self.file_name = self._adjust_epex_source_path_filename(start_date_formatted,
                                                                                      epex_country,
                                                                                      epex_country_code,
                                                                                      epex_year)
        else:
            self.source_path, self.file_name = self._adjust_epex_source_path_filename(start_date_formatted)
        init_ValidateObject = ValidateObjectDl(self.pipeline_conf['ingestion']['file']['delimiter'])
        delimiter = init_ValidateObject.get_delimiter()
        source_path_list = self.source_path.split(";")
        for sp in source_path_list:
            logging.info(f'Source PATH: {sp}')
            if self.table_name in ['paneuropeanprices', 'paneuropeanvolumes']:
                sftp_files_list = self.sftp.pull_obj_ids(sp)
            else:
                sftp_files_list = self.sftp.pull_obj_ids_between(sp, env_start_date, env_end_date)
            init_ValidateObject_fr = ValidateObject()
            valid_sftp_list, _ = init_ValidateObject_fr.validate_file_list(sftp_files_list, self.file_extension)
            download_f = [_ for _ in valid_sftp_list if _ in self.file_name.split(';')]
            logging.info(valid_sftp_list)
            logging.info(sp)
            for key, response in self.sftp.read_sftp_files_as_strings(download_f, sp):


                lines_in_file = response.split("\n")

                if self.table == 'intradaycon' or self.table == 'intradayconhistorical':
                    country_name = key.split("-")[1]
                elif self.table in ['paneuropeanvolumes', 'paneuropeanprices']:
                    country_name = key.split("_")[-3]
                    ida_code = key.split("_")[-2]
                else:
                    country_name = key.split("_")[-2]
                    if country_name == "luxembourg" and (self.table == 'auctionspotprices' or self.table == 'auctionspotvolumes'):
                        # To grab country from filename: auction_spot_prices_germany_luxembourg_2024.csv
                        country_name = "germany_" + country_name
                logging.info(f'Country Name: {country_name}')
                
                description_line = lines_in_file[0]
                self.matcher[key]['description_line'] = description_line
                header_line = lines_in_file[1]
                header = header_line.replace("\r", "").split(delimiter)

                logging.info(f"Header: {header}")
                data = []

                for line in lines_in_file[2:-1]:
                    values_in_line = line.replace("\r", "").split(delimiter)
                    data.append(values_in_line)

                df = pd.DataFrame(data, columns=header)
                df["country"] = country_name
                self.dfs[key] = df
            

    def transform_data(self) -> None:
        for key, df in self.dfs.items():
            if self.table == 'intradaycon' or self.table == 'intradayconhistorical':
                country_name = key.split("-")[1]
            elif self.table in ['paneuropeanvolumes', 'paneuropeanprices']:
                country_name = key.split("_")[-3]
                ida_code = key.split("_")[-2]
            else:
                country_name = key.split("_")[-2]
                if country_name == "luxembourg" and (self.table == 'auctionspotprices' or self.table == 'auctionspotvolumes'):
                    # To grab country from filename: auction_spot_prices_germany_luxembourg_2024.csv
                    country_name = "germany_" + country_name
            logging.info(f'Country Name: {country_name}')
            if self.table in ['intradayauctionpriceshh', 'intradayauctionpricesqh', 'intradayauctionpriceshourly', 'auctionspotprices', 'auctionspotpriceshh', 'paneuropeanprices']:
                currency_code = self.matcher[key]['description_line'].split(" ")[-1]
                logging.info(f'Currency Code: {currency_code}')
                df["currency"] = currency_code
            if self.table in ['paneuropeanvolumes', 'paneuropeanprices']:
                df["ida_code"] = ida_code
            if self.table == 'intradayauctionpriceshh' and country_name != 'france':
                df["Off-Peak 1"] = ""
                df["Off-Peak 2"] = ""
                df["Sun Peak"] = ""
                header_ordered = ['Delivery day', 'Hour 1 Q1', 'Hour 1 Q2', 'Hour 2 Q1', 'Hour 2 Q2', 'Hour 3A Q1', 'Hour 3A Q2', 'Hour 3B Q1', 'Hour 3B Q2', 
                                    'Hour 4 Q1', 'Hour 4 Q2', 'Hour 5 Q1', 'Hour 5 Q2', 'Hour 6 Q1', 'Hour 6 Q2', 'Hour 7 Q1', 'Hour 7 Q2', 'Hour 8 Q1', 'Hour 8 Q2', 
                                    'Hour 9 Q1', 'Hour 9 Q2', 'Hour 10 Q1', 'Hour 10 Q2', 'Hour 11 Q1', 'Hour 11 Q2', 'Hour 12 Q1', 'Hour 12 Q2', 
                                    'Hour 13 Q1', 'Hour 13 Q2', 'Hour 14 Q1', 'Hour 14 Q2', 'Hour 15 Q1', 'Hour 15 Q2', 'Hour 16 Q1', 'Hour 16 Q2', 
                                    'Hour 17 Q1', 'Hour 17 Q2', 'Hour 18 Q1', 'Hour 18 Q2', 'Hour 19 Q1', 'Hour 19 Q2', 'Hour 20 Q1', 'Hour 20 Q2', 
                                    'Hour 21 Q1', 'Hour 21 Q2', 'Hour 22 Q1', 'Hour 22 Q2', 'Hour 23 Q1', 'Hour 23 Q2', 'Hour 24 Q1', 'Hour 24 Q2', 
                                    'Minimum', 'Maximum', 'Off-Peak', 'Baseload', 'Off-Peak 1', 'Peakload', 'Sun Peak', 'Off-Peak 2', 'country', 'currency']
                df = df.reindex(columns=header_ordered)

            if self.table == 'intradayauctionpriceshourly' and country_name != 'ch-ida1':
                df["Peakload"] = ""
                df["Off-Peak"] = ""
                df["Off-Peak 1"] = ""
                header_ordered = ['Delivery day', 'Hour 1', 'Hour 2', 'Hour 3A', 'Hour 3B', 'Hour 4', 'Hour 5', 'Hour 6', 
                                    'Hour 7', 'Hour 8', 'Hour 9', 'Hour 10', 'Hour 11', 'Hour 12', 'Hour 13', 'Hour 14', 'Hour 15', 
                                    'Hour 16', 'Hour 17', 'Hour 18', 'Hour 19', 'Hour 20', 'Hour 21', 'Hour 22', 'Hour 23', 'Hour 24', 
                                    'Minimum', 'Maximum', 'Baseload', 'Peakload', 'Off-Peak 2', 'Off-Peak', 'Off-Peak 1', 'country', 'currency']
                df = df.reindex(columns=header_ordered)

            if self.table == 'auctionspotprices' and country_name == 'great-britain':
                df["Middle-Night"] = ""
                df["Early Morning"] = ""
                df["Early Afternoon"] = ""
                df["Late Morning"] = ""
                df["Rush Hour"] = ""
                df["Off-Peak 2"] = ""
                df["Night"] = ""
                df["Off-Peak 1"] = ""
                df["Business"] = ""
                df["Morning"] = ""
                df["High Noon"] = ""
                df["Afternoon"] = ""
                df["Evening"] = ""
                df["Sunpeak"] = ""
                header_ordered = ['Delivery day', 'Hour 1', 'Hour 2', 'Hour 3A', 'Hour 3B', 'Hour 4', 'Hour 5', 'Hour 6', 'Hour 7', 
                                    'Hour 8', 'Hour 9', 'Hour 10', 'Hour 11', 'Hour 12', 'Hour 13', 'Hour 14', 'Hour 15', 'Hour 16', 
                                    'Hour 17', 'Hour 18', 'Hour 19', 'Hour 20', 'Hour 21', 'Hour 22', 'Hour 23', 'Hour 24', 'Minimum', 
                                    'Maximum', 'Middle-Night', 'Early Morning', 'Late Morning', 'Early Afternoon', 'Rush Hour', 
                                    'Off-Peak 2', 'Baseload', 'Peakload', 'Night', 'Off-Peak 1', 'Business', 'Offpeak', 'Morning', 
                                    'High Noon', 'Afternoon', 'Evening', 'Sunpeak', 'country', 'currency']
                df = df.reindex(columns=header_ordered)
            if self.table in ['auctionspotprices', 'paneuropeanvolumes', 'paneuropeanprices']:
                df = self._extract_auction_spot_data_date(df)
                if self.table == 'paneuropeanvolumes':
                    df = self._epex_transpose(df, 'volume', key)
                elif self.table == 'paneuropeanprices':
                    df = self._epex_transpose(df, 'price', key)
                    for col in ["Minimum", "Maximum", "Off-Peak", "Baseload",
                                        "Off-Peak 1", "Peakload", "Sun Peak", "Off-Peak 2"]:
                        if col not in df.columns:
                            logging.info(f"adding {col} column")
                            df[col] = ''
            self.output_df = pd.concat([self.output_df, df], ignore_index=True)
        return self.output_df


    def close(self) -> None:
        self.sftp.disconnect()
        logging.info('External connections closed.')



    def _get_dates_between(self):
        # Convert the input strings to date objects
        if env_start_date is None or env_end_date is None:
            raise Exception('Missing env dates')
        start_date = datetime.strptime(date_parser.parse(env_start_date).strftime('%d/%m/%Y'), '%d/%m/%Y')
        logging.info(f'START DATE: {start_date}')
        end_date = datetime.strptime(date_parser.parse(env_end_date).strftime('%d/%m/%Y'), '%d/%m/%Y')
        logging.info(f'END DATE: {end_date}')
        # Initialize an empty list to store the dates
        date_list = []
        
        # Loop from the start date to the end date
        while start_date <= end_date:
            date_list.append(start_date.strftime('%d/%m/%Y'))
            start_date += timedelta(days=1)
        
        return date_list
    
    def _extract_auction_spot_data_date(self, df: pd.DataFrame):
        days = self._get_dates_between()
        if self.table in ['paneuropeanvolumes', 'paneuropeanprices']:
            days = days[1:]
        return df[df['Delivery day'].isin(days)]
    
    def _epex_transpose(self, df, output_column_name, filename):
        """
        Transforms a DataFrame with columns representing time intervals that start with "Hour" into rows with a datetime column.
        
        Parameters:
            df : dataframe.
            granularity (str): The time granularity ('quarter_hourly', 'half_hourly', or 'hourly').
        Returns:
            pd.DataFrame: Transformed DataFrame with datetime, value columns, and original non-hour columns.
        """
        clock_shift_columns = [col for col in df.columns if col.startswith("Hour 3A")]
        clock_shift_columns_b = [col for col in df.columns if col.startswith("Hour 3B")]

        for col in clock_shift_columns:
            df[col.replace('A', '')] = df[col].combine_first(df[col.replace('A', 'B')])
        df = df.drop(columns=clock_shift_columns + clock_shift_columns_b)
        
        # Identify columns that start with "Hour" and columns to retain
        hour_columns = [col for col in df.columns if col.startswith("Hour")]
        other_columns = [col for col in df.columns if not col.startswith("Hour")]

        # Melt only hour-related columns
        melted_df = pd.melt(df, id_vars=other_columns, value_vars=hour_columns,
                        var_name='Time_Interval', value_name='Value')

        granularity = max(int(re.search(r'Q(\d+)', col).group(1)) for col in hour_columns)
        # Set the base start time
        if granularity == 4:
            # Extract hour and quarter information
            melted_df[['Hour', 'Quarter']] = melted_df['Time_Interval'].str.extract(r'Hour (\d+) Q(\d)')
            melted_df['Hour'] = melted_df['Hour'].astype(int)
            melted_df['Quarter'] = melted_df['Quarter'].astype(int)
            
            # Calculate datetime
            melted_df['datetime'] = (
                pd.to_timedelta(melted_df['Hour'] - 1, unit='h') +
                pd.to_timedelta((melted_df['Quarter'] - 1) * 15, unit='m')
            ).astype(str).str[-8:]

            melted_df = melted_df.drop(columns=['Time_Interval', 'Hour', 'Quarter'])
            
        elif granularity == 2:
            # Extract hour and half-hour information
            melted_df[['Hour', 'HalfHour']] = melted_df['Time_Interval'].str.extract(r'Hour (\d+) Q(\d)')
            melted_df['Hour'] = melted_df['Hour'].astype(int)
            melted_df['HalfHour'] = melted_df['HalfHour'].astype(int)
            
            # Calculate datetime
            melted_df['datetime'] = (
                pd.to_timedelta(melted_df['Hour'] - 1, unit='h') +
                pd.to_timedelta((melted_df['HalfHour'] - 1) * 30, unit='m')
            ).astype(str).str[-8:]
            melted_df = melted_df.drop(columns=['Time_Interval', 'Hour', 'HalfHour'])
            
        elif granularity == 1:
            # Extract hour information
            melted_df['Hour'] = melted_df['Time_Interval'].str.extract(r'Hour (\d+)').astype(int)
            
            # Calculate datetime
            melted_df['datetime'] = (
                pd.to_timedelta(melted_df['Hour'] - 1, unit='h')
            ).astype(str).str[-8:]
            melted_df = melted_df.drop(columns=['Time_Interval', 'Hour'])
        
        else:
            raise ValueError("Invalid granularity. Choose from 'quarter_hourly', 'half_hourly', or 'hourly'.")
        
        # Reorder columns for readability
        melted_df = melted_df[['datetime', 'Value'] + other_columns]
        melted_df['Delivery day'] = melted_df['Delivery day'] + ' ' + melted_df['datetime']
        melted_df = melted_df.drop(columns=['datetime'])
        melted_df['Delivery day'] = pd.to_datetime(melted_df['Delivery day'], format='%d/%m/%Y %H:%M:%S') \
        .dt.tz_localize('CET', ambiguous=True) \
        .dt.tz_convert('UTC') \
        .dt.strftime('%Y-%m-%d %H:%M:%S')
        melted_df = melted_df.rename(columns={"Delivery day": "delivery_datetime", "Value": output_column_name})
        melted_df['ida_code'] = filename.split('_')[-2]
        return melted_df