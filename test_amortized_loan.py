import unittest
from pprint import pprint

import amortized_loan

class TestAmortizedLoan(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_min_pmt(self):
		# tested against http://www.bankrate.com/calculators/mortgages/amortization-calculator.aspx
		amt = 200000
		term = 30
		api = 0.05
		loan = amortized_loan.AmortizedLoan(amt, term, api)

		self.assertAlmostEqual(loan.min_payment, 1073.64, 2)

		pprint(loan.calculate_amortization_table())

if __name__ == '__main__':
	unittest.main()