import requests
from pprint import pprint as pp
import yaml

#read the file config.yaml
with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

API_TOKEN = config['API_TOKEN']
SYSTEM_ID = config['SYSTEM_ID']

MEMBER_ID = '6513400c7624c94f0950ead4'


def get_member(MEMBER_ID):
    #https://api.apparyllis.com/v1/member/:systemId/:docId
    url = f"https://api.apparyllis.com/v1/member/{SYSTEM_ID}/{MEMBER_ID}"
    payload={}
    headers = {
    'Authorization': API_TOKEN
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def get_members(SYSTEM_ID):
    #https://api.apparyllis.com/v1/members/:systemId
    url = f"https://api.apparyllis.com/v1/members/{SYSTEM_ID}"
    payload={}
    headers = {
    'Authorization': API_TOKEN
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def get_front_history(MEMBER_ID):
    #https://api.apparyllis.com/v1/frontHistory/member/:memberId
    url = f"https://api.apparyllis.com/v1/frontHistory/member/{MEMBER_ID}"
    payload={}
    headers = {
    'Authorization': API_TOKEN,
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response


pp(get_front_history(MEMBER_ID).json())