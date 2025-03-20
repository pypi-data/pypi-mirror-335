import os


log_level = os.getenv('LOG_LEVEL', 'INFO')

datacatalog_endpoint = os.getenv('DATACATALOG_API_V2_URL')
datacatalog_api_key = os.getenv('DATACATALOG_API_V2_SECRET')
datacatalog_api_endpoint = os.getenv('DATACATALOG_API_ENDPOINT')

minio_endpoint = os.getenv('MINIO_ENDPOINT')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

datawatcher_db_url = os.getenv('DATAWATCHER_DB_URL')
datawatcher_db_table = os.getenv('DATAWATCHER_DB_TABLE')
datawatcher_db_schema = os.getenv('DATAWATCHER_DB_SCHEMA')

local_download_path = os.getenv('LOCAL_DOWNLOAD_PATH')

env_end_date = os.getenv('END_DATE')
env_start_date = os.getenv('START_DATE')