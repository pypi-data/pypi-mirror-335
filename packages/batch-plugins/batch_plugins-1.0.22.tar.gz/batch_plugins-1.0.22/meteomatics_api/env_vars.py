import os

meteomatics_username = os.getenv('METEOMATICS_USERNAME') or os.getenv('API_USERNAME')
meteomatics_secret = os.getenv('METEOMATICS_SECRET') or os.getenv('API_KEY')
meteomatics_conf_path = os.getenv('METEOMATICS_CONF_PATH')
start_date = os.getenv('START_DATE')
end_date = os.getenv('END_DATE')
meteomatics_interval = os.environ.get('METEOMATICS_INTERVAL', 30) # e.g. 30
meteomatics_quantiles = os.environ.get('METEOMATICS_QUANTILES', None) # e.g. None, 'quantile0.25,quantile0.5,quantile0.75'
meteomatics_model = os.environ.get('METEOMATICS_MODEL', None) # e.g. None, ecmwf-vareps