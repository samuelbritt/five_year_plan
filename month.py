from datetime import datetime, date
from dateutil.relativedelta import relativedelta

import enum

DatePart = enum.Enum(('YEAR', 'MONTH', 'DAY'))

class Month(object):
    def __init__(self, date_):
        super().__init__()
        self._date = date(date_.year, date_.month, 1)

    def __repr__(self):
        return self.__class__.__name__ + '(' + repr(self._date) + ')'
    def __str__(self):
        return self._date.strftime('%Y-%b')
 
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def year(self):
        return self._date.year

    @property
    def month(self):
        return self._date.month

    def as_datetime(self):
        return datetime.combine(self._date, datetime.min.time())

    def add_months(self, month_count):
        month_delta = relativedelta(months=month_count)
        return Month((self.as_datetime() + month_delta).date())

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