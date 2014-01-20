import unittest
import datetime

import home


class TestMortgageZeroDown(unittest.TestCase):
    def setUp(self):
        
        self.purchase_date = datetime.date(2014,1,1)
        self.amt = 200000
        self.apr = 0.05
        self.term = 30
        self.pmi_rate = 0.01
        self.down_payment_percent = 0.0

        self.loan = home.Home()
        self.loan.purchase_date = self.purchase_date
        self.loan.purchase_amount = self.amt
        self.loan.apr = self.apr
        self.loan.down_payment_percent = self.down_payment_percent
        self.loan.term_in_years = self.term
        self.loan.pmi_rate = self.pmi_rate

    def tearDown(self):
        pass

    def test_min_pmt(self):
        self.assertAlmostEqual(self.loan.minimum_payment, 1073.64, 2)

    def test_pmi_payment(self):
        self.assertAlmostEqual(self.loan.pmi_payment, 166.67, 2)

    def test_final_results(self):
        self.assertEqual(self.loan.last_payment_date, None)
        self.assertAlmostEqual(self.loan.remaining_balance, self.amt)
        self.assertAlmostEqual(self.loan.total_interest_paid(), 0, 2)
        self.assertAlmostEqual(self.loan.total_pmi_paid, 0, 2)

        payments = self.loan.calculate_amortization_table()

        self.assertEqual(self.loan.last_payment_date, datetime.date(2043, 12, 1))
        self.assertAlmostEqual(self.loan.remaining_balance, 0)
        self.assertAlmostEqual(self.loan.total_pmi_paid, 21166.67, 2)
        self.assertAlmostEqual(self.loan.total_interest_paid(), 186511.57, 2)
        self.assertAlmostEqual(self.loan.total_interest_paid(2014), 9932.99, 2)
        self.assertAlmostEqual(self.loan.total_interest_paid(2015), 9782.02, 2)
        self.assertAlmostEqual(self.loan.total_interest_paid(2043), 342.25, 2)

    def test_first_payment(self):
        payments = self.loan.calculate_amortization_table()
        self.assertEqual(payments[0].date, datetime.date(2014, 1, 1))
        self.assertAlmostEqual(payments[0].interest_amount, 833.33, 2)
        self.assertAlmostEqual(payments[0].principle_amount, 240.31, 2)
        self.assertAlmostEqual(payments[0].pmi_amount, 166.67, 2)

    def test_last_payment(self):
        payments = self.loan.calculate_amortization_table()
        self.assertEqual(payments[-1].date, datetime.date(2043, 12, 1))
        self.assertEqual(self.loan.last_payment_date, datetime.date(2043, 12, 1))
        self.assertAlmostEqual(payments[-1].interest_amount, 4.45, 2)
        self.assertAlmostEqual(payments[-1].principle_amount, 1069.19, 2)
        self.assertAlmostEqual(payments[-1].pmi_amount, 0, 2)

    def test_table(self):
        return
        pprint(self.loan.calculate_amortization_table())


class TestMortgage30Down(unittest.TestCase):
    def setUp(self):
        self.purchase_date = datetime.date(2014,1,1)
        self.amt = 200000
        self.apr = 0.05
        self.term = 30
        self.pmi_rate = 0.01
        self.down_payment_percent = 0.30

        self.loan = home.Home()
        self.loan.purchase_date = self.purchase_date
        self.loan.purchase_amount = self.amt
        self.loan.apr = self.apr
        self.loan.down_payment_percent = self.down_payment_percent
        self.loan.term_in_years = self.term
        self.loan.pmi_rate = self.pmi_rate


    def tearDown(self):
        pass

    def test_min_pmt(self):
        self.assertAlmostEqual(self.loan.minimum_payment, 751.55, 2)

    def test_pmi_payment(self):
        self.assertAlmostEqual(self.loan.pmi_payment, 0, 2)

    def test_final_results(self):
        self.assertEqual(self.loan.last_payment_date, None)
        self.assertAlmostEqual(self.loan.remaining_balance, 140000)
        self.assertAlmostEqual(self.loan.total_interest_paid(), 0, 2)
        self.assertAlmostEqual(self.loan.total_pmi_paid, 0, 2)

        payments = self.loan.calculate_amortization_table()

        self.assertEqual(self.loan.last_payment_date, datetime.date(2043, 12, 1))
        self.assertAlmostEqual(self.loan.remaining_balance, 0)
        self.assertAlmostEqual(self.loan.total_pmi_paid, 0, 2)
        self.assertAlmostEqual(self.loan.total_interest_paid(), 130558.10, 2)
        self.assertAlmostEqual(self.loan.total_interest_paid(2014), 6953.09, 2)
        self.assertAlmostEqual(self.loan.total_interest_paid(2015), 6847.42, 2)
        self.assertAlmostEqual(self.loan.total_interest_paid(2043), 239.58, 2)

    def test_first_payment(self):
        payments = self.loan.calculate_amortization_table()
        self.assertEqual(payments[0].date, datetime.date(2014, 1, 1))
        self.assertAlmostEqual(payments[0].interest_amount, 583.33, 2)
        self.assertAlmostEqual(payments[0].principle_amount, 168.22, 2)
        self.assertAlmostEqual(payments[0].pmi_amount, 0, 2)

    def test_last_payment(self):
        payments = self.loan.calculate_amortization_table()
        self.assertEqual(payments[-1].date, datetime.date(2043, 12, 1))
        self.assertEqual(self.loan.last_payment_date, datetime.date(2043, 12, 1))
        self.assertAlmostEqual(payments[-1].interest_amount, 3.12, 2)
        self.assertAlmostEqual(payments[-1].principle_amount, 748.43, 2)
        self.assertAlmostEqual(payments[-1].pmi_amount, 0, 2)

    def test_table(self):
        return
        pprint(self.loan.calculate_amortization_table())

if __name__ == '__main__':
    unittest.main()