import logging
from datetime import datetime
import pandas as pd

import sqlalchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

class DataWatcherDriver:

    def __init__(self, func) -> None:
        self.func = func

    def __call__(self, url, schema, table=None, method=None, df=None, statement=None):
        """
        :param: url -> db_sys://user:pass@hostname/db_name
        :param: method -> insert, update etc.
        """

        # -------------- define variables --------------
        self.engine = create_engine(url)
        self.cnxn = self.engine.connect()
        self.schema = schema
        if table is not None:
            self.tbl = table
        if df is not None:
            self.data = df.to_dict(orient='records')
        self.statement = statement

        # -------------- initiating db properties/session --------------
        self.metadata = self.dbMetadata(self.engine, self.schema)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # -------------- execute sql job --------------
        try:
            if method.upper() == 'INSERT':
                self.table = self.dbTable(self.tbl, self.metadata)
                logging.info(f'Inserting data into db {self.schema}.{self.tbl}')
                self.cnxn.execute(self.table.insert(), self.data)

                self.session.commit()
                logging.info(f'Inserted data into db {self.schema}.{self.tbl}')

            if method.upper() == 'SELECT':
                logging.info(f'Selecting data from schema {self.schema}')
                data = self.cnxn.execute(statement)
                self.session.commit()
                logging.info(f'Selected data from schema {self.schema}')
                return data

        except Exception as e:
            self.session.rollback()
            raise e

        finally:
            logging.info(f'Connection to {self.schema} closed')
            self.cnxn.close()

    def __repr__(self):
        return f'url: {self.url}, schema: {self.schema}, table: {self.table}, method: {self.method}, data_length: {len(self.df)}'

    @classmethod
    def dbMetadata(self, engine, schema):
        return sqlalchemy.schema.MetaData(bind=engine, schema=schema)

    @classmethod
    def dbTable(self, table, metadata):
        return sqlalchemy.Table(table, metadata, autoload=True)

class DataWatcherReport:
    def __init__(self, object_id: str, batch_id: str, pipeline_conf: dict, minio_in_list: list[dict], minio_ready_list: list[dict], minio_rejected_list: list[dict], start_tms: datetime, end_tms: datetime) -> None:
        self.object_id = object_id
        self.batch_id = batch_id
        self.pipeline_conf = pipeline_conf
        self.minio_in_list = minio_in_list
        self.minio_ready_list = minio_ready_list
        self.minio_rejected_list = minio_rejected_list
        self.start_tms = start_tms
        self.end_tms = end_tms
        self.sla = (self.end_tms - self.start_tms).seconds

        self.report = {
            'batch_id': [self.batch_id],
            'object_id': [self.object_id],
            'flow_pattern': [self.pipeline_conf['ingestion']['flowPattern']],
            'source_type': [self.pipeline_conf['ingestion']['source']['type']],
            'source_host': [self.pipeline_conf['ingestion']['source']['host']],
            'source_path': [self.pipeline_conf['ingestion']['source']['path']],

            'batch_size': [],
            'batch_size_b': [],
            'accepted_batch_size': [],
            'accepted_batch_size_b': [],
            'rejected_batch_size': [],
            'rejected_batch_size_b': [],
            'archive_folder_name': [self.pipeline_conf['archive']['location']],
            'start_tms': [self.start_tms],
            'end_tms': [self.end_tms],
            'sla': [self.sla],
            'acceptance_rate': []
        }

    def build_fr_report(self) -> pd.DataFrame:
        if len(self.minio_in_list) == 0:
            acceptance_rate = 'NULL'
        else:
            acceptance_rate = len(self.minio_ready_list) / len(self.minio_in_list)

        self.report['acceptance_rate'].append(acceptance_rate)
        self.report['batch_size'].append(len(self.minio_in_list))
        self.report['batch_size_b'].append(sum([int(attr['Size']) if attr['Size'] is not None else 0 for attr in self.minio_in_list]))
        self.report['accepted_batch_size'].append(len(self.minio_ready_list))
        self.report['accepted_batch_size_b'].append(sum([int(attr['Size']) if attr['Size'] is not None else 0 for attr in self.minio_ready_list]))
        self.report['rejected_batch_size'].append(len(self.minio_rejected_list))
        self.report['rejected_batch_size_b'].append(sum([int(attr['Size']) if attr['Size'] is not None else 0 for attr in self.minio_rejected_list]))

        return pd.DataFrame(self.report)

@DataWatcherDriver
def insert_data_watcher_report(self, url, schema, table, method, df) -> None:
    # Insert data into postgres db
    logging.info('Inserting Data Watcher  report')