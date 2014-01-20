import people
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
        self.net_income = None

    def calculate_summary(self, tax_calculator=None):
        if tax_calculator is None:
            tax_calculator = tax_calculators.TaxCalculator(self.family, self.year)

        self.total_taxes = tax_calculator.total_taxes
        self.fed_taxes = tax_calculator.federal_taxes
        self.fica = tax_calculator.fica_taxes
        self.state = tax_calculator.state_taxes
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

            FICA Tax:                   ({fica:>8d})
            Federal Income Tax:         ({fed_taxes:>8d})
            State Income Tax:           ({state:>8d})

            Net Income:                  {net:>8d}
            Effective Tax Rate:          {eff_rate:>10.2%}

        """.format(family=self.family,
                   year=self.year,
                   gross=round(self.gross_income),
                   retirement=round(self.retirement),
                   healthcare=round(self.healthcare),
                   fed_taxes=round(self.fed_taxes),
                   fica=round(self.fica),
                   state=round(self.state),
                   fed_agi=round(self.fed_agi),
                   state_agi=round(self.state_agi),
                   net=round(self.net_income),
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



if __name__ == '__main__':
    main()
