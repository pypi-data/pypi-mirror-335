import requests
import logging
from urllib.parse import urljoin
from core.core_env_vars import *

class DataCatalogDriver:
    """
    Class to interact with the Data Catalog API to retrieve ClickHouse table schema.
    """
    def __init__(self, object_id: str):
        """ Initialize the DataCatalogAPI """
        self.catalog_endpoint = urljoin(f"{datacatalog_endpoint}/", f"objects/doc/{object_id}")
        self.headers = {'X-API-KEY': datacatalog_api_key}
        self.object_id = object_id

    def fetch_catalog(self):
        """ Fetch  the Data Catalog API. 
        :return: Json with the API response
        """
        try:
            logging.info(f"Fetching ClickHouse schema for table {self.object_id} from Data Catalog API")
            # Simulated API response for demonstration purposes
            response = requests.get(url=self.catalog_endpoint, headers=self.headers)
            if response.status_code == 200:
                try:
                    data = response.json()
                    logging.info("Successfully fetched schema from Data Catalog API")
                    return data
                except ValueError as e:
                    logging.error(f"Failed to parse JSON: {e}")
                    raise
            else:
                logging.error(f"Datacatalog Request failed with Status Code: {response.status_code}")
                raise Exception('Datacatalog failure')
        except Exception as e:
            logging.error(f"Error fetching schema from Data Catalog API: {str(e)}")
            raise

    def get_table_schema(self):
        """
        Fetch the schema for the Data Catalog response.
        :return: Dictionary mapping column names to ClickHouse data types.
        """
        try:
            catalog = self.fetch_catalog()
            schema_columns = catalog['storage']['columns']
            schema = {column: details['type'] for column, details in schema_columns.items()}
            return schema
        except ValueError as e:
            logging.error(f"Failed to parse JSON: {e}")
            raise

    def get_catalog(self):
        """
        Fetch the catalog for the Data Catalog response.
        :return: Str: Bronze/Silver or Gold.
        """
        try:
            catalog = self.fetch_catalog()
            return catalog['catalog']
        except ValueError as e:
            logging.error(f"Failed to parse JSON: {e}")
            raise
