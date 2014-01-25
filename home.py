import common_loans

class HomePayment(object):
    def __init__(self, mortgage_payment, pmi_payment_amount):
        super().__init__()

        self.mortgage_payment = mortgage_payment
        self.month = mortgage_payment.month
        self.mortgage_payment_amount = mortgage_payment.payment_amount
        self.principle_amount = mortgage_payment.principle_amount
        self.interest_amount = mortgage_payment.interest_amount
        self.new_balance = mortgage_payment.new_balance
        self.pmi_amount = pmi_payment_amount
        self.total_payment_amount = mortgage_payment.payment_amount + pmi_payment_amount

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Payment {month} {amt:>8.2f} ({princ:>8.2f} P, {int:>8.2f} I, {pmi:>8.2f} PMI {rem:>10.2f} R)".format(
            month=self.month,
            amt=self.total_payment_amount,
            princ=self.principle_amount,
            int=self.interest_amount,
            pmi=self.pmi_amount,
            rem=self.new_balance
        )

class PMI(object):
    """docstring for PMI"""
    def __init__(self, home, rate=None):
        super().__init__()
        self.home = home
        self.rate = rate or 0.015

    @property
    def standard_monthly_pmi_payment(self):
        return self.rate * self.home.financed_amount / 12
    
    @property
    def pmi_payment(self):
        if self.home.current_percent_equity < 0.20:
            return self.standard_monthly_pmi_payment
        else:
            return 0

class Home(object):
    def __init__(self,
                 purchase_month=None,
                 purchase_amount=None,
                 down_payment_percent=None,
                 apr=None,
                 term_in_years=None,
                 pmi_rate=None):
        super().__init__()
        self.purchase_month = purchase_month
        self.purchase_amount = purchase_amount
        self.down_payment_percent = down_payment_percent
        self.apr = apr
        self.term_in_years = term_in_years
        self._mortgage = None

        self.pmi_rate = pmi_rate
        self._pmi = None

        self.payments = []

    @property
    def current_value(self):
        return self.mortgage.purchase_amount

    @property
    def current_equity(self):
        return self.current_value - self.remaining_balance

    @property
    def current_percent_equity(self):
        return self.current_equity / self.current_value
    
    # Mortgage pass-throughs
    @property
    def mortgage(self):
        if self._mortgage is None:
            self._mortgage = common_loans.Mortgage(self.purchase_month,
                                                   self.purchase_amount,
                                                   self.down_payment_percent,
                                                   self.apr,
                                                   self.term_in_years)
        return self._mortgage

    @property
    def financed_amount(self):
        return self.mortgage.financed_amount
    
    @property
    def remaining_balance(self):
        return self.mortgage.remaining_balance

    @property
    def minimum_payment(self):
        return self.mortgage.minimum_payment

    @property
    def last_payment_month(self):
        return self.mortgage.last_payment_month

    def total_interest_paid(self, year=None):
        return self.mortgage.total_interest_paid(year)

    # PMI pass-throughs
    @property
    def pmi(self):
        if self._pmi is None:
            self._pmi = PMI(self, self.pmi_rate)
        return self._pmi
    
    @property
    def pmi_payment(self):
        return self.pmi.pmi_payment

    @property
    def total_pmi_paid(self):
        if not self.payments:
            return 0
        return sum(p.pmi_amount for p in self.payments)

    def make_monthly_payment(self, payment_month=None):
        pmi_payment = self.pmi.pmi_payment
        mortgage_payment = self.mortgage.make_payment(payment_month)
        home_payment = HomePayment(mortgage_payment, pmi_payment)
        self.payments.append(home_payment)
        return home_payment

    def calculate_amortization_table(self):
        while self.remaining_balance > 0:
            self.make_monthly_payment()
        return self.payments