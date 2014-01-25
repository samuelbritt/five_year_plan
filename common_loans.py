import amortized_loan


class Mortgage(object):
    def __init__(self,
                 purchase_month=None,
                 purchase_amount=None,
                 down_payment_percent=None,
                 apr=None,
                 term_in_years=None):
        super().__init__()
        self.purchase_month = purchase_month
        self.purchase_amount = purchase_amount
        self.down_payment_percent = down_payment_percent
        self.apr = apr
        self.term_in_years = term_in_years

        self._mortgage_loan = None
        self._payments = []

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
                                                               self.purchase_month,
                                                               amortized_loan.CompoundType.MONTHLY)
        return self._mortgage_loan

    @property
    def minimum_payment(self):
        return self.mortgage_loan.minimum_payment

    @property
    def last_payment_month(self):
        return self.mortgage_loan.last_payment_month

    @property
    def remaining_balance(self):
        return self.mortgage_loan.remaining_balance

    def total_interest_paid(self, year=None):
        return self.mortgage_loan.total_interest_paid(year)

    @property
    def payments(self):
        return self._payments

    def make_payment(self, payment_month=None):
        loan_payment = self.mortgage_loan.make_payment(self.minimum_payment, payment_month)
        self.payments.append(loan_payment)
        return loan_payment

    def calculate_amortization_table(self, regular_payment_amount=None):
        while self.mortgage_loan.remaining_balance > 0:
            self.make_payment()
        return self.payments


class StudentLoan(object):
    def __init__(self,
                 start_month=None,
                 start_amount=None,
                 apr=None,
                 term_in_years=10):
        super().__init__()
        self.start_month = start_month
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
                                                              self.start_month,
                                                              amortized_loan.CompoundType.DAILY)
        return self._student_loan

    @property
    def minimum_payment(self):
        return self.student_loan.minimum_payment

    @property
    def last_payment_month(self):
        return self.student_loan.last_payment_month

    @property
    def remaining_balance(self):
        return self.student_loan.remaining_balance

    def total_interest_paid(self, year=None):
        return self.student_loan.total_interest_paid(year)

    @property
    def payments(self):
        return self.student_loan.payments

    def make_payment(self, payment_amount=None, payment_month=None):
        return self.student_loan.make_payment(payment_amount, payment_month)

    def calculate_amortization_table(self, regular_payment_amount=None):
        return self.student_loan.calculate_amortization_table(regular_payment_amount)