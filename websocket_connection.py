import asyncio
import websockets
import socket
import json
import yaml
import requests
import logging
from datetime import datetime

#set up logging
from write_to_log import write_to_log as log
log_path = 'logs/websocket.log'

#check if the file config.yaml exists and if not create it from config.yaml.example
try:
    with open('config.yaml', 'r') as file:
        pass
except FileNotFoundError:
    with open('config.yaml.example', 'r') as file:
        with open('config.yaml', 'w') as file2:
            file2.write(file.read())
            print("Created config.yaml from config.yaml.example")
            print("Please edit config.yaml with your own values or there will be errors.")
            exit()

#read the file config.yaml
with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

API_TOKEN = config['API_TOKEN']
SYSTEM_ID = config['SYSTEM_ID']
WEBHOOK_POSTS = config['WEBHOOK_POSTS']
WEBHOOK_URL = config['WEBHOOK_URL']

def send_discord_message(message):
    if WEBHOOK_POSTS == True:
        webhook_url = WEBHOOK_URL

        payload = {'content': message}
        headers = {'Content-Type': 'application/json'}

        response = requests.post(webhook_url, json=payload, headers=headers)

        if response.status_code == 204:
            log(log_path, f"Discord message sent successfully: {message}")
        else:
            log(log_path, f"Failed to send Discord message. Status code: {response.status_code}")
    elif WEBHOOK_POSTS == False:
        log(log_path, f"Discord message not sent because WEBHOOK_POSTS is set to {WEBHOOK_POSTS} in config.yaml")
    else:
        log(log_path,"WEBHOOK_POSTS is not set to True or False. Please check config.yaml")

def handle_member(member_id, name, operation_type):
    fronting_status = True if operation_type == 'insert' else False
    if operation_type == 'update':
        # Member updated, perform your action here
        log(log_path, f"Member {member_id} updated. Perform action.")
        #send_discord_message(f"{name} has stopped fronting.")
        #update the fronting status of the member in members.yaml
        members_file_path = 'members.yaml'
        with open(members_file_path, 'r') as file:
            members_data = yaml.safe_load(file)
            if members_data is None:
                members_data = {}
        members_data[member_id]['fronting'] = fronting_status
        with open(members_file_path, 'w') as file:
            yaml.dump(members_data, file)
        log(log_path, f"Updated fronting status of {name} to False in members.yaml")
    elif operation_type == 'insert':
        # Member inserted, perform your action here
        log( log_path, f"Member {member_id} inserted. Perform action.")
        #send_discord_message(f"{name} has started fronting.")
        #update the fronting status of the member in members.yaml
        members_file_path = 'members.yaml'
        with open(members_file_path, 'r') as file:
            members_data = yaml.safe_load(file)
            if members_data is None:
                members_data = {}
        members_data[member_id]['fronting'] = fronting_status
        with open(members_file_path, 'w') as file:
            yaml.dump(members_data, file)
        log( log_path, f"Updated fronting status of {name} to True in members.yaml")
    else:
        log( log_path, f"Unknown operation type {operation_type}, no action performed.")

def get_member(MEMBER_ID):
    #https://api.apparyllis.com/v1/member/:systemId/:docId
    url = f"https://api.apparyllis.com/v1/member/{SYSTEM_ID}/{MEMBER_ID}"
    payload={}
    headers = {
    'Authorization': API_TOKEN
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def get_all_members(SYSTEM_ID):
    url = f"https://api.apparyllis.com/v1/members/{SYSTEM_ID}"
    payload={}
    headers = {
    'Authorization': API_TOKEN,
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

async def authenticate(socket, token):
    payload = {'op': 'authenticate', 'token': token}
    await socket.send(json.dumps(payload))
    response = await socket.recv()
    log(log_path, response)

async def keep_alive(socket):
    while True:
        await asyncio.sleep(10)
        await socket.send('ping')

async def handle_messages(socket):
    while True:
        try:
            message = await socket.recv()
            # process message here
            handle_message(message)
        except Exception as e:
            log( log_path, f"Handle Messages Error: {e}")
            # exit the loop if an error occurs
            break

def handle_message(message):
    if message == 'pong':
        log( log_path, "Received pong")
        return
    try:
        if not message:
            log( log_path, "Message is empty")
            return

        parsed_message = json.loads(message)
        target = parsed_message.get('target', '')
        results = parsed_message.get('results', [])

        if results is not None:
            for result in results:
                operation_type = result.get('operationType', '')
                log( log_path, operation_type)
                content = result.get('content', {})
                if content is not None:
                    member_id = content.get('member', '')
                    log( log_path, member_id)

                if target == 'frontHistory' and operation_type in ['update', 'insert']:
                    handle_front_history(member_id, operation_type)

    except json.JSONDecodeError as e:
        log( log_path, f"Error decoding JSON: {e}")
    except Exception as e:
        log( log_path, f"Error handling message: {e}")

def handle_front_history(member_id, operation_type):
    members_file_path = 'members.yaml'

    #check if the file members.yaml exists and if not create it
    try:
        with open(members_file_path, 'r') as file:
            pass
    except FileNotFoundError:
        with open(members_file_path, 'w') as file:
            file.write('')
            log( log_path, "Created members.yaml")

    with open(members_file_path, 'r') as file:
        members_data = yaml.safe_load(file)
        if members_data is None:
            members_data = {}

    if member_id in members_data:
        # Member found, perform your action here
        log( log_path, f"Member {member_id} found. Perform action.")
        yaml_name = members_data[member_id]['name']
        #compare the name in members.yaml to the name in the member
        member = json.loads(get_member(member_id).text)
        #get the name of the member from the content of the member
        name = member.get('content', {}).get('name', {})
        if yaml_name != name:
            log( log_path, f"Name in members.yaml ({yaml_name}) does not match name in member ({name}). Updating name in members.yaml.")
            members_data[member_id]['name'] = name
            with open(members_file_path, 'w') as file:
                yaml.dump(members_data, file)
            log( log_path, f"Updated name of {name} in members.yaml")
        handle_member(member_id, name, operation_type)
    else:
        # Member not found, add a new entry to members.yaml
        member = json.loads(get_member(member_id).text)
        #get the name of the member from the content of the member
        name = member.get('content', {}).get('name', {})
        members_data[member_id] = {'name': name, 'fronting': False}
        with open(members_file_path, 'w') as file:
            yaml.dump(members_data, file)
        log( log_path, f"New member {name} added to members.yaml")
        
        handle_member(member_id, name, operation_type)

logging.basicConfig(level=logging.INFO)

async def main():
    url = 'wss://api.apparyllis.com/v1/socket'
    token = API_TOKEN

    async with websockets.connect(url) as socket:
        # Authenticate
        await authenticate(socket, token)

        # Check if authentication was successful
        response = await socket.recv()
        if "Successfully authenticated" in response:
            log( log_path, "Authentication successful")
            
            # Start a task to handle incoming messages
            message_task = asyncio.create_task(handle_messages(socket))

            # Start a task to send a ping every 10 seconds to keep the connection alive
            keep_alive_task = asyncio.create_task(keep_alive(socket))

            # Wait for both tasks to complete
            await asyncio.gather(message_task, keep_alive_task)
        else:
            log( log_path, "Authentication failed")

def is_connected():
    try:
        # connect to the host -- tells us if the host is actually reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

if __name__ == "__main__":
    asyncio.run(main())