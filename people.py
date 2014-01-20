
class Deduction(object):
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

class Person(object):
    """Holds data for a person"""
    def __init__(self, name):
        super(Person, self).__init__()
        self.name = name
        self._gross_income = {}
        self._healthcare_contribution = {}
        self._retirement_contribution_rate = {}


    def gross_income(self, year):
        if year in self._gross_income:
            return float(self._gross_income[year])
        else:
            return 0

    def set_gross_income(self, year, gross_income):
        self._gross_income[year] = gross_income

    def healthcare_contribution(self, year):
        if year in self._healthcare_contribution:
            return self._healthcare_contribution[year]
        else:
            return 0
    
    def set_healthcare_contribution(self, year, healthcare_contribution):
        self._healthcare_contribution[year] = healthcare_contribution

    def set_retirement_contribution_rate(self, year, retirement_contribution_rate):
        self._retirement_contribution_rate[year]  = retirement_contribution_rate

    def retirement_contribution_rate(self, year):
        if year in self._retirement_contribution_rate:
            return self._retirement_contribution_rate[year]
        else:
            return 0

    def retirement_contribution(self, year):
        return self.retirement_contribution_rate(year) * self.gross_income(year)

    def __str__(self):
        return "{}".format(self.name)

class Family(object):
    """docstring for Family"""
    def __init__(self, members, filing_status, state_of_residence=None):
        super(Family, self).__init__()
        self.members = members
        self.filing_status = filing_status
        self.state_of_residence = state_of_residence
        self._deductions = {}
        self._student_loan_interest_payments = {}

    def __str__(self):
        return "Family({})".format(
            ", ".join(str(p) for p in self.members)
        )

    def gross_income(self, year):
        return sum(p.gross_income(year) for p in self.members)

    def healthcare_contribution(self, year):
        return sum(p.healthcare_contribution(year) for p in self.members)
    
    def retirement_contribution(self, year):
        return sum(p.retirement_contribution(year) for p in self.members)

    @property
    def member_count(self):
        return len(self.members)

    def deduct(self, year, deduction):
        if year in self._deductions:
            self._deductions[year].append(deduction)
        else:
            self._deductions[year] = [deduction]

    def deductions(self, year):
        if year in self._deductions:
            return sum(d.amount for d in self._deductions[year])
        else:
            return 0

    def pay_student_loan_interest(self, year, amount):
        if year in self._student_loan_interest_payments:
            self._student_loan_interest_payments[year].append(amount)
        else:
            self._student_loan_interest_payments[year] = [amount]

    def student_loan_interest_payments(self, year):
        if year in self._student_loan_interest_payments:
            return sum(d for d in self._student_loan_interest_payments[year])
        else:
            return 0