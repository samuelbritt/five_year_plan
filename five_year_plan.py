import numpy as np

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

FilingStatus = Enum(["SINGLE", "MARRIED_JOINT"])

class Person(object):
    """Holds data for a person"""
    def __init__(self,
                 name,
                 yearly_gross_income=0.0,
                 retirement_contribution_rate=0.0,
                 yearly_healthcare_contribution=0.0):
        super(Person, self).__init__()
        self.name = name
        self.yearly_gross_income = yearly_gross_income
        self.retirement_contribution_rate = retirement_contribution_rate
        self.yearly_healthcare_contribution = yearly_healthcare_contribution
    
    def __str__(self):
        return "{}: {}k/year".format(
            self.name,
            int(self.yearly_gross_income/1000.0)
        )

class Family(object):
    """docstring for Family"""
    def __init__(self, members, filing_status=FilingStatus.MARRIED_JOINT):
        super(Family, self).__init__()
        self.members = members
        self.filing_status = filing_status

    def __str__(self):
        return "Family({})".format(
            ", ".join(str(p) for p in self.members)
        )

    @property
    def yearly_gross_income(self):
        return sum(p.yearly_gross_income for p in self.members)

    @property
    def yearly_healthcare_contribution(self):
        return sum(p.yearly_healthcare_contribution for p in self.members)
    
    @property
    def yearly_retirement_contribution(self):
        return sum(p.retirement_contribution_rate * p.yearly_gross_income for p in self.members)

class AmortizedLoan(object):
    """docstring for AmortizedLoan"""
    def __init__(self, purchase_amount, apr, term_in_years):
        super(AmortizedLoan, self).__init__()
        self.purchase_amount = purchase_amount
        self.apr = apr
        self.term_in_years = term_in_years

        self.min_payment = -np.pmt(self.apr/12, 12*self.term_in_years, self.purchase_amount)
        self.total_interest_paid = 0
        self.total_prinicple_paid = 0

    def make_payment(self, payment_amount):
        pass

federal_tax_data = {
    2013: {
        FilingStatus.MARRIED_JOINT: {
                'tax_brackets':
                    [
                        (      0, 0.10  ),
                        (  17850, 0.15  ),
                        (  72500, 0.25  ),
                        ( 146400, 0.28  ),
                        ( 223050, 0.33  ),
                        ( 398350, 0.35  ),
                        ( 450000, 0.396 )
                    ],
                'medicare_tax_rate': 0.0145,
                'social_security_tax_rate': 0.62,
                'social_security_tax_max_amount_per_person': 70500.0,
                'standard_deduction_amount': 12200.0,
                'exemption_amount_per_person': 3900.0
        }
    }
}

def student_loan_interest_deduction(MAGI,
                                    total_interest_paid,
                                    filing_status=FilingStatus.MARRIED_JOINT):
    """ Returns the amount of money you can deduct from your taxes,
        given modified adjusted gross income and total interest paid.
    """
    max_deduction = 2500.0
    phaseout_denominator = 30000.0
    phaseout_numerator_reduction = 125000.0
    deduction_due_to_phaseout = 0.0

    if filing_status == FilingStatus.SINGLE:
        max_magi = 75000.0
        phaseout_denominator = 15000.0
        phaseout_numerator_reduction = 60000.0

    total_interest_paid = min(total_interest_paid, max_deduction)
    deduction_due_to_phaseout = max(
        total_interest_paid *
            (MAGI - phaseout_numerator_reduction) / float(phaseout_denominator),
        0.0
    )
    return max(total_interest_paid - deduction_due_to_phaseout, 0.0)



def _federal_income_tax(gross_income,
                        tax_brackets,
                        bracket_index=-1,
                        taxes_so_far=0):
    """ Returns the amount of federal taxes, in dollars, given a gross income
    and set of tax brackets. Assumes the brackets are of the form
        [(income_level_x, rate_above_x), (income_level_y, rate_above_y), ...]
    in increasing order.
    """
    if gross_income > 0:
        income_level, rate = tax_brackets[bracket_index]
        taxes_so_far += (
                 rate * max(gross_income - income_level, 0) +
                 _federal_income_tax(min(gross_income, income_level),
                                         tax_brackets,
                                         bracket_index - 1,
                                         taxes_so_far)
                )
    return taxes_so_far

def federal_income_tax(persons, tax_brackets):
    return _federal_income_tax(family.yearly_gross_income, tax_brackets, -1, 0)

def federal_fica_tax(family,
                     medicare_tax_rate,
                     social_security_tax_rate,
                     social_security_tax_max_amount_per_person):
    return (
        medicare_tax_rate * (family.yearly_gross_income - family.yearly_healthcare_contribution) +
        sum(
            [
                min(p.yearly_gross_income * social_security_tax_rate,
                    social_security_tax_max_amount_per_person)
                for p in family.members
            ]
        )
    )

def federal_taxes(persons,
                  tax_year=2013):
    tax_data = federal_tax_data[tax_year][family.filing_status]
    income_tax = federal_income_tax(persons, tax_data['tax_brackets'])

    fica_tax = federal_fica_tax(persons,
                                tax_data['medicare_tax_rate'],
                                tax_data['social_security_tax_rate'],
                                tax_data['social_security_tax_max_amount_per_person'])

    return income_tax, fica_tax

def federal_taxable_income(persons):
    pass

if __name__ == '__main__':
    # print(student_loan_interest_deduction(5000, 2700))
    # print(student_loan_interest_deduction(5000, 800))
    # print(student_loan_interest_deduction(125000, 800))
    # print(student_loan_interest_deduction(125000, 2750))
    # print(student_loan_interest_deduction(125001, 2750))
    # print(student_loan_interest_deduction(145000, 800))
    # print(student_loan_interest_deduction(145000, 2750))
    # print(student_loan_interest_deduction(155000, 2750))
    # print(student_loan_interest_deduction(175000, 2750))


    sam = Person("sam")
    sam.yearly_gross_income = 40000
    sam.health_insurance_paid_per_year = 1090
    sam.retirement_contribution_rate = 0.05

    april = Person("april")
    april.yearly_gross_income = 102340
    april.health_insurance_paid_per_year = 1690
    april.retirement_contribution_rate = 0.06

    print(sam)
    print(april)
    family = Family([sam, april], FilingStatus.MARRIED_JOINT)
    
    sam.yearly_gross_income = 0
    april.yearly_gross_income = 0
    
    print(family)
    print(federal_taxes(family))

    sam.yearly_gross_income = 0
    print(0, federal_taxes(family))
    sam.yearly_gross_income = 5000
    print(5000, federal_taxes(family))
    sam.yearly_gross_income = 150000
    print(150000, federal_taxes(family))
    sam.yearly_gross_income = 73480
    print(73480, federal_taxes(family))
    sam.yearly_gross_income = 100240
    print(100240, federal_taxes(family))
    sam.yearly_gross_income = 147270
    print(147270, federal_taxes(family))
    sam.yearly_gross_income = 149640
    print(149640, federal_taxes(family))
    sam.yearly_gross_income = 153400
    print(153400, federal_taxes(family))
    sam.yearly_gross_income = 157160
    print(157160, federal_taxes(family))
    sam.yearly_gross_income = 160920
    print(160920, federal_taxes(family))

    # sam.yearly_gross_income = 74170
    # april.yearly_gross_income = 53870
    # print(federal_taxes(family))
    # print(federal_taxes(( 99840, 80000)))
    # print(federal_taxes((102340, 80000)))
    # print(federal_taxes((102340, 84000)))
    # print(federal_taxes((102340, 88000)))
    # print(federal_taxes((102340, 92000)))