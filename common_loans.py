import amortized_loan

class Mortgage(object):
    def __init__(self):
        super().__init__()
        
        self.purchase_date = None
        self.purchase_amount = None
        self.down_payment_percent = None
        self.apr = None
        self.term_in_years = None

        self._mortgage_loan = None

    @property
    def down_payment_amount(self):
        return self.purchase_amount * self.down_payment_percent

    @property
    def financed_amount(self):
        return self.purchase_amount * (1 - self.down_payment_percent)

    @property
    def mortgage_loan(self):
        if self._mortgage_loan is None
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
    def total_interest_paid(self):
        return self.mortgage_loan.total_interest_paid

    @property
    def payments(self):
        return self.mortgage_loan.payments

    def make_payment(self, payment_amount=None, payment_date=None):
        return self.mortgage_loan.make_payment(self, payment_amount, payment_date)


    def calculate_amortization_table(self, regular_payment_amount=None):
        return self.mortgage_loan.calculate_amortization_table(regular_payment_amount)