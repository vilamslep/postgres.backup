import os
from backup.item import BackupItem
from configuration import config, ScheduleItem, Periodicity
from utils.postgres import databases, Database
from typing import List
import fs, traceback
from loguru import logger

class Task:
    name:str
    kind: Periodicity
    items: List[BackupItem]
    keep_count:int

    def __init__(self, name: str, kind: Periodicity, dbs: list, keep_count: int ) -> None:
        self.name = name
        self.kind = kind
        self.keep_count = keep_count

        dbs_in_server =  databases(dbs)
        db_as_obs = self.__add_which_not_found(dbs, dbs_in_server)
        
        self.items = []
        for db in db_as_obs:
            self.items.append(BackupItem(db))

    def __add_which_not_found(self, dbs: list, dbls: list) -> list:
        for db in dbs:
            rs = list(filter(lambda x: x.name == db, dbls))
            
            if len(rs) == 0:
                dbls.append(Database(db,''))

        return dbls
        
    def execute(self):
        tmpath = fs.temp_dir()
        rpath = fs.get_root_dir(config.backpath(), self.name, self.kind)
        
        logger.info(f'temp directory is {tmpath}')
        logger.info(f'root path is {rpath}')
                
        for item in self.items:
            logger.info(f'start handling \'{item.database.name}\'')

            try:
                item.backup(tmpath, rpath)
            except:
                logger.error(traceback.format_exc())
            else:        
                logger.info(f'finish handling \'{item.database.name}\'')     
        
        logger.info('removing old copies')
        try:
            kind_path = os.path.dirname(rpath)
            fs.clear_old_backup(kind_path, self.keep_count)
        except:
            logger.error(traceback.format_exc())
        else:
            logger.info('success')


def new_task(schedule: ScheduleItem) -> Task|None:
    if schedule == None:
        return None

    if schedule.need_to_run():
        name = schedule.get_kind_preview()
        kind = schedule.kind
        keep_count = schedule.keep_count
        dbs = schedule.dbs
        return Task(name, kind, dbs, keep_count)
    else:
        return None 

def generate_task_by_schedules():
    schedules = config.get_schedules()

    tasks = [
        new_task(schedules.daily),
        new_task(schedules.weekly),
        new_task(schedules.monthly)
        ]

    return list( filter(lambda x: x != None, tasks) )



