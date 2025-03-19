import os


port = os.getenv('SFTP_PORT')
username = os.getenv('SFTP_USERNAME')
password = os.getenv('SFTP_PASSWORD')
private_key = os.getenv('SFTP_PRIVATE_KEY')
passphrase = os.getenv('SFTP_PASSPHRASE') or password
start_date = os.environ.get('START_DATE')
end_date = os.environ.get('END_DATE')

epex_country = os.getenv('EPEX_COUNTRY')
epex_country_code = os.getenv('EPEX_COUNTRY_CODE')
epex_year = os.getenv('EPEX_YEAR')