import unittest
from pprint import pprint

import common_loans
import month

# See  http://www.mlcalc.com

class TestStudentLoan(unittest.TestCase):
    def setUp(self):
        
        self.month = month.Month(2014,1,)
        self.amt = 130000
        self.apr = 0.065
        self.term = 10

        self.loan = common_loans.StudentLoan()
        self.loan.month = self.month
        self.loan.start_amount = self.amt
        self.loan.apr = self.apr

    def tearDown(self):
        pass

    def test_min_pmt(self):
        self.assertAlmostEqual(self.loan.minimum_payment, 1473.39, 2)
        #self.loan.calculate_amortization_table()

if __name__ == '__main__':
    unittest.main()