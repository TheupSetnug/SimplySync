import requests
import yaml
from pprint import pprint

#get the system id from config.yaml
config_file_path = 'config.yaml'
with open(config_file_path, 'r') as file:
    config = yaml.safe_load(file)
    if config is None:
        config = {}
SYSTEM_ID = config['SYSTEM_ID']
API_TOKEN = config['API_TOKEN']



