import unittest

import people
from data import FilingStatus

class TestPerson(unittest.TestCase):
    def setUp(self):
        self.p1 = people.Person("p1")
        self.p1.set_gross_income(2010, 0)
        self.p1.set_healthcare_contribution(2010, 0)
        self.p1.set_retirement_contribution_rate(2010, 0)

        self.p2 = people.Person("p2")
        self.p2.set_gross_income(2010, 0)
        self.p2.set_healthcare_contribution(2010, 0)
        self.p2.set_retirement_contribution_rate(2010, 0)

        self.p3 = people.Person("p3")
        self.p3.set_gross_income(2010, 17000)
        self.p3.set_healthcare_contribution(2010, 0)
        self.p3.set_retirement_contribution_rate(2010, 0.05)

        self.p4 = people.Person("p4")
        self.p4.set_gross_income(2010, 120000)
        self.p4.set_healthcare_contribution(2010, 1000)
        self.p4.set_retirement_contribution_rate(2010, 0.05)

        self.p5 = people.Person("p5")
        self.p5.set_gross_income(2010, 120000)
        self.p5.set_healthcare_contribution(2010, 1000)
        self.p5.set_retirement_contribution_rate(2010, 0.10)

    def tearDown(self):
        pass

    def test_income(self):
        self.assertEqual(self.p1.gross_income(2010), 0)
        self.assertEqual(self.p3.gross_income(2010), 17000)
        self.assertEqual(self.p4.gross_income(2010), 120000)

class TestFamily(unittest.TestCase):
    def setUp(self):
        self.p1 = people.Person("p1")
        self.p1.set_gross_income(2010, 0)
        self.p1.set_healthcare_contribution(2010, 0)
        self.p1.set_retirement_contribution_rate(2010, 0)

        self.p2 = people.Person("p2")
        self.p2.set_gross_income(2010, 0)
        self.p2.set_healthcare_contribution(2010, 0)
        self.p2.set_retirement_contribution_rate(2010, 0)

        self.p3 = people.Person("p3")
        self.p3.set_gross_income(2010, 17000)
        self.p3.set_healthcare_contribution(2010, 0)
        self.p3.set_retirement_contribution_rate(2010, 0.05)

        self.p4 = people.Person("p4")
        self.p4.set_gross_income(2010, 120000)
        self.p4.set_healthcare_contribution(2010, 1000)
        self.p4.set_retirement_contribution_rate(2010, 0.05)

        self.p5 = people.Person("p5")
        self.p5.set_gross_income(2010, 120000)
        self.p5.set_healthcare_contribution(2010, 1000)
        self.p5.set_retirement_contribution_rate(2010, 0.10)

        self.family_noIncome = people.Family((self.p1, self.p2), FilingStatus.MARRIED_JOINT)
        self.family_poor =     people.Family((self.p1, self.p3), FilingStatus.MARRIED_JOINT)
        self.family_midClass = people.Family((self.p1, self.p4), FilingStatus.MARRIED_JOINT)
        self.family_rich =     people.Family((self.p4, self.p5), FilingStatus.MARRIED_JOINT)

    def tearDown(self):
        pass

    def test_gross_income(self):
        self.assertEqual(self.family_noIncome.gross_income(2010), 0)
        self.assertEqual(self.family_poor.gross_income(2010), 17000)
        self.assertEqual(self.family_midClass.gross_income(2010), 120000)
        self.assertEqual(self.family_rich.gross_income(2010), 240000)

    def test_healthcare_contribution(self):
        self.assertEqual(self.family_noIncome.healthcare_contribution(2010), 0)
        self.assertEqual(self.family_poor.healthcare_contribution(2010), 0)
        self.assertEqual(self.family_midClass.healthcare_contribution(2010), 1000)
        self.assertEqual(self.family_rich.healthcare_contribution(2010), 2000)

    def test_retirement_contribution(self):
        self.assertEqual(self.family_noIncome.retirement_contribution(2010), 0)
        self.assertEqual(self.family_poor.retirement_contribution(2010), 850)
        self.assertEqual(self.family_midClass.retirement_contribution(2010), 6000)
        self.assertEqual(self.family_rich.retirement_contribution(2010), 18000)

        p1 = people.Person('p1')
        p1.set_gross_income(2013, 99840)
        p1.set_retirement_contribution_rate(2013, .06)
        p2 = people.Person('p2')
        p2.set_gross_income(2013, 80000)
        p2.set_retirement_contribution_rate(2013, .05)
        f = people.Family((p1, p2), FilingStatus.MARRIED_JOINT)
        self.assertAlmostEqual(f.retirement_contribution(2013), 9990, -1)

    def test_itemized_deductions(self):
        self.assertEqual(self.family_noIncome.itemized_deductions(2010), 0)
        
        d = people.Deduction('mortgage', 100)
        self.family_noIncome.add_deduction(2010, d)
        self.family_noIncome.add_deduction(2010, d)
        self.family_noIncome.add_deduction(2011, d)

        self.assertEqual(self.family_noIncome.itemized_deductions(2010), 200)
        self.assertEqual(self.family_noIncome.itemized_deductions(2011), 100)
        self.assertEqual(self.family_noIncome.itemized_deductions(2012), 0)

if __name__ == '__main__':
    unittest.main()
