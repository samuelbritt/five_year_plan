import datetime

import people
import home
import tax_calculators
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
        self.fed_taxes = None
        self.fica = None
        self.state = None
        self.property = None
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

        self.net_income = self.gross_income - sum((self.retirement, self.healthcare)) - self.total_taxes

    def __str__(self):
        return """
            {year} Year Summary for {family}
            ------------------------------------------
            Gross Income:                {gross:>8d}
            Retirement Contribution:    ({retirement:>8d})
            Health Care Contribution:   ({healthcare:>8d})

            Federal Taxable Income:      {fed_agi:>8d}
            State Taxable Income:        {state_agi:>8d}

            Federal Income Tax:         ({fed_taxes:>8d})
            State Income Tax:           ({state:>8d})
            FICA Tax:                   ({fica:>8d})
            Property Tax:               ({prop:>8d})

            Net Income:                  {net:>8d}
            Effective Tax Rate:          {eff_rate:>8.2%}

        """.format(year=self.year,
                   family=self.family,
                   gross=int(round(self.gross_income)),
                   retirement=int(round(self.retirement)),
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

    summary = YearSummary(f, year)
    summary.calculate_summary()
    print(summary)

    print("Buy a home:")
    h = home.Home()
    h.purchase_date = datetime.date(2013, 1, 1)
    h.purchase_amount = 200000
    h.down_payment_percent = 0.10
    h.apr = 0.05
    h.term_in_years = 30
    f.home = h
    h.calculate_amortization_table()

    summary = YearSummary(f, year)
    summary.calculate_summary()
    print(summary)

if __name__ == '__main__':
    main()
