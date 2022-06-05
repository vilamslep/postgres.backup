from datetime import datetime
from backup.backup import Backup
from backup import Backup
from configuration import load_setting
from loguru import logger

def main():

   Backup().run()
   
if __name__ == '__main__':
   now = datetime.now().strftime("%d-%m-%Y")
   logger.add(f'log\\{now}.log')
   logger.info('start script')
   try:
      load_setting('setting.yaml')
      main()
   except Exception as ex:
      logger.error(ex)
      exit(1)
         
   logger.info('finish script')
    