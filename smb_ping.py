#Simple SMB connect and disconnect(ping-eske) utility that can check SMB availability.
#Tuning required for SMB server version - "connection.connect(Dialects.SMB_3_1_1"
#Test platform was Synology with minimal set to Version 1 through Version 3
#No warranty expressed, coded with chatGPT

#Required library - smbprotocol (https://pypi.org/project/smbprotocol/)
#Usage: py .\smb_ping.py
#Enter the IP address of the SMB server:
#Enter the username (leave blank if none):
#Enter the password (leave blank if none):
#Enter delay between retries (seconds):
#Invalid input for delay. Setting default to 30 seconds.
#Example output: Success: 0, Failures: 5, Last failure: 2024-04-16 18:45:14


import sys
import uuid
import time
import logging
from datetime import datetime
from smbprotocol.connection import Connection, Dialects
from smbprotocol.session import Session
from smbprotocol.tree import TreeConnect

# Setup logging to file with INFO level. Console messages will be handled separately.
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler("debug.log")])

def check_smb_share(host, username=None, password=None):
    try:
        # Establish connection using SMB 3.1.1
        connection = Connection(uuid.uuid4(), host, 445)
        connection.connect(Dialects.SMB_3_1_1)
        
        # Start session
        session = Session(connection, username, password)
        session.connect()
        
        # Connect to the IPC$ share
        share_path = "\\\\{}\\IPC$".format(host)
        tree = TreeConnect(session, share_path)
        tree.connect()
        
        # Success message for logging
        logging.info("Successfully connected to SMB server.")
        return True
    except Exception as e:
        # Detailed error logging
        logging.error("Error connecting to SMB server: " + str(e))
        return False
    finally:
        connection.disconnect(True)

if __name__ == "__main__":
    host = input("Enter the IP address of the SMB server: ")
    username = input("Enter the username (leave blank if none): ") or None
    password = input("Enter the password (leave blank if none): ") or None
    try:
        delay = int(input("Enter delay between retries (seconds): "))
    except ValueError:
        print("Invalid input for delay. Setting default to 30 seconds.")
        delay = 30

    success_count = 0
    failure_count = 0
    last_failure_time = "N/A"

    while True:
        success = check_smb_share(host, username, password)
        if success:
            success_count += 1
        else:
            failure_count += 1
            last_failure_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Prepare the message
        message = f"\rSuccess: {success_count}, Failures: {failure_count}, Last failure: {last_failure_time}"
        message = message.ljust(80)  # Ensure the message is long enough to overwrite previous output
        print(message, end='', flush=True)

        if failure_count >= 5:
            # Log the exit due to consecutive errors
            logging.error("Exiting after 5 consecutive errors.")
            break

        time.sleep(delay)
