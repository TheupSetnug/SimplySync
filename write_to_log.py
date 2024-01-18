from datetime import datetime
import os

def write_to_log(file, message):
    # get the file name from the file path formatting in capital letters
    file_name = file.split('/')[-1].upper()
    # check if the directory exists and if not create it
    directory = os.path.dirname(file)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created {directory}")
    # check if the file exists and if not create it
    try:
        with open(file, 'a', encoding='utf-8') as file:
            # append a new line to the end of the file with a timestamp and the message
            file.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message.encode('utf-8')}")
    except FileNotFoundError:
        with open(file, 'w', encoding='utf-8') as file:
            file.write('')
            print(f"Created {file}")
    print(f"{file_name} - {message}")
