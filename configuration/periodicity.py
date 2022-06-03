from enum import Enum

class Periodicity(Enum):
    DAILY       = 1
    WEEKLY      = 2
    MONTHLY     = 3

    def preview(self) -> str:
        if self == Periodicity.DAILY:
            return 'daily'
        if self == Periodicity.WEEKLY:
            return 'weekly'
        if self == Periodicity.MONTHLY:
            return 'monthly'
    
            