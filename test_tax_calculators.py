import unittest

import people
import tax_calculators
import common_loans
import data

class MockFederalTaxDao(data.FederalTaxDao):
    def __init__(self, year, filing_status):
        super().__init__(year, filing_status)
    def get_data(self):
        return {
            'tax_brackets': [
                (      0, 0.10  ),
                (  17850, 0.15  ),
                (  72500, 0.25  ),
                ( 146400, 0.28  ),
                ( 223050, 0.33  ),
                ( 398350, 0.35  ),
                ( 450000, 0.396 )
            ],
            'medicare_tax_rate': 0.0145,
            'social_security_tax_rate': .062,
            'social_security_tax_wage_base_limit': 113700.0,
            'standard_deduction_amount': 12200.0,
            'exemption_amount_per_person': 3900.0,
            'student_loan_max_deduction': 2500.0,
            'student_loan_phaseout_denominator': 30000.0,
            'student_loan_phaseout_numerator_reduction': 125000.,
        }

class MockFederalTaxData(data.FederalTaxData):
    def __init__(self, year, filing_status):
        super().__init__(year, filing_status, MockFederalTaxDao(year, filing_status))

class MockStateTaxDao(data.StateTaxDao):
    def __init__(self, state, year, filing_status):
        super().__init__(state, year, filing_status)
    def get_data(self):
        return {
            'tax_brackets':
                [
                    (     0, 0.01 ),
                    (  1000, 0.02 ),
                    (  3000, 0.03 ),
                    (  5000, 0.04 ),
                    (  7000, 0.05 ),
                    ( 10000, 0.06)
                ],
            'standard_deduction_amount': 3000.0,
            'exemption_amount_per_person': 2700.0,
        }

class MockStateTaxData(data.StateTaxData):
    def __init__(self, state, year, filing_status):
        super().__init__(state, year, filing_status, MockStateTaxDao(state, year, filing_status))



class TestStudentLoan(unittest.TestCase):
    class MockMagiCalculator(tax_calculators.MagiCalculator):
        """docstring for MockMagiCalculator"""
        def __init__(self, family, year):
            super().__init__(family, year)
        
        def calculate(self):
            return self.family.gross_income(self.year)

    class MockStudentLoan(common_loans.StudentLoan):
        def __init__(self):
            super().__init__()
            self._interest_paid = 0
        
        def make_payment(self, payment_amount, payement_date):
            self._interest_paid = payment_amount

        def total_interest_paid(self, year):
            return self._interest_paid


    def setUp(self):
        self.year = 2013
        self.p1 = people.Person("p1")
        self.p1.set_gross_income(self.year, 0)
        self.p1.set_healthcare_contribution(self.year, 0)
        self.p1.set_retirement_contribution_rate(self.year, 0)

        self.p2 = people.Person("p2")
        self.p2.set_gross_income(self.year, 0)
        self.p2.set_healthcare_contribution(self.year, 0)
        self.p2.set_retirement_contribution_rate(self.year, 0)

        self.p3 = people.Person("p3")
        self.p3.set_gross_income(self.year, 17000)
        self.p3.set_healthcare_contribution(self.year, 0)
        self.p3.set_retirement_contribution_rate(self.year, 0)

        self.p4 = people.Person("p4")
        self.p4.set_gross_income(self.year, 120000)
        self.p4.set_healthcare_contribution(self.year, 0)
        self.p4.set_retirement_contribution_rate(self.year, 0)

        self.p5 = people.Person("p5")
        self.p5.set_gross_income(self.year, 25000)
        self.p5.set_healthcare_contribution(self.year, 0)
        self.p5.set_retirement_contribution_rate(self.year, 0)

        self.family_noIncome = people.Family((self.p1, self.p2), data.FilingStatus.MARRIED_JOINT)
        self.family_poor =     people.Family((self.p1, self.p3), data.FilingStatus.MARRIED_JOINT)
        self.family_midClass = people.Family((self.p1, self.p4), data.FilingStatus.MARRIED_JOINT)
        self.family_rich =     people.Family((self.p4, self.p5), data.FilingStatus.MARRIED_JOINT)

        self.mock_tax_data = MockFederalTaxData(self.year, data.FilingStatus.MARRIED_JOINT)
        self.mock_student_loan = self.MockStudentLoan()

    def tearDown(self):
        pass


    def get_mocked_student_loan_interest_deduction_calculator(self, family):
        mock_magi_calculator = self.MockMagiCalculator(family, self.year)
        mock_magi_calculator.federal_tax_data = self.mock_tax_data

        student_loan_interest_deduction_calculator = tax_calculators.StudentLoanInterestDeductionCalculator(family, self.year)
        student_loan_interest_deduction_calculator.federal_tax_data = self.mock_tax_data
        student_loan_interest_deduction_calculator.magi_calculator = mock_magi_calculator

        family.student_loan = self.mock_student_loan
        return student_loan_interest_deduction_calculator

    def test_student_loan_interest_deduction_noIncome(self):
        family = self.family_poor
        student_loan_interest_deduction_calculator = self.get_mocked_student_loan_interest_deduction_calculator(family)

        self.assertAlmostEqual(student_loan_interest_deduction_calculator.calculate(), 0)

    def test_student_loan_interest_deduction_low_income_low_interest(self):
        # low income, low interest paid: Should get full deduction
        family = self.family_poor
        student_loan_interest_deduction_calculator = self.get_mocked_student_loan_interest_deduction_calculator(family)
        family.student_loan.make_payment(800, self.year)
        self.assertAlmostEqual(student_loan_interest_deduction_calculator.calculate(), 800)

    def test_student_loan_interest_deduction_low_income_high_interest(self):
        # low income, low interest paid: Should get full deduction
        family = self.family_poor
        student_loan_interest_deduction_calculator = self.get_mocked_student_loan_interest_deduction_calculator(family)
        family.student_loan.make_payment(2700, self.year)
        self.assertAlmostEqual(student_loan_interest_deduction_calculator.calculate(), 2500)

    def test_student_loan_interest_deduction_mid_income_low_interest(self):
        # mid income, low interest paid: Should get full deduction
        family = self.family_midClass
        student_loan_interest_deduction_calculator = self.get_mocked_student_loan_interest_deduction_calculator(family)
        family.student_loan.make_payment(800, self.year)
        self.assertAlmostEqual(student_loan_interest_deduction_calculator.calculate(), 800)

    def test_student_loan_interest_deduction_mid_income_high_interest(self):
        # mid income, high interest paid: Should get full deduction
        family = self.family_midClass
        student_loan_interest_deduction_calculator = self.get_mocked_student_loan_interest_deduction_calculator(family)
        family.student_loan.make_payment(8000, self.year)
        self.assertAlmostEqual(student_loan_interest_deduction_calculator.calculate(), 2500)

    def test_student_loan_interest_deduction_high_income_low_interest(self):
        # very high income, low interest paid: deduction is phased out
        family = self.family_rich
        student_loan_interest_deduction_calculator = self.get_mocked_student_loan_interest_deduction_calculator(family)
        family.student_loan.make_payment(800, self.year)
        self.assertAlmostEqual(student_loan_interest_deduction_calculator.calculate(), 266.66666667)

    def test_student_loan_interest_deduction_high_income_high_interest(self):
        # very high income, low interest paid: deduction is phased out
        family = self.family_rich
        student_loan_interest_deduction_calculator = self.get_mocked_student_loan_interest_deduction_calculator(family)
        family.student_loan.make_payment(2700, self.year)
        self.assertAlmostEqual(student_loan_interest_deduction_calculator.calculate(), 833.3333333)

class TestFicaTax(unittest.TestCase):
    def setUp(self):
        self.year = 2013

        self.p1 = people.Person("p1")
        self.p1.set_gross_income(self.year, 0)
        self.p1.set_healthcare_contribution(self.year, 0)
        self.p1.set_retirement_contribution_rate(self.year, 0)

        self.p2 = people.Person("p2")
        self.p2.set_gross_income(self.year, 0)
        self.p2.set_healthcare_contribution(self.year, 0)
        self.p2.set_retirement_contribution_rate(self.year, 0)

        self.p3 = people.Person("p3")
        self.p3.set_gross_income(self.year, 17000)
        self.p3.set_healthcare_contribution(self.year, 0)
        self.p3.set_retirement_contribution_rate(self.year, 0.05)

        self.p4 = people.Person("p4")
        self.p4.set_gross_income(self.year, 120000)
        self.p4.set_healthcare_contribution(self.year, 1000)
        self.p4.set_retirement_contribution_rate(self.year, 0.05)

        self.p5 = people.Person("p5")
        self.p5.set_gross_income(self.year, 120000)
        self.p5.set_healthcare_contribution(self.year, 1000)
        self.p5.set_retirement_contribution_rate(self.year, 0.10)

        self.family_noIncome = people.Family((self.p1, self.p2), data.FilingStatus.MARRIED_JOINT)
        self.family_poor =     people.Family((self.p1, self.p3), data.FilingStatus.MARRIED_JOINT)
        self.family_midClass = people.Family((self.p1, self.p4), data.FilingStatus.MARRIED_JOINT)
        self.family_rich =     people.Family((self.p4, self.p5), data.FilingStatus.MARRIED_JOINT)

        self.mock_tax_data = MockFederalTaxData(self.year, self.family_noIncome.filing_status)
    
    def tearDown(self):
        pass

    def test_medicare_noIncome(self):
        medicare = tax_calculators.MedicareTaxCalculator(self.family_noIncome, self.year, self.mock_tax_data)
        self.assertAlmostEqual(medicare.calculate(), 0)

    def test_medicare_poor(self):
        medicare = tax_calculators.MedicareTaxCalculator(self.family_poor, self.year, self.mock_tax_data)
        self.assertAlmostEqual(medicare.calculate(), 246.5)

    def test_medicare_midClass(self):
        medicare = tax_calculators.MedicareTaxCalculator(self.family_midClass, self.year, self.mock_tax_data)
        self.assertAlmostEqual(medicare.calculate(), 1725.5)

    def test_medicare_rich(self):
        medicare = tax_calculators.MedicareTaxCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(medicare.calculate(), 3451)


    def test_social_security_noIncome(self):
        ss = tax_calculators.SocialSecurityTaxCalculator(self.family_noIncome, self.year, self.mock_tax_data)
        self.assertAlmostEqual(ss.calculate(), 0)

    def test_social_security_poor(self):
        ss = tax_calculators.SocialSecurityTaxCalculator(self.family_poor, self.year, self.mock_tax_data)
        self.assertAlmostEqual(ss.calculate(), 1054)

    def test_social_security_midClass(self):
        ss = tax_calculators.SocialSecurityTaxCalculator(self.family_midClass, self.year, self.mock_tax_data)
        self.assertAlmostEqual(ss.calculate(), 7049.4)

    def test_social_security_rich(self):
        ss = tax_calculators.SocialSecurityTaxCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(ss.calculate(), 14098.8)


    def test_federal_fica_noIncome(self):
        fica = tax_calculators.FicaTaxCalculator(self.family_noIncome, self.year, self.mock_tax_data)
        self.assertAlmostEqual(fica.calculate(), 0)

    def test_federal_fica_poor(self):
        fica = tax_calculators.FicaTaxCalculator(self.family_poor, self.year, self.mock_tax_data)
        self.assertAlmostEqual(fica.calculate(), 1300.5)

    def test_federal_fica_midClass(self):
        fica = tax_calculators.FicaTaxCalculator(self.family_midClass, self.year, self.mock_tax_data)
        self.assertAlmostEqual(fica.calculate(), 8774.9)

    def test_federal_fica_rich(self):
        fica = tax_calculators.FicaTaxCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(fica.calculate(), 17549.8)

class TestFederalIncomeTax(unittest.TestCase):
    def setUp(self):
        self.year = 2013
        self.p1 = people.Person("p1")
        self.p1.set_gross_income(self.year, 0)
        self.p1.set_healthcare_contribution(self.year, 0)
        self.p1.set_retirement_contribution_rate(self.year, 0)

        self.p2 = people.Person("p2")
        self.p2.set_gross_income(self.year, 0)
        self.p2.set_healthcare_contribution(self.year, 0)
        self.p2.set_retirement_contribution_rate(self.year, 0)

        self.p3 = people.Person("p3")
        self.p3.set_gross_income(self.year, 17000)
        self.p3.set_healthcare_contribution(self.year, 0)
        self.p3.set_retirement_contribution_rate(self.year, 0)

        self.p4 = people.Person("p4")
        self.p4.set_gross_income(self.year, 120000)
        self.p4.set_healthcare_contribution(self.year, 0)
        self.p4.set_retirement_contribution_rate(self.year, 0)

        self.p5 = people.Person("p5")
        self.p5.set_gross_income(self.year, 120000)
        self.p5.set_healthcare_contribution(self.year, 0)
        self.p5.set_retirement_contribution_rate(self.year, 0)

        self.family_noIncome = people.Family((self.p1, self.p2), data.FilingStatus.MARRIED_JOINT)
        self.family_poor =     people.Family((self.p1, self.p3), data.FilingStatus.MARRIED_JOINT)
        self.family_midClass = people.Family((self.p1, self.p4), data.FilingStatus.MARRIED_JOINT)
        self.family_rich =     people.Family((self.p4, self.p5), data.FilingStatus.MARRIED_JOINT)

        self.mock_tax_data = MockFederalTaxData(self.year, data.FilingStatus.MARRIED_JOINT)

    def tearDown(self):
        pass

    def test_federal_agi_noIncome(self):
        agi_calculator = tax_calculators.FederalAgiCalculator(self.family_noIncome, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 0)

    def test_federal_agi_poor(self):
        agi_calculator = tax_calculators.FederalAgiCalculator(self.family_poor, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 0)

    def test_federal_agi_midClass(self):
        agi_calculator = tax_calculators.FederalAgiCalculator(self.family_midClass, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 100000)

    def test_federal_agi_rich(self):
        agi_calculator = tax_calculators.FederalAgiCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 220000)

    def test_federal_agi_rich_with_retirement(self):
        self.p4.set_retirement_contribution_rate(self.year, 0.05)
        agi_calculator = tax_calculators.FederalAgiCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 214000, -1)

    def test_federal_agi_rich_with_retirement_and_healthcare(self):
        self.p4.set_retirement_contribution_rate(self.year, 0.05)
        self.p4.set_healthcare_contribution(self.year, 1000)
        agi_calculator = tax_calculators.FederalAgiCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 213000, -1)


    def test_federal_income_tax_noIncome(self):
        federal_income_tax_calculator = tax_calculators.FederalIncomeTaxCalculator(self.family_noIncome, self.year, self.mock_tax_data)
        self.assertAlmostEqual(federal_income_tax_calculator.calculate(), 0)

    def test_federal_income_tax_poor(self):
        federal_income_tax_calculator = tax_calculators.FederalIncomeTaxCalculator(self.family_poor, self.year, self.mock_tax_data)
        self.assertAlmostEqual(federal_income_tax_calculator.calculate(), 0)

    def test_federal_income_tax_midClass(self):
        federal_income_tax_calculator = tax_calculators.FederalIncomeTaxCalculator(self.family_midClass, self.year, self.mock_tax_data)
        self.assertAlmostEqual(federal_income_tax_calculator.calculate(), 16860, -2)

    def test_federal_income_tax_rich(self):
        federal_income_tax_calculator = tax_calculators.FederalIncomeTaxCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(federal_income_tax_calculator.calculate(), 49070, -2)

    def test_federal_income_tax_rich_with_retirement(self):
        self.p4.set_retirement_contribution_rate(self.year, 0.05)
        self.p4.set_healthcare_contribution(self.year, 1000)
        federal_income_tax_calculator = tax_calculators.FederalIncomeTaxCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(federal_income_tax_calculator.calculate(), 47110, -1)

class TestStateAgiCalculator(unittest.TestCase):
    def setUp(self):
        self.year = 2013
        self.p1 = people.Person("p1")
        self.p1.set_gross_income(self.year, 0)
        self.p1.set_healthcare_contribution(self.year, 0)
        self.p1.set_retirement_contribution_rate(self.year, 0)

        self.p2 = people.Person("p2")
        self.p2.set_gross_income(self.year, 0)
        self.p2.set_healthcare_contribution(self.year, 0)
        self.p2.set_retirement_contribution_rate(self.year, 0)

        self.p3 = people.Person("p3")
        self.p3.set_gross_income(self.year, 17000)
        self.p3.set_healthcare_contribution(self.year, 0)
        self.p3.set_retirement_contribution_rate(self.year, 0)

        self.p4 = people.Person("p4")
        self.p4.set_gross_income(self.year, 120000)
        self.p4.set_healthcare_contribution(self.year, 0)
        self.p4.set_retirement_contribution_rate(self.year, 0)

        self.p5 = people.Person("p5")
        self.p5.set_gross_income(self.year, 120000)
        self.p5.set_healthcare_contribution(self.year, 0)
        self.p5.set_retirement_contribution_rate(self.year, 0)

        self.family_noIncome = people.Family((self.p1, self.p2), data.FilingStatus.MARRIED_JOINT)
        self.family_poor =     people.Family((self.p1, self.p3), data.FilingStatus.MARRIED_JOINT)
        self.family_midClass = people.Family((self.p1, self.p4), data.FilingStatus.MARRIED_JOINT)
        self.family_rich =     people.Family((self.p4, self.p5), data.FilingStatus.MARRIED_JOINT)

        self.mock_tax_data = MockStateTaxData('MockState', self.year, data.FilingStatus.MARRIED_JOINT)

    def tearDown(self):
        pass

    def test_state_agi_noIncome(self):
        agi_calculator = tax_calculators.StateAgiCalculator(self.family_noIncome, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 0, -1)

    def test_state_agi_poor(self):
        agi_calculator = tax_calculators.StateAgiCalculator(self.family_poor, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 8600, -1)

    def test_state_agi_midClass(self):
        agi_calculator = tax_calculators.StateAgiCalculator(self.family_midClass, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 111600, -1)

    def test_state_agi_rich(self):
        agi_calculator = tax_calculators.StateAgiCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 231600, -1)

    def test_state_agi_rich_with_retirement(self):
        self.p4.set_retirement_contribution_rate(self.year, 0.05)
        agi_calculator = tax_calculators.StateAgiCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 225600, -1)

    def test_state_agi_rich_with_retirement_and_healthcare(self):
        self.p4.set_retirement_contribution_rate(self.year, 0.05)
        self.p4.set_healthcare_contribution(self.year, 1000)
        agi_calculator = tax_calculators.StateAgiCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(agi_calculator.calculate(), 225600, -1)


    def test_state_income_tax_noIncome(self):
        income_tax_calculator = tax_calculators.StateIncomeTaxCalculator(self.family_noIncome, self.year, self.mock_tax_data)
        self.assertAlmostEqual(income_tax_calculator.calculate(), 0, -1)

    def test_state_income_tax_poor(self):
        income_tax_calculator = tax_calculators.StateIncomeTaxCalculator(self.family_poor, self.year, self.mock_tax_data)
        self.assertAlmostEqual(income_tax_calculator.calculate(), 270, -1)

    def test_state_income_tax_midClass(self):
        income_tax_calculator = tax_calculators.StateIncomeTaxCalculator(self.family_midClass, self.year, self.mock_tax_data)
        self.assertAlmostEqual(income_tax_calculator.calculate(), 6436, -1)

    def test_state_income_tax_rich(self):
        income_tax_calculator = tax_calculators.StateIncomeTaxCalculator(self.family_rich, self.year, self.mock_tax_data)
        self.assertAlmostEqual(income_tax_calculator.calculate(), 13636, -1)


class TestNetIncome(unittest.TestCase):

    class MockStateIncomeCalculator(tax_calculators.StateIncomeTaxCalculator):
        """ On the spreadsheet, we use a simple tax rate to determine state taxes,
        not the more correct tax brackets. Mock that here """
        def __init__(self, family, year, tax_data):
            super().__init__(family, year, tax_data)

        def calculate(self):
            return self.agi * 0.059

    def setUp(self):
        # from spreadsheet
        self.year = 2013

        april_day_shift = people.Person('april_day_shift')
        april_evening_shift = people.Person('april_evening_shift')
        sam_no_bonus = people.Person('sam_no_bonus')
        sam_below = people.Person('sam_below')
        sam_meets = people.Person('sam_meets')
        sam_exceeds = people.Person('sam_exceeds')

        for p in (april_evening_shift, april_day_shift):
            p.set_healthcare_contribution(self.year, 1690)
            p.set_retirement_contribution_rate(self.year, 0.06)

        for p in (sam_no_bonus, sam_below, sam_meets, sam_exceeds):
            p.set_healthcare_contribution(self.year, 1090)
            p.set_retirement_contribution_rate(self.year, 0.05)

        april_day_shift.set_gross_income(self.year, 99840)
        april_evening_shift.set_gross_income(self.year, 102340)
        sam_no_bonus.set_gross_income(self.year, 80000)
        sam_below.set_gross_income(self.year, 84000)
        sam_meets.set_gross_income(self.year, 88000)
        sam_exceeds.set_gross_income(self.year, 92000)

        self.f1 = people.Family((april_day_shift, sam_no_bonus), data.FilingStatus.MARRIED_JOINT, 'GA')
        self.f2 = people.Family((april_evening_shift, sam_no_bonus), data.FilingStatus.MARRIED_JOINT, 'GA')
        self.f3 = people.Family((april_evening_shift, sam_below), data.FilingStatus.MARRIED_JOINT, 'GA')
        self.f4 = people.Family((april_evening_shift, sam_meets), data.FilingStatus.MARRIED_JOINT, 'GA')
        self.f5 = people.Family((april_evening_shift, sam_exceeds), data.FilingStatus.MARRIED_JOINT, 'GA')

        self.mock_fed_tax_data = MockFederalTaxData(self.year, data.FilingStatus.MARRIED_JOINT)
        self.mock_state_tax_data = MockStateTaxData('GA', self.year, data.FilingStatus.MARRIED_JOINT)

    def tearDown(self):
        pass

    def get_mocked_net_income_calculator(self, family):
        fed_income_calc = tax_calculators.FederalIncomeTaxCalculator(family, self.year, self.mock_fed_tax_data)
        fica_calc = tax_calculators.FicaTaxCalculator(family, self.year, self.mock_fed_tax_data)
        state_income_calc = self.MockStateIncomeCalculator(family, self.year, self.mock_state_tax_data) # tax_calculators.StateIncomeTaxCalculator(family, self.year, self.mock_state_tax_data)

        tax_calculator = tax_calculators.TaxCalculator(family, self.year)
        tax_calculator.federal_income_tax_calculator = fed_income_calc
        tax_calculator.fica_tax_calculator = fica_calc
        tax_calculator.state_income_tax_calculator = state_income_calc

        net_income_calc = tax_calculators.NetIncomeCalculator(family, self.year)
        net_income_calc.tax_calculator = tax_calculator

        return net_income_calc

    def test_net_income(self):
        family = self.f1
        net_income_calc = self.get_mocked_net_income_calculator(family)
        self.assertAlmostEqual(net_income_calc.calculate(), 115180, -1)

        family = self.f2
        net_income_calc = self.get_mocked_net_income_calculator(family)
        self.assertAlmostEqual(net_income_calc.calculate(), 116540, -1)

        family = self.f3
        net_income_calc = self.get_mocked_net_income_calculator(family)
        self.assertAlmostEqual(net_income_calc.calculate(), 118746, -1)

        family = self.f4
        net_income_calc = self.get_mocked_net_income_calculator(family)
        self.assertAlmostEqual(net_income_calc.calculate(), 120952, -1)

        family = self.f5
        net_income_calc = self.get_mocked_net_income_calculator(family)
        self.assertAlmostEqual(net_income_calc.calculate(), 123158, -1)


if __name__ == '__main__':
    unittest.main()
