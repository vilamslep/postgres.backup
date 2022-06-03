from configuration.schedule_item import ScheduleItem , init_item
from configuration.periodicity import Periodicity 

class Schedules:
    daily       : ScheduleItem
    weekly      : ScheduleItem
    monthly     : ScheduleItem
    quarterly   : ScheduleItem
    yearly      : ScheduleItem

    def __init__(self, conf:dir) -> None:
        self.daily      = init_item('daily', conf, Periodicity.DAILY)
        self.weekly     = init_item('weekly', conf, Periodicity.WEEKLY)
        self.monthly    = init_item('monthly', conf, Periodicity.MONTHLY)
        
