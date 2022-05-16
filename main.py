from backup.backup import start
from dotenv import load_dotenv
from loguru import logger
from backup.backup import send_email_error
import os

def main():
    start()

if __name__ == '__main__':
    load_dotenv('env')
    main()

    