import requests
import yaml
import json
from pprint import pprint

#get the system id from config.yaml
config_file_path = 'config.yaml'
with open(config_file_path, 'r') as file:
    config = yaml.safe_load(file)
    if config is None:
        config = {}
SYSTEM_ID = config['SYSTEM_ID']
API_TOKEN = config['API_TOKEN']

def get_all_members(SYSTEM_ID):
    url = f"https://api.apparyllis.com/v1/members/{SYSTEM_ID}"
    payload={}
    headers = {
    'Authorization': API_TOKEN,
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def get_member(MEMBER_ID):
    #https://api.apparyllis.com/v1/member/:systemId/:docId
    url = f"https://api.apparyllis.com/v1/member/{SYSTEM_ID}/{MEMBER_ID}"
    payload={}
    headers = {
    'Authorization': API_TOKEN
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def update_current_fronters():
    url = "https://api.apparyllis.com/v1/fronters/"
    payload={}
    headers = {
    'Authorization': API_TOKEN
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(response.text)

    member_ids = [item['content']['member'] for item in response]
    for member_id in member_ids:
        #update the fronting status of the member in members.yaml if it is not already true
        members_file_path = 'members.yaml'
        with open(members_file_path, 'r') as file:
            members_data = yaml.safe_load(file)
            if members_data is None:
                members_data = {}
        if members_data[member_id]['fronting'] == False:
            members_data[member_id]['fronting'] = True
            with open(members_file_path, 'w') as file:
                yaml.dump(members_data, file)
            print(f"Updated fronting status of {members_data[member_id]['name']} to True in members.yaml")
        else:
            print(f"Fronting status of {members_data[member_id]['name']} is already True in members.yaml. Skipping update.")
    
update_current_fronters()