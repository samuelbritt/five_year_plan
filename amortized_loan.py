
import numpy as np
import datetime
import calendar

import enum

CompoundType = enum.Enum(["MONTHLY", "DAILY"])

class Payment(object):
    def __init__(self, date, payment_amount, interest_amount, principle_amount):
        super().__init__()
        self.date = date
        self.payment_amount = payment_amount
        self.interest_amount = interest_amount
        self.principle_amount = principle_amount

    def __str__(self):
        return "Payment {year}-{month}-{day} {amt} ({int}i, {princ}p)".format(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            amt=self.payment_amount,
            int=self.interest_amount,
            princ=self.principle_amount
        )
    def __repr__(self):
        return "Payment {year}-{month}-{day} {amt:6.2f} ({int:6.2f}i, {princ:6.2f}p)".format(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            amt=self.payment_amount,
            int=self.interest_amount,
            princ=self.principle_amount
        )

class Compunder(object):
    def __init__(self, amortized_loan=None):
        super().__init__()
        self.loan = amortized_loan
    def min_payment(self):
        pass
    def interest_amount(self, payment_date):
        pass

class MonthlyCompounder(Compunder):
    def __init__(self):
        super().__init__()

    @property
    def monthly_rate(self):
        return self.loan.apr / 12

    @property
    def term_in_months(self):
        return self.loan.term_in_years * 12

    
    def min_payment(self):
        return -np.pmt(self.monthly_rate, self.term_in_months, self.loan.purchase_amount)
    def interest_amount(self, payment_date):
        return self.monthly_rate * self.loan.remaining_balance
        

class DailyCompounder(Compunder):
    def __init__(self):
        super().__init__()
        self.days_in_month = 365.25 / 12
    @property
    def daily_rate(self):
        return self.loan.apr / 365.25
    @property
    def term_in_days(self):
        return self.loan.term_in_years * 365.25

    def min_payment(self):
        return -self.days_in_month * np.pmt(self.daily_rate, self.days, self.loan.purchase_amount)
    def interest_amount(self, payment_date):
        days_since_last_payment = (payment_date - self.loan.last_payment_date).days
        return (self.daily_rate * days_since_last_payment) * self.loan.remaining_balance



class CompunderFactory(object):
    def __init__(self):
        super().__init__()
    def get_compounder(self, compound_type):
        if compound_type == CompoundType.MONTHLY:
            return MonthlyCompounder()
        elif compound_type == CompoundType.DAILY:
            return DailyCompounder()

class AmortizedLoan(object):
    """docstring for AmortizedLoan"""
    def __init__(self, purchase_amount, term_in_years, apr, start_date=datetime.date(2014, 1, 1), compound_type=CompoundType.MONTHLY):
        super().__init__()
        self.purchase_amount = purchase_amount
        self.term_in_years = term_in_years
        self.apr = apr

        self.compounder = CompunderFactory().get_compounder(compound_type)
        self.compounder.loan = self

        self.min_payment = self.compounder.min_payment()

        self.remaining_balance = self.purchase_amount
        self.last_payment_date = start_date
        self.payments = []

    def __str__(self):
        return "AmortizedLoan: {amt} for {term} years at {apr}%".format(amt=self.purchase_amount,
                                                                        term=self.term_in_years,
                                                                        apr=self.apr)

    def add_month(self, date):
        days_in_month = calendar.monthrange(date.year, date.month)[1]
        return date + datetime.timedelta(days_in_month)

    def make_payment(self, payment_amount=None, payment_date=None):
        if self.remaining_balance == 0:
            return

        payment_amount = payment_amount if payment_amount is not None else self.min_payment
        payment_date = payment_date if payment_date is not None else self.add_month(self.last_payment_date)
        interest_amount = self.compounder.interest_amount(payment_date)
        principle_amount = max(payment_amount - interest_amount, 0)

        payment = Payment(payment_date, payment_amount, interest_amount, principle_amount)
        self.remaining_balance = max(self.remaining_balance - principle_amount, 0)
        self.payments.append((payment, self.remaining_balance))
        self.last_payment_date = payment_date

    def calculate_amortization_table(self):
        while self.remaining_balance > 0:
            self.make_payment()
        return self.payments