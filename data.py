import enum

FilingStatus = enum.Enum(["SINGLE", "MARRIED_JOINT"])

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
            'social_security_tax_rate': 0.062,
            'social_security_tax_wage_base_limit': 113700.0,
            'standard_deduction_amount': 12200.0,
            'exemption_amount_per_person': 3900.0,
            'student_loan_max_deduction': 2500.0,
            'student_loan_phaseout_denominator': 30000.0,
            'student_loan_phaseout_numerator_reduction': 125000.0
        },
        FilingStatus.SINGLE: {
            'student_loan_max_deduction': 2500.0,
            'student_loan_phaseout_denominator': 15000.0,
            'student_loan_phaseout_numerator_reduction': 60000.0
        }
    },
    2014: {
        FilingStatus.MARRIED_JOINT: {
            'tax_brackets':
                [
                    (      0, 0.10  ),
                    (  18150, 0.15  ),
                    (  73800, 0.25  ),
                    ( 148850, 0.28  ),
                    ( 226850, 0.33  ),
                    ( 405100, 0.35  ),
                    ( 457600, 0.396 )
                ],
            'medicare_tax_rate': 0.0145,
            'social_security_tax_rate': 0.062,
            'social_security_tax_wage_base_limit': 117000.0,
            'standard_deduction_amount': 12400.0,
            'exemption_amount_per_person': 3950.0,
            'student_loan_max_deduction': 2500.0,
            'student_loan_phaseout_denominator': 30000.0,
            'student_loan_phaseout_numerator_reduction': 130000.0
        }
    }
}


state_tax_data = {
    'GA': {
        2013: {
            FilingStatus.MARRIED_JOINT: {
                'tax_brackets':
                [
                    (     0, 0.01 ),
                    (  1000, 0.02 ),
                    (  3000, 0.03 ),
                    (  5000, 0.04 ),
                    (  7000, 0.05 ),
                    ( 10000, 0.06)
                ],
                'exemption_amount_per_person': 2700.0,
                'standard_deduction_amount': 3000.0,
            },
        },
    },
}

class FederalTaxDao(object):
    def __init__(self, year, filing_status):
        super().__init__()
        self.year = year
        self.filing_status = filing_status
    def get_data(self):
        return federal_tax_data[self.year][self.filing_status]
    

class FederalTaxData(object):
    """docstring for FederalTaxData"""
    def __init__(self, year, filing_status, tax_dao=None):
        super().__init__()
        self.year = year
        self.filing_status = filing_status
        self._tax_dao = tax_dao

        _tax_data = self.tax_dao.get_data()
        self.tax_brackets = _tax_data['tax_brackets']
        self.medicare_tax_rate = _tax_data['medicare_tax_rate']
        self.social_security_tax_rate = _tax_data['social_security_tax_rate']
        self.social_security_tax_wage_base_limit = _tax_data['social_security_tax_wage_base_limit']
        self.standard_deduction_amount = _tax_data['standard_deduction_amount']
        self.exemption_amount_per_person = _tax_data['exemption_amount_per_person']
        self.student_loan_max_deduction = _tax_data['student_loan_max_deduction'] 
        self.student_loan_phaseout_denominator = _tax_data['student_loan_phaseout_denominator'] 
        self.student_loan_phaseout_numerator_reduction = _tax_data['student_loan_phaseout_numerator_reduction'] 

    @property
    def tax_dao(self):
        if self._tax_dao is None:
            self._tax_dao = FederalTaxDao(self.year, self.filing_status)
        return self._tax_dao
    @tax_dao.setter
    def tax_dao(self, value):
        self._tax_dao = value


class StateTaxDao(object):
    def __init__(self, state, year, filing_status):
        super().__init__()
        self.state = state
        self.year = year
        self.filing_status = filing_status
    def get_data(self):
        return state_tax_data[self.state][self.year][self.filing_status]

class StateTaxData(object):
    """docstring for StateTaxData"""
    def __init__(self, state, year, filing_status, tax_dao=None):
        super().__init__()
        self.state = state
        self.year = year
        self.filing_status = filing_status
        self._tax_dao = tax_dao

        _tax_data = self.tax_dao.get_data()
        self.tax_brackets = _tax_data['tax_brackets']
        self.standard_deduction_amount = _tax_data['standard_deduction_amount']
        self.exemption_amount_per_person = _tax_data['exemption_amount_per_person']

    @property
    def tax_dao(self):
        if self._tax_dao is None:
            self._tax_dao = StateTaxDao(self.state, self.year, self.filing_status)
        return self._tax_dao
    @tax_dao.setter
    def tax_dao(self, value):
        self._tax_dao = value