from datetime import datetime

def write_to_log(file, message):
    #check if the file exists and if not create it
    try:
        with open(file, 'a') as file:
            #append a new line to the end of the file with a timestamp and the message
            file.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}")
    except FileNotFoundError:
        with open(file, 'w') as file:
            file.write('')
            print(f"Created {file}")
    print(f"Logged - {message}")