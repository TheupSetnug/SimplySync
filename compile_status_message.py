import yaml

def compile_status_message():
    #load members.yaml
    members_file_path = 'members.yaml'
    with open(members_file_path, 'r') as file:
        members_data = yaml.safe_load(file)
    
    #compile a list of members fronting
    fronting_members = []
    for member_id, member_data in members_data.items():
        if member_data['fronting'] == True:
            fronting_members.append(member_data['name'])
    
    #compile the status message formatted line by line in a block text for discord, or a message saying no fronters
    if len(fronting_members) > 0:
        message_status_content = "Currently Available Members:\n"
        for member in fronting_members:
            message_status_content += f"``🟢 {member}``\n"
    else:
        message_status_content = f"No one is fronting."
    return message_status_content