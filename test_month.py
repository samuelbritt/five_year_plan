import unittest
from datetime import date

import month

class TestMonth(unittest.TestCase):
    def setUp(self):

        self.m1 = month.Month(2014, 1)
        self.m2 = month.Month(2015, 3)

        # Tested in sql server:
        # DECLARE @d1 date = '2014-1-25'
        # DECLARE @d2 date = '2015-3-20'
        # DECLARE @m1 date = dateadd(month, datediff(month, 0, @d1), 0)
        # DECLARE @m2 date = dateadd(month, datediff(month, 0, @d2), 0)
        # SELECT @m1, @m2
        # select datediff(year, @m1, @m2), datediff(year, @m2, @m1)
        # select datediff(month, @m1, @m2), datediff(month, @m2, @m1)
        # select datediff(day, @m1, @m2), datediff(day, @m2, @m1)
        # ---------- ----------
        # 2014-01-01 2015-03-01
        # 1           -1
        # 14          -14
        # 424         -424

    def tearDown(self):
        pass

    def test_fromdate(self):
        d1 = date(2015, 3, 1)
        d2 = date(2015, 3, 20)

        self.assertEqual(month.Month.fromdate(d1), self.m2)
        self.assertEqual(month.Month.fromdate(d2), self.m2)

    def test_datediff_year(self):
        part = month.DatePart.YEAR

        diff = self.m1.datediff(part, self.m1)
        self.assertEqual(diff, 0)
        diff = self.m1.datediff(part, self.m2)
        self.assertEqual(diff, 1)
        diff = self.m2.datediff(part, self.m1)
        self.assertEqual(diff, -1)
    
    def test_datediff_month(self):
        part = month.DatePart.MONTH

        diff = self.m1.datediff(part, self.m1)
        self.assertEqual(diff, 0)
        diff = self.m1.datediff(part, self.m2)
        self.assertEqual(diff, 14)
        diff = self.m2.datediff(part, self.m1)
        self.assertEqual(diff, -14)

    def test_datediff_day(self):
        part = month.DatePart.DAY

        diff = self.m1.datediff(part, self.m1)
        self.assertEqual(diff, 0)
        diff = self.m1.datediff(part, self.m2)
        self.assertEqual(diff, 424)
        diff = self.m2.datediff(part, self.m1)
        self.assertEqual(diff, -424)

    def test_monthadd(self):
        self.assertEqual(self.m1.monthadd(14), self.m2)
        self.assertEqual(self.m2.monthadd(-14), self.m1)

    def test_cmp(self):
        self.assertTrue(self.m1 != self.m2)
        self.assertTrue(self.m1 < self.m2)
        self.assertTrue(self.m1 <= self.m2)
        self.assertTrue(self.m2 > self.m1)
        self.assertTrue(self.m2 >= self.m1)
        self.assertFalse(self.m1 == self.m2)
        self.assertFalse(self.m1 > self.m2)


if __name__ == '__main__':
    unittest.main()