import sqlalchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import logging


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