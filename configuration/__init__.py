from configuration.config import Config
from configuration.schedule_item import ScheduleItem
from configuration.periodicity import Periodicity

config = Config()

def load_setting(fpath:str):
    config.load_setting(fpath)