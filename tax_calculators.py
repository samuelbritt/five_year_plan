import people
import data


class Calculator(object):
    """Tax-related calculator. Abstract class. Always needs a family and a tax year"""
    def __init__(self, family, year, tax_data=None):
        super().__init__()
        self.family = family
        self.year = year
        self._tax_data = tax_data

    @property
    def tax_data(self):
        if self._tax_data is None:
            self._tax_data = self.get_new_tax_data()#data.FederalTaxData(self.year, self.family.filing_status)
        return self._tax_data

    @tax_data.setter
    def tax_data(self, value):
        self._tax_data = value

    def get_new_tax_data(self):
        pass

    def calculate(self):
        pass

class FederalCalculator(Calculator):
    """docstring for FederalCalculator"""
    def __init__(self, family, year, tax_data=None):
        super().__init__(family, year, tax_data)
        # self._tax_data = tax_data

    def get_new_tax_data(self):
        return data.FederalTaxData(self.year, self.family.filing_status)

    # @property
    # def tax_data(self):
    #     if self._tax_data is None:
    #         self._tax_data = data.FederalTaxData(self.year, self.family.filing_status)
    #     return self._tax_data

    # @tax_data.setter
    # def tax_data(self, value):
    #     self._tax_data = value


class StateCalculator(Calculator):
    """docstring for StateCalculator"""
    def __init__(self, family, year, tax_data=None):
        super().__init__(family, year, tax_data)
        # self._tax_data = tax_data

    def get_new_tax_data(self):
        return data.StateTaxData(self.family.state_of_residence, self.year, self.family.filing_status)

    # @property
    # def tax_data(self):
    #     if self._tax_data is None:
    #         self._tax_data = data.StateTaxData(self.family.state_of_residence, self.year, self.family.filing_status)
    #     return self._tax_data

    # @tax_data.setter
    # def tax_data(self, value):
    #     self._tax_data = value

class MagiCalculator(FederalCalculator):
    """Calculates MAGI"""
    def __init__(self, family, year, tax_data=None):
        super().__init__(family, year, tax_data)

    def calculate(self):
        magi = (
            self.family.gross_income(self.year)
            - self.family.member_count * self.tax_data.exemption_amount_per_person
            - max(self.tax_data.standard_deduction_amount, self.family.deductions(self.year))
            - self.family.retirement_contribution(self.year)
            - self.family.healthcare_contribution(self.year)
        )
        return max(magi, 0.0)

class StudentLoanInterestDeductionCalculator(FederalCalculator):
    """Calculates student loan interest deduction"""
    def __init__(self, family, year, tax_data=None, magi_calculator=None):
        super().__init__(family, year, tax_data)
        self._magi_calculator = magi_calculator

    @property
    def magi_calculator(self):
        if self._magi_calculator is None:
            self._magi_calculator = MagiCalculator(self.family, self.year, self.tax_data)
        return self._magi_calculator

    @magi_calculator.setter
    def magi_calculator(self, value):
        self._magi_calculator = value

    def calculate(self):
        """ Returns the amount of money you can deduct from your taxes,
            given modified adjusted gross income and total interest paid.
            See http://www.irs.gov/publications/p970/ch04.html
        """
        max_deduction = self.tax_data.student_loan_max_deduction
        phaseout_denominator = self.tax_data.student_loan_phaseout_denominator
        phaseout_numerator_reduction = self.tax_data.student_loan_phaseout_numerator_reduction
        magi = self.magi_calculator.calculate()

        total_interest_paid = min(self.family.student_loan_interest_payments(self.year), max_deduction)
        phaseout_multiplier = (magi - phaseout_numerator_reduction) / float(phaseout_denominator)
        deduction_due_to_phaseout = max(total_interest_paid * phaseout_multiplier, 0.0)
        return max(total_interest_paid - deduction_due_to_phaseout, 0.0)
        

class FederalAgiCalculator(FederalCalculator):
    """docstring for FederalAgiCalculator"""
    def __init__(self, family, year, tax_data=None, magi_calculator=None, student_loan_interest_deduction_calculator=None):
        super().__init__(family, year, tax_data)
        self._magi_calculator = magi_calculator
        self._student_loan_interest_deduction_calculator = student_loan_interest_deduction_calculator

    @property
    def magi_calculator(self):
        if self._magi_calculator is None:
            self._magi_calculator = MagiCalculator(self.family, self.year, self.tax_data)
        return self._magi_calculator

    @magi_calculator.setter
    def magi_calculator(self, value):
        self._magi_calculator = value

    @property
    def student_loan_interest_deduction_calculator(self):
        if self._student_loan_interest_deduction_calculator is None:
            self._student_loan_interest_deduction_calculator = StudentLoanInterestDeductionCalculator(self.family, self.year, self.tax_data, self.magi_calculator)
        return self._student_loan_interest_deduction_calculator
    
    @student_loan_interest_deduction_calculator.setter
    def student_loan_interest_deduction_calculator(self, value):
        self._student_loan_interest_deduction_calculator = value

    def calculate(self):
        magi = self.magi_calculator.calculate()
        student_loan_interest_deduction = self.student_loan_interest_deduction_calculator.calculate()
        return magi - student_loan_interest_deduction


class TaxBracketCalculator(Calculator):
    def __init__(self, family, year, tax_data, agi_calculator):
        super().__init__(family, year, tax_data)
        self.agi_calculator = agi_calculator

    def _income_tax(self,
                    income,
                    tax_brackets,
                    bracket_index=-1,
                    taxes_so_far=0):
        """ Recursive helper function.
        Returns the amount of federal taxes, in dollars, given a (taxable) income
        and set of tax brackets. Assumes the brackets are of the form
            [(income_level_x, rate_above_x), (income_level_y, rate_above_y), ...]
        in increasing order.
        """
        if income > 0:
            income_level, rate = tax_brackets[bracket_index]
            taxes_so_far += (
                     rate * max(income - income_level, 0) +
                     self._income_tax(min(income, income_level),
                                      tax_brackets,
                                      bracket_index - 1,
                                      taxes_so_far)
                    )
        return taxes_so_far

    def calculate(self):
        taxable_income = self.agi_calculator.calculate()
        return self._income_tax(taxable_income, self.tax_data.tax_brackets)#, -1, 0)

##
## Federal Income Tax
##
class FederalIncomeTaxCalculator(FederalCalculator):
    """docstring for IncomeTax"""
    def __init__(self, family, year, tax_data=None, federal_agi_calculator=None):
        super().__init__(family, year, tax_data)
        self._federal_agi_calculator = federal_agi_calculator

    @property
    def federal_agi_calculator(self):
        if self._federal_agi_calculator is None:
            self._federal_agi_calculator = FederalAgiCalculator(self.family, self.year, self.tax_data)
        return self._federal_agi_calculator

    @federal_agi_calculator.setter
    def federal_agi_calculator(self, value):
        self._federal_agi_calculator = value

    @property
    def agi(self):
        return self.federal_agi_calculator.calculate()

    def calculate(self):
        bracket_calculator = TaxBracketCalculator(self.family, self.year, self.tax_data, self.federal_agi_calculator)
        return bracket_calculator.calculate()


##
## Federal FICA Tax
##
class MedicareTaxCalculator(FederalCalculator):
    """docstring for MedicareTaxCalculator"""
    def __init__(self, family, year, tax_data=None):
        super().__init__(family, year, tax_data)
    def calculate(self):
        medicare_tax_rate = self.tax_data.medicare_tax_rate
        medicare_taxable_income = self.family.gross_income(self.year) - self.family.healthcare_contribution(self.year)
        return medicare_tax_rate * medicare_taxable_income

class SocialSecurityTaxCalculator(FederalCalculator):
    """docstring for SocialSecurityTaxCalculator"""
    def __init__(self, family, year, tax_data=None):
        super().__init__(family, year, tax_data)
    def calculate(self):
        social_security_tax_wage_base_limit = self.tax_data.social_security_tax_wage_base_limit
        social_security_tax_rate = self.tax_data.social_security_tax_rate
        social_security_taxable_income = sum(min(p.gross_income(self.year), social_security_tax_wage_base_limit) for p in self.family.members)
        return social_security_tax_rate * social_security_taxable_income

class FicaTaxCalculator(FederalCalculator):
    """docstring for FICATax"""
    def __init__(self, family, year, tax_data=None, medicare_tax_calculator=None, social_security_tax_calculator=None):
        super().__init__(family, year, tax_data)
        self._medicare_tax_calculator = medicare_tax_calculator
        self._social_security_tax_calculator = social_security_tax_calculator

    @property
    def medicare_tax_calculator(self):
        if self._medicare_tax_calculator is None:
            self._medicare_tax_calculator = MedicareTaxCalculator(self.family, self.year, self.tax_data)
        return self._medicare_tax_calculator

    @medicare_tax_calculator.setter
    def medicare_tax_calculator(self, value):
        self._federal_agi_calculator = value

    @property
    def social_security_tax_calculator(self):
        if self._social_security_tax_calculator is None:
            self._social_security_tax_calculator = SocialSecurityTaxCalculator(self.family, self.year, self.tax_data)
        return self._social_security_tax_calculator

    @social_security_tax_calculator.setter
    def social_security_tax_calculator(self, value):
        self._federal_agi_calculator = value

    def calculate(self):
        return self.medicare_tax_calculator.calculate() + self.social_security_tax_calculator.calculate()

##
## State Income Tax Calculator
##
class StateAgiCalculator(StateCalculator):
    def __init__(self, family, year, tax_data=None):
        super().__init__(family, year, tax_data)
    
    def calculate(self):
        agi = (
            self.family.gross_income(self.year)
            - self.family.member_count * self.tax_data.exemption_amount_per_person
            - max(self.tax_data.standard_deduction_amount, self.family.deductions(self.year))
            - self.family.retirement_contribution(self.year)
        )
        return max(agi, 0.0)

class StateIncomeTaxCalculator(StateCalculator):
    """docstring for StateIncomeTaxCalculator"""
    def __init__(self, family, year, tax_data=None, state_agi_calculator=None):
        super().__init__(family, year, tax_data)
        self._state_agi_calculator = state_agi_calculator

    @property
    def state_agi_calculator(self):
        if self._state_agi_calculator is None:
            self._state_agi_calculator = StateAgiCalculator(self.family, self.year, self.tax_data)
        return self._state_agi_calculator
    @state_agi_calculator.setter
    def state_agi_calculator(self, value):
        self._state_agi_calculator = value

    @property
    def agi(self):
        return self.state_agi_calculator.calculate()

    def calculate(self):
        bracket_calculator = TaxBracketCalculator(self.family, self.year, self.tax_data, self.state_agi_calculator)
        return bracket_calculator.calculate()


class TaxCalculator(Calculator):
    def __init__(
            self,
            family,
            year,
            federal_income_tax_calculator=None,
            fica_tax_calculator=None,
            state_income_tax_calculator=None
        ):
        super().__init__(family, year)
        self._federal_income_tax_calculator = federal_income_tax_calculator
        self._fica_tax_calculator = fica_tax_calculator
        self._state_income_tax_calculator = state_income_tax_calculator

    @property
    def state_income_tax_calculator(self):
        if self._state_income_tax_calculator is None:
            self._state_income_tax_calculator = StateIncomeTaxCalculator(self.family, self.year)
        return self._state_income_tax_calculator
    @state_income_tax_calculator.setter
    def state_income_tax_calculator(self, value):
        self._state_income_tax_calculator = value

    @property
    def federal_income_tax_calculator(self):
        if self._federal_income_tax_calculator is None:
            self._federal_income_tax_calculator = FederalIncomeTaxCalculator(self.family, self.year)
        return self._federal_income_tax_calculator
    @federal_income_tax_calculator.setter
    def federal_income_tax_calculator(self, value):
        self._federal_income_tax_calculator = value

    @property
    def fica_tax_calculator(self):
        if self._fica_tax_calculator is None:
            self._fica_tax_calculator = FicaTaxCalculator(self.family, self.year)
        return self._fica_tax_calculator
    @fica_tax_calculator.setter
    def fica_tax_calculator(self, value):
        self._fica_tax_calculator = value

    @property
    def federal_agi(self):
        return self.federal_income_tax_calculator.agi
    
    @property
    def state_agi(self):
        return self.state_income_tax_calculator.agi

    @property
    def federal_taxes(self):
        return self.federal_income_tax_calculator.calculate()

    @property
    def fica_taxes(self):
        return self.fica_tax_calculator.calculate()

    @property
    def state_taxes(self):
        return self.state_income_tax_calculator.calculate()

    @property
    def total_taxes(self):
        return sum((self.federal_taxes, self.state_taxes, self.fica_taxes))

    def calculate(self):
        return self.total_taxes

class NetIncomeCalculator(Calculator):
    """docstring for NetIncomeCalculator"""
    def __init__(self, family, year, tax_calculator=None):
        super().__init__(family, year)
        self._tax_calculator = tax_calculator

    @property
    def tax_calculator(self):
        if self._tax_calculator is None:
            self._tax_calculator = TaxCalculator(self.family, self.year)
        return self._tax_calculator

    @tax_calculator.setter
    def tax_calculator(self, value):
        self._tax_calculator = value
    
    def calculate(self):
        gross = self.family.gross_income(self.year)
        retirement = self.family.retirement_contribution(self.year)
        healthcare = self.family.healthcare_contribution(self.year)

        taxes = self.tax_calculator.calculate()

        return gross - sum((retirement, healthcare)) - taxes

if __name__ == '__main__':
    pass
