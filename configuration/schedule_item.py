from configuration.periodicity import Periodicity
from datetime import datetime, timedelta
 
class ScheduleItem:
    dbs: list
    keep_count: int
    repeat: list
    kind: Periodicity

    def __init__(self, conf: dir, kind: Periodicity) -> None:
        self.dbs = conf['dbs']
        self.keep_count = conf['keep_count']
        self.kind = kind
        self.repeat = conf['repeat']

    def get_kind_preview(self) -> str:
        return self.kind.preview()

    def need_to_run(self) -> bool:
        if self.repeat == None:
            return False
        if self.kind == Periodicity.DAILY:
            return self.__check_daily_schedules()
        elif self.kind == Periodicity.WEEKLY:
            return self.__check_weekly_schedules()
        elif self.kind == Periodicity.MONTHLY:
            return self.__check_monthly_schedules()

    def __check_daily_schedules(self):
        today = datetime.now()
        
        weekday = today.weekday()+1
            
        for day in self.repeat:
            if (day == 0 or day == weekday):
                return True

    def __check_weekly_schedules(self):
        today = datetime.now()
        
        week_number = today.isocalendar().week

        if (today.weekday()+1) != 7:
            return False

        for week in self.repeat:
            if (week == 0 or week == week_number):
                return True

    def __check_monthly_schedules(self):
        today = datetime.now()
        
        if today.month == 12:
            year = today.year + 1
            next_month = 1
        else:
            year = today.year
            next_month = today.month + 1 

        finish_day = (datetime(year, next_month, 1) - timedelta(days=1)).day

        if today.day != finish_day:
            return False

        for month in self.repeat:
            if (month == 0 or month == today.month):
                return True


def init_item(kind: str, conf: dir, period: Periodicity) -> ScheduleItem:
        if kind in conf:
            return ScheduleItem(conf[kind], period)
        else:
            return None