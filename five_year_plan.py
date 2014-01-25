import datetime
import copy

import people
import home
import tax_calculators
import common_loans
from data import FilingStatus


class YearSummary(object):
    """docstring for YearSummary"""
    def __init__(self, family, year):
        super().__init__()
        self.family = family
        self.year = year
        self.gross_income = self.family.gross_income(year)
        self.retirement = self.family.retirement_contribution(year)
        self.healthcare = self.family.healthcare_contribution(year)
        self.mortgage_interest = self.family.mortgage_interest_payments(year)
        self.itemized_deductions = self.family.itemized_deductions(year)
        self.fed_taxes = None
        self.fica = None
        self.state = None
        self.property = None
        self.std_deduction = None
        self.net_income = None

    def calculate_summary(self, tax_calculator=None):
        if tax_calculator is None:
            tax_calculator = tax_calculators.TaxCalculator(self.family, self.year)

        self.total_taxes = tax_calculator.total_taxes
        self.fed_taxes = tax_calculator.federal_taxes
        self.fica = tax_calculator.fica_taxes
        self.state = tax_calculator.state_taxes
        self.property = tax_calculator.property_taxes
        self.fed_agi = tax_calculator.federal_agi
        self.state_agi = tax_calculator.state_agi
        self.std_deduction = tax_calculator.federal_standard_deduction
        self.student_loan_deduction = tax_calculator.student_loan_interest_deduction

        self.net_income = self.gross_income - sum((self.retirement, self.healthcare)) - self.total_taxes

    def __str__(self):
        return """
            {year} Year Summary for {family}
            ------------------------------------------
            Gross Income:                    {gross:>8d}
            Retirement Contribution:        ({retirement:>8d})
            Health Care Contribution:       ({healthcare:>8d})

            Standard Deduction:             ({std_deduction:>8d})
            Total Itemized Deductions:      ({itemized_deductions:>8d})
                Mortgage Interest Payments: ({mort_int:>8d})
            Student Loan Interest:          ({student_loan_int:>8d})

            Federal Taxable Income:         {fed_agi:>8d}
            State Taxable Income:           {state_agi:>8d}

            Federal Income Tax:             ({fed_taxes:>8d})
            State Income Tax:               ({state:>8d})
            FICA Tax:                       ({fica:>8d})
            Property Tax:                   ({prop:>8d})

            Net Income:                     {net:>8d}
            Effective Tax Rate:             {eff_rate:>8.2%}

        """.format(year=self.year,
                   family=self.family,
                   gross=int(round(self.gross_income)),
                   retirement=int(round(self.retirement)),
                   std_deduction=int(round(self.std_deduction)),
                   itemized_deductions=int(round(self.itemized_deductions)),
                   mort_int=int(round(self.mortgage_interest)),
                   student_loan_int=int(round(self.student_loan_deduction)),
                   healthcare=int(round(self.healthcare)),
                   fed_agi=int(round(self.fed_agi)),
                   state_agi=int(round(self.state_agi)),
                   fed_taxes=int(round(self.fed_taxes)),
                   state=int(round(self.state)),
                   fica=int(round(self.fica)),
                   prop=int(round(self.property)),
                   net=int(round(self.net_income)),
                   eff_rate=self.fed_taxes/self.gross_income)

def main():
    year = 2013

    sam = people.Person('sam')
    sam.set_gross_income(year, 80000)
    sam.set_retirement_contribution_rate(year, 0.05)
    sam.set_healthcare_contribution(year, 1000)

    april = people.Person('april')
    april.set_gross_income(year, 100000)
    april.set_retirement_contribution_rate(year, 0.06)
    april.set_healthcare_contribution(year, 1500)

    f = people.Family((sam, april),
                      filing_status=FilingStatus.MARRIED_JOINT,
                      state_of_residence='GA')


    s_max_pmts = common_loans.StudentLoan()
    s_max_pmts.start_date =  datetime.date(year, 1, 1)
    s_max_pmts.start_amount = 160000
    s_max_pmts.apr = 0.068
    s_max_pmts.term_in_years = 10

    s_min_pmts = copy.copy(s_max_pmts)
    s_min_pmts.calculate_amortization_table()
    s_max_pmts.calculate_amortization_table(6000)

    h_small = home.Home()
    h_small.purchase_date = datetime.date(year, 1, 1)
    h_small.purchase_amount = 200000
    h_small.down_payment_percent = 0.10
    h_small.apr = 0.05
    h_small.term_in_years = 30
    h_small.calculate_amortization_table()

    h_huge = home.Home()
    h_huge.purchase_date = datetime.date(year, 1, 1)
    h_huge.purchase_amount = 400000
    h_huge.down_payment_percent = 0.10
    h_huge.apr = 0.05
    h_huge.term_in_years = 30
    h_huge.calculate_amortization_table()

    print("Just rent")
    summary = YearSummary(f, year)
    summary.calculate_summary()
    print(summary)

    print("Add student loans, max payments")
    f.student_loan = s_max_pmts
    summary = YearSummary(f, year)
    summary.calculate_summary()
    print(summary)

    print("Add student loans, min payments")
    f.student_loan = s_min_pmts
    summary = YearSummary(f, year)
    summary.calculate_summary()
    print(summary)

    print("Buy a small home:")
    f.home = h_small
    summary = YearSummary(f, year)
    summary.calculate_summary()
    print(summary)

    print("Buy a huge home:")
    f.home = h_huge
    summary = YearSummary(f, year)
    summary.calculate_summary()
    print(summary)


if __name__ == '__main__':
    main()
