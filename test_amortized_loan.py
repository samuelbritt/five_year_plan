import unittest
from pprint import pprint

import amortized_loan
import month

class TestAmortizedLoan(unittest.TestCase):
	def setUp(self):
		# http://www.mlcalc.com
		self.amt = 200000
		self.term = 30
		self.apr = 0.05
		start_month = month.Month(2014, 1)
		cmpd_type = amortized_loan.CompoundType.MONTHLY
		self.loan = amortized_loan.AmortizedLoan(self.amt, self.term, self.apr,
		                                         start_month=start_month,
		                                         compound_type=cmpd_type)

	def tearDown(self):
		pass

	def test_min_pmt(self):
		self.assertAlmostEqual(self.loan.minimum_payment, 1073.64, 2)

	def test_final_results(self):
		self.assertEqual(self.loan.last_payment_month, None)
		self.assertAlmostEqual(self.loan.remaining_balance, self.amt)
		self.assertAlmostEqual(self.loan.total_interest_paid(), 0, 2)

		payments = self.loan.calculate_amortization_table()

		self.assertEqual(self.loan.last_payment_month, month.Month(2043, 12))
		self.assertAlmostEqual(self.loan.remaining_balance, 0)
		self.assertAlmostEqual(self.loan.total_interest_paid(), 186511.57, 2)
		self.assertAlmostEqual(self.loan.total_interest_paid(2014), 9932.99, 2)
		self.assertAlmostEqual(self.loan.total_interest_paid(2015), 9782.02, 2)
		self.assertAlmostEqual(self.loan.total_interest_paid(2043), 342.25, 2)

	def test_first_payment(self):
		payments = self.loan.calculate_amortization_table()
		self.assertEqual(payments[0].month, month.Month(2014, 1))
		self.assertAlmostEqual(payments[0].interest_amount, 833.33, 2)
		self.assertAlmostEqual(payments[0].principle_amount, 240.31, 2)

	def test_last_payment(self):
		payments = self.loan.calculate_amortization_table()
		self.assertEqual(payments[-1].month, month.Month(2043, 12))
		self.assertEqual(self.loan.last_payment_month, month.Month(2043, 12))
		self.assertAlmostEqual(payments[-1].interest_amount, 4.45, 2)
		self.assertAlmostEqual(payments[-1].principle_amount, 1069.19, 2)

	def test_table(self):
		return
		pprint(loan.calculate_amortization_table())


if __name__ == '__main__':
	unittest.main()