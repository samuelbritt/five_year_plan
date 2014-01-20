import amortized_loan

class MortgagePayment(object):
    def __init__(self, loan_payment, pmi_payment_amount):
        super().__init__()

        self.loan_payment = loan_payment
        self.date = loan_payment.date
        self.loan_payment_amount = loan_payment.payment_amount
        self.principle_amount = loan_payment.principle_amount
        self.interest_amount = loan_payment.interest_amount
        self.new_balance = loan_payment.new_balance
        self.pmi_amount = pmi_payment_amount
        self.total_payment_amount = loan_payment.payment_amount + pmi_payment_amount

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Payment {date} {amt:>8.2f} ({princ:>8.2f} P, {int:>8.2f} I, {pmi:>8.2f} PMI {rem:>10.2f} R)".format(
            date=self.date.isoformat(),
            amt=self.total_payment_amount,
            princ=self.principle_amount,
            int=self.interest_amount,
            pmi=self.pmi_amount,
            rem=self.new_balance
        )

class PMI(object):
    """docstring for PMI"""
    def __init__(self, mortgage, rate=0.015):
        super().__init__()
        self.mortgage = mortgage
        self.rate = rate

    @property
    def standard_monthly_pmi_payment(self):
        return self.rate * self.mortgage.financed_amount / 12
    
    @property
    def pmi_payment(self):
        if self.mortgage.current_percent_equity < 0.20:
            return self.standard_monthly_pmi_payment
        else:
            return 0

class Mortgage(object):
    def __init__(self,
                 purchase_date=None,
                 purchase_amount=None,
                 down_payment_percent=None,
                 apr=None,
                 term_in_years=None,
                 pmi_rate=None):
        super().__init__()
        self.purchase_date = purchase_date
        self.purchase_amount = purchase_amount
        self.down_payment_percent = down_payment_percent
        self.apr = apr
        self.term_in_years = term_in_years
        self.pmi_rate = pmi_rate

        self._mortgage_loan = None
        self._pmi = None
        self._payments = []

    @property
    def current_home_value(self):
        return self.purchase_amount

    @property
    def current_equity(self):
        return self.current_home_value - self.mortgage_loan.remaining_balance

    @property
    def current_percent_equity(self):
        return self.current_equity / self.current_home_value    

    @property
    def down_payment_amount(self):
        return self.purchase_amount * self.down_payment_percent

    @property
    def financed_amount(self):
        return self.purchase_amount * (1 - self.down_payment_percent)

    @property
    def mortgage_loan(self):
        if self._mortgage_loan is None:
            self._mortgage_loan = amortized_loan.AmortizedLoan(self.financed_amount,
                                                               self.term_in_years,
                                                               self.apr,
                                                               self.purchase_date,
                                                               amortized_loan.CompoundType.MONTHLY)
        return self._mortgage_loan

    @property
    def minimum_payment(self):
        return self.mortgage_loan.minimum_payment

    @property
    def last_payment_date(self):
        return self.mortgage_loan.last_payment_date

    @property
    def remaining_balance(self):
        return self.mortgage_loan.remaining_balance

    def total_interest_paid(self, year=None):
        return self.mortgage_loan.total_interest_paid(year)

    @property
    def total_pmi_paid(self):
        if not self.payments:
            return 0
        return sum(p.pmi_amount for p in self.payments)

    @property
    def pmi(self):
        if self._pmi is None:
            self._pmi = PMI(self, self.pmi_rate)
        return self._pmi
    
    @property
    def pmi_payment(self):
        return self.pmi.pmi_payment

    @property
    def payments(self):
        return self._payments

    def make_payment(self, payment_date=None):
        pmi_payment = self.pmi.pmi_payment
        loan_payment = self.mortgage_loan.make_payment(self.minimum_payment, payment_date)
        mortgage_payment = MortgagePayment(loan_payment, pmi_payment)
        self.payments.append(mortgage_payment)

    def calculate_amortization_table(self, regular_payment_amount=None):
        while self.mortgage_loan.remaining_balance > 0:
            self.make_payment()
        return self.payments


class StudentLoan(object):
    def __init__(self,
                 start_date=None,
                 start_amount=None,
                 apr=None,
                 term_in_years=10):
        super().__init__()
        self.start_date = start_date
        self.start_amount = start_amount
        self.apr = apr
        self.term_in_years = term_in_years

        self._student_loan = None

    @property
    def student_loan(self):
        if self._student_loan is None:
            self._student_loan = amortized_loan.AmortizedLoan(self.start_amount,
                                                              self.term_in_years,
                                                              self.apr,
                                                              self.start_date,
                                                              amortized_loan.CompoundType.DAILY)
        return self._student_loan

    @property
    def minimum_payment(self):
        return self.student_loan.minimum_payment

    @property
    def last_payment_date(self):
        return self.student_loan.last_payment_date

    @property
    def remaining_balance(self):
        return self.student_loan.remaining_balance

    def total_interest_paid(self, year=None):
        return self.student_loan.total_interest_paid(year)

    @property
    def payments(self):
        return self.student_loan.payments

    def make_payment(self, payment_amount=None, payment_date=None):
        return self.student_loan.make_payment(payment_amount, payment_date)

    def calculate_amortization_table(self, regular_payment_amount=None):
        return self.student_loan.calculate_amortization_table(regular_payment_amount)