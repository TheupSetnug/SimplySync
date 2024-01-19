import discord
from discord.ext import commands
import websocket_connection
import asyncio
import requests
import json
import yaml

#set up logging
from  write_to_log import write_to_log as log
log_path = 'logs/client.log'

#check if the file config.yaml exists and if not create it from config.yaml.example
try:
    with open('config.yaml', 'r') as file:
        pass
except FileNotFoundError:
    with open('config.yaml.example', 'r') as file:
        with open('config.yaml', 'w') as file2:
            file2.write(file.read())
            log(log_path, "Created config.yaml from config.yaml.example")
            log(log_path, "Please edit config.yaml with your own values or there will be errors.")
            exit()

#read the file config.yaml
with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

discord_token = config['DISCORD_TOKEN']
API_TOKEN = config['API_TOKEN']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', description="This is a Helper Bot",intents=intents)

async def startsocket():
    try:
        log(log_path, f"starting websocket connection...")
        await websocket_connection.main()    
    except Exception as e:
        log(log_path, f"Error with websocket: {e}")
        await asyncio.sleep(5)
        log(log_path, f"Restarting websocket connection...")
        await startsocket()
    
def compile_status_message():
    #load members.yaml
    members_file_path = 'members.yaml'
    with open(members_file_path, 'r') as file:
        members_data = yaml.safe_load(file)
    
    #compile a list of members fronting
    fronting_members = []
    non_fronting_members = []
    blacklisted_member_ids = config['BLACKLISTED_MEMBER_IDS']
    for member_id, member_data in members_data.items():
        if member_data['fronting'] == True and member_id not in blacklisted_member_ids:
            fronting_members.append(member_data['name'])
    for member_id, member_data in members_data.items():
        if member_data['fronting'] == False and member_id not in blacklisted_member_ids:
            non_fronting_members.append(member_data['name'])
    
    #compile the status message formatted line by line in a block text for discord, or a message saying no fronters
    if len(fronting_members) > 0:
        message_status_content = "Currently Fronting, Co-Fronting, or Co-consious Members:\n"
        for member in fronting_members:
            message_status_content += f"``🟢 {member}``\n"
    else:
        message_status_content = f"No one is here... *crickets*"
    return message_status_content

async def update_status_message():
    message_status_content = compile_status_message()
    status_channel_id = config['STATUS_CHANNEL_ID']
    status_message_id = config['STATUS_MESSAGE_ID']
    status_channel = bot.get_channel(int(status_channel_id))
    status_message = await status_channel.fetch_message(status_message_id)
    await status_message.edit(content=message_status_content)

async def update_status_message_loop():
    #check for updates every 10 seconds, and skip if there are no updates
    while True:
        await asyncio.sleep(10)
        message_status_content = compile_status_message()
        status_channel_id = config['STATUS_CHANNEL_ID']
        status_message_id = config['STATUS_MESSAGE_ID']
        status_channel = bot.get_channel(int(status_channel_id))
        status_message = await status_channel.fetch_message(status_message_id)
        #check if the status message content is the same as the compiled status message content and trim whitespace
        if status_message.content.strip() != message_status_content.strip():
            await status_message.edit(content=message_status_content)
            log(log_path, f"Status message edited")

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
            log(log_path, f"Updated fronting status of {members_data[member_id]['name']} to True in members.yaml")
        else:
            log(log_path, f"Fronting status of {members_data[member_id]['name']} is already True in members.yaml. Skipping update.")
 
def clear_fronting_statuses():
    members_file_path = 'members.yaml'
    with open(members_file_path, 'r') as file:
        members_data = yaml.safe_load(file)
        if members_data is None:
            members_data = {}
    for member_id, member_data in members_data.items():
        members_data[member_id]['fronting'] = False
    with open(members_file_path, 'w') as file:
        yaml.dump(members_data, file)
    log(log_path, f"Set all fronting statuses to False in members.yaml")

@bot.event
async def on_ready():
    log(log_path, f'We have logged in as {bot.user}')
    #clear all fronting statuses in members.yaml
    clear_fronting_statuses()
    #update the fronting statuses of all current fronters
    update_current_fronters()
    #use the status channel id from config.yaml to set the status channel, if there is one
    status_channel_id = config['STATUS_CHANNEL_ID']
    if status_channel_id is not None:
        status_channel = bot.get_channel(int(status_channel_id))
        log(log_path, f"Status channel set to: {status_channel_id}")
        #set status_message_id from config.yaml, if there is one
        status_message_id = config['STATUS_MESSAGE_ID']
        if status_message_id is not None and status_message_id != "":
            #get the message from the status channel
            status_message = await status_channel.fetch_message(status_message_id)
            log(log_path, f"Status message set to: {status_message_id}")
        else:
            log(log_path, f"No status message ID set in config.yaml")
            #create a new message in the status channel and set status_message_id in config.yaml
            status_message = await status_channel.send("Creating new status message...")
            status_message_id = f"{status_channel.last_message_id}"
            config['STATUS_MESSAGE_ID'] = status_message_id
            with open('config.yaml', 'w') as f:
                yaml.dump(config, f)
            log(log_path, f"Created new status message with ID: {status_message_id}")
        #compile the status message
        status_message_content = compile_status_message()
        #edit the status message
        await status_message.edit(content=status_message_content)
        log(log_path, f"Status message edited to: {status_message_content}")
    else:
        log(log_path, f"No status channel set in config.yaml, please set it manually")

    #start websocket connection and keep running before its done
    asyncio.create_task(startsocket())

    asyncio.create_task(update_status_message_loop())


@bot.command()
async def reload(ctx):
    channel_id_current = ctx.channel.id
    clear_fronting_statuses()
    update_current_fronters()
    #update the status message  
    await update_status_message()
    #send a message to the channel the command was sent in
    await ctx.send(f"Reloaded fronting statuses and current fronters.")
    log(log_path, f"Reloaded fronting statuses and current fronters.")

bot.run(discord_token)