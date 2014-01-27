import unittest
from pprint import pprint

import month
import savings_goals as s

class TestSavingsPlan(unittest.TestCase):
    def setUp(self):

        self.car1 = s.SavingsGoal('car 1',   6000, month.Month(2015, 10))
        self.car2 = s.SavingsGoal('car 2',  30000, month.Month(2015, 12))
        self.house = s.SavingsGoal('house', 60000, month.Month(2015,  6))

    def tearDown(self):
        pass

    def create_amount_available(self, monthly_income):
        max_month = month.Month(2015, 12)
        min_month = month.Month(2014, 1)
        amount_available = {}
        
        this_month = min_month
        while this_month <= max_month:
            amount_available[this_month] = monthly_income
            this_month = this_month.monthadd(1)
        return amount_available


    def test_plan(self):
        amount_available = self.create_amount_available(6000)
        # pprint (amount_available)

        goals = s.SavingsGoals()
        goals.add_goal(self.car1)
        goals.add_goal(self.car2)
        p = goals.calculate_savings_plan(amount_available)
        print()
        pprint (p)


if __name__ == '__main__':
    unittest.main()