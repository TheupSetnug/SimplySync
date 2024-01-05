import asyncio
import websockets
import json
import yaml
import requests

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
            print(f"Discord message sent successfully: {message}")
        else:
            print(f"Failed to send Discord message. Status code: {response.status_code}")
    elif WEBHOOK_POSTS == False:
        print(f"Discord message not sent because WEBHOOK_POSTS is set to {WEBHOOK_POSTS} in config.yaml")
    else:
        print("WEBHOOK_POSTS is not set to True or False. Please check config.yaml")

def handle_member(member_id, name, operation_type):
    fronting_status = True if operation_type == 'insert' else False
    if operation_type == 'update':
        # Member updated, perform your action here
        print(f"Member {member_id} updated. Perform action.")
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
        print(f"Updated fronting status of {name} to False in members.yaml")
    elif operation_type == 'insert':
        # Member inserted, perform your action here
        print(f"Member {member_id} inserted. Perform action.")
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
        print(f"Updated fronting status of {name} to True in members.yaml")
    else:
        print(f"Unknown operation type {operation_type}, no action performed.")

def get_member(MEMBER_ID):
    #https://api.apparyllis.com/v1/member/:systemId/:docId
    url = f"https://api.apparyllis.com/v1/member/{SYSTEM_ID}/{MEMBER_ID}"
    payload={}
    headers = {
    'Authorization': API_TOKEN
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

async def authenticate(socket, token):
    payload = {'op': 'authenticate', 'token': token}
    await socket.send(json.dumps(payload))
    response = await socket.recv()
    print(response)

async def keep_alive(socket):
    while True:
        await asyncio.sleep(10)
        await socket.send('ping')

async def handle_messages(socket):
    while True:
        message = await socket.recv()
        handle_message(message)

def handle_message(message):
    if message == 'pong':
        print("Received pong")
        return
    try:
        if not message:
            print("Message is empty")
            return

        parsed_message = json.loads(message)
        target = parsed_message.get('target', '')
        results = parsed_message.get('results', [])

        if results is not None:
            for result in results:
                operation_type = result.get('operationType', '')
                print(operation_type)
                content = result.get('content', {})
                if content is not None:
                    member_id = content.get('member', '')
                    print(member_id)

                if target == 'frontHistory' and operation_type in ['update', 'insert']:
                    handle_front_history(member_id, operation_type)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error handling message: {e}")

def handle_front_history(member_id, operation_type):
    members_file_path = 'members.yaml'

    #check if the file members.yaml exists and if not create it
    try:
        with open(members_file_path, 'r') as file:
            pass
    except FileNotFoundError:
        with open(members_file_path, 'w') as file:
            file.write('')
            print("Created members.yaml")

    with open(members_file_path, 'r') as file:
        members_data = yaml.safe_load(file)
        if members_data is None:
            members_data = {}

    if member_id in members_data:
        # Member found, perform your action here
        print(f"Member {member_id} found. Perform action.")
        name = members_data[member_id]['name']
        handle_member(member_id, name, operation_type)
    else:
        # Member not found, add a new entry to members.yaml
        member = json.loads(get_member(member_id).text)
        #get the name of the member from the content of the member
        name = member.get('content', {}).get('name', {})
        members_data[member_id] = {'name': name, 'fronting': False}
        with open(members_file_path, 'w') as file:
            yaml.dump(members_data, file)
        print(f"New member {name} added to members.yaml")
        
        handle_member(member_id, name, operation_type)

async def main():
    url = 'wss://api.apparyllis.com/v1/socket'
    token = API_TOKEN

    async with websockets.connect(url) as socket:
        # Authenticate
        await authenticate(socket, token)

        # Check if authentication was successful
        response = await socket.recv()
        if "Successfully authenticated" in response:
            print("Authentication successful")
            
            # Start a task to handle incoming messages
            message_task = asyncio.create_task(handle_messages(socket))

            # Start a task to send a ping every 10 seconds to keep the connection alive
            keep_alive_task = asyncio.create_task(keep_alive(socket))

            # Wait for both tasks to complete
            await asyncio.gather(message_task, keep_alive_task)
        else:
            print("Authentication failed")

if __name__ == "__main__":
    asyncio.run(main())