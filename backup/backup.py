from datetime import datetime
import traceback, jinja2
import backup.task as task
from typing import List
from loguru import logger
from configuration import config
from notification import notify
import os


class Backup:
    data: datetime
    tasks: List[task.Task]

    def __init__(self) -> None:
        self.data = datetime.now()
        self.tasks = task.generate_task_by_schedules()

    def run(self)-> None:
        logger.info('start backuping')
        for t in self.tasks:
            logger.info(f'handling of kind \'{t.name}\'')
            try:
                t.execute()
            except:
                logger.error(traceback.format_exc())
        
        logger.info('sending report') 
        self.__send_email_report()  

    def __send_email_report(self):
        content = dict()
        content['error_count'] = 0
        content['warning_count'] = 0
        content['success_count'] = 0
        content['tasks'] = [] 
        for task in self.tasks:
            itask = dict()
            itask['name'] = task.name.title()
            itask['items'] = list()
            for i in task.items:
                ii = dict('')
                if i.status == 'error':
                    content['error_count'] +=1
                elif i.status == 'warining':
                    content['warning_count'] +=1
                else:
                    content['success_count'] +=1
                
                ii['name'] = i.database.name
                ii['oid'] = i.database.oid
                ii['status'] = i.status.title()
                ii['start_time'] = i.start_time.strftime('%H:%M:%S')
                ii['end_time'] = i.end_time.strftime('%H:%M:%S')
                if i.database.oid != '':
                    ii['size_database'] = str((round(i.size_database / 1024 / 1024 / 1024, 2))) + ' GB'
                    ii['size_backup'] = str((round(i.size_backup / 1024 / 1024 / 1024, 2))) + ' GB'
                else:
                    ii['size_database'] = ''
                    ii['size_backup'] = ''

                ii['backup'] = i.backup_path
                ii['details'] = i.details

                itask['items'].append(ii)

            content['tasks'].append(itask)

        content['error'] = content['error_count'] > 0
        content['warning'] = content['warning_count'] > 0
        content['success'] = content['success_count'] > 0

        days_of_week = ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
        month = ('January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December')

        content['day_of_week'] = days_of_week[(self.data.weekday())]
        content['day_of_month'] = self.data.day
        content['month'] = month[self.data.month-1] 
        content['year'] = self.data.year
        
        loader  = jinja2.FileSystemLoader('assets')
        env     = jinja2.Environment(loader=loader, trim_blocks=True)
        tpl     = env.get_template('main.html')
        result  = tpl.render(content)
        
        notify.EmailLetter(
            notify.EmailUser(config.email.user, config.email.password, config.email.smtp_host, config.email.smtp_port),
            result, config.email.letter['subject'], 'VS.Backup', config.email.recivers  
        ).send()