import unittest
import datetime
from pprint import pprint

import amortized_loan

class TestAmortizedLoan(unittest.TestCase):
	def setUp(self):
		# tested against http://www.bankrate.com/calculators/mortgages/amortization-calculator.aspx
		# and http://www.mortgagecalculator.org/
		amt = 200000
		term = 30
		api = 0.05
		start_date = datetime.date(2014,1,1)
		cmpd_type = amortized_loan.CompoundType.MONTHLY
		self.loan = amortized_loan.AmortizedLoan(amt, term, api, start_date=start_date, compound_type=cmpd_type)

	def tearDown(self):
		pass

	def test_min_pmt(self):
		self.assertAlmostEqual(self.loan.min_payment, 1073.64, 2)

	def test_final_results(self):
		payments = self.loan.calculate_amortization_table()
		self.assertAlmostEqual(self.loan.remaining_balance, 0)
		self.assertAlmostEqual(self.loan.total_interest_paid, 186511.57, 2)

	def test_first_payment(self):
		payments = self.loan.calculate_amortization_table()
		self.assertEqual(payments[0].date, datetime.date(2014, 2, 1))
		self.assertAlmostEqual(payments[0].interest_amount, 833.33, 2)
		self.assertAlmostEqual(payments[0].principle_amount, 240.31, 2)

	def test_last_payment(self):
		payments = self.loan.calculate_amortization_table()
		self.assertEqual(payments[-1].date, datetime.date(2044, 1, 1))
		self.assertAlmostEqual(payments[-1].interest_amount, 4.45, 2)
		self.assertAlmostEqual(payments[-1].principle_amount, 1069.19, 2)

	def test_table(self):
		# pprint(loan.calculate_amortization_table())
		pass


if __name__ == '__main__':
	unittest.main()