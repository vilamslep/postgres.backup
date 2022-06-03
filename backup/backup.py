import traceback
import backup.task as task
from typing import List
from loguru import logger

class Backup:
    tasks: List[task.Task]

    def __init__(self) -> None:
        self.tasks = task.generate_task_by_schedules()

    def run(self)-> None:
        logger.info('start backuping')
        for t in self.tasks:
            logger.info(f'handling of kind \'{t.name}\'')
            try:
                t.execute()
            except:
                logger.error(traceback.format_exc())