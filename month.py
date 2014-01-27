from datetime import datetime, date
from dateutil.relativedelta import relativedelta

import enum

DatePart = enum.Enum(('YEAR', 'MONTH', 'DAY'))

class Month(object):
    def __init__(self, year, month):
        super().__init__()
        self._date = date(year, month, 1)

    @classmethod
    def fromdate(cls, date_):
        return cls(date_.year, date_.month)

    def __repr__(self):
        return self.__class__.__name__ + '(' + repr(self._date.year) + ', ' + repr(self._date.month) + ')'
    def __str__(self):
        return self._date.strftime('%Y-%b')

    def __hash__(self):
        return self._date.__hash__()
 
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if type(other) is type(self):
            return self._date > other._date
        return False

    def __lt__(self, other):
        if type(other) is type(self):
            return self._date < other._date
        return False

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    @property
    def year(self):
        return self._date.year

    @property
    def month(self):
        return self._date.month

    def as_datetime(self):
        return datetime.combine(self._date, datetime.min.time())

    def monthadd(self, month_count):
        month_delta = relativedelta(months=month_count)
        return Month.fromdate((self.as_datetime() + month_delta).date())

    def datediff(self, date_part, other):
        diff = relativedelta(other.as_datetime(), self.as_datetime())
        if date_part == DatePart.DAY:
            return (other._date - self._date).days
        elif date_part == DatePart.MONTH:
            return diff.months + (diff.years * 12)
        elif date_part == DatePart.YEAR:
            return diff.years
        else:
            return None