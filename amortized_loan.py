
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar

import enum

CompoundType = enum.Enum(["MONTHLY", "DAILY"])

class Payment(object):
    def __init__(self, loan, payment_date, payment_amount):
        super().__init__()
        self.date = payment_date
        self.payment_amount = payment_amount
        self.previous_balance = loan.remaining_balance

        self.interest_amount = loan.compounder.interest_amount(self.date)
        self.principle_amount = max(self.payment_amount - self.interest_amount, 0)
        self.new_balance = max(self.previous_balance - self.principle_amount, 0)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Payment {date} {amt:>8.2f} ({princ:>8.2f} P, {int:>8.2f} I, {rem:>10.2f} R)".format(
            date=self.date.isoformat(),
            amt=self.payment_amount,
            princ=self.principle_amount,
            int=self.interest_amount,
            rem=self.new_balance
        )

class Compunder(object):
    def __init__(self, amortized_loan):
        super().__init__()
        self.loan = amortized_loan
    def minimum_payment(self):
        pass
    def interest_amount(self, payment_date):
        pass

class MonthlyCompounder(Compunder):
    def __init__(self, amortized_loan):
        super().__init__(amortized_loan)

    @property
    def monthly_rate(self):
        return self.loan.apr / 12

    @property
    def term_in_months(self):
        return self.loan.term_in_years * 12

    
    def minimum_payment(self):
        return -np.pmt(self.monthly_rate, self.term_in_months, self.loan.purchase_amount)
    def interest_amount(self, payment_date):
        return self.monthly_rate * self.loan.remaining_balance
        
class DailyCompounder(Compunder):
    def __init__(self, amortized_loan):
        super().__init__(amortized_loan)
        self.days_in_month = 365.25 / 12
    @property
    def daily_rate(self):
        return self.loan.apr / 365.25
    @property
    def term_in_days(self):
        return self.loan.term_in_years * 365.25

    def minimum_payment(self):
        return -self.days_in_month * np.pmt(self.daily_rate, self.days, self.loan.purchase_amount)
    def interest_amount(self, payment_date):
        days_since_last_payment = (payment_date - self.loan.last_payment_date).days
        return (self.daily_rate * days_since_last_payment) * self.loan.remaining_balance

class CompunderFactory(object):
    def __init__(self, amortized_loan):
        super().__init__()
        self.loan = amortized_loan
        self.compound_type = amortized_loan.compound_type
    def get_compounder(self):
        if self.compound_type == CompoundType.MONTHLY:
            return MonthlyCompounder(self.loan)
        elif self.compound_type == CompoundType.DAILY:
            return DailyCompounder(self.loan)

class AmortizedLoan(object):
    """docstring for AmortizedLoan"""
    def __init__(self, purchase_amount, term_in_years, apr, start_date, compound_type):
        super().__init__()
        self.purchase_amount = purchase_amount
        self.term_in_years = term_in_years
        self.apr = apr
        self.compound_type = compound_type

        self.compounder = CompunderFactory(self).get_compounder()

        self.minimum_payment = self.compounder.minimum_payment()

        self.remaining_balance = self.purchase_amount
        self.last_payment_date = start_date
        self.payments = []

    def __str__(self):
        return "AmortizedLoan: {amt} for {term} years at {apr}%".format(amt=self.purchase_amount,
                                                                        term=self.term_in_years,
                                                                        apr=self.apr)

    @property
    def total_interest_paid(self):
        if not self.payments:
            return 0
        return sum((p.interest_amount for p in self.payments))

    def _add_month(self, date):
        date = datetime.combine(date, datetime.min.time())
        one_month = relativedelta(months=1)
        return (date + one_month).date()

    def make_payment(self, payment_amount=None, payment_date=None):
        if self.remaining_balance == 0:
            return

        payment_amount = payment_amount if payment_amount is not None else self.minimum_payment
        payment_date = payment_date if payment_date is not None else self._add_month(self.last_payment_date)

        payment = Payment(self, payment_date, payment_amount)
        self.payments.append(payment)
        self.last_payment_date = payment_date
        self.remaining_balance = payment.new_balance
        return payment

    def calculate_amortization_table(self, regular_payment_amount=None):
        while self.remaining_balance > 0:
            self.make_payment(regular_payment_amount)
        return self.payments