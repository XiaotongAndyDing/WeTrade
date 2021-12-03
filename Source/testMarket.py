from unittest import TestCase

from Source.Market import Stock, Cash


class TestStock(TestCase):
    def test_evolve(self):
        stock_test = Stock('stock_test', 100, 0, 0)

        # test creation of Stock
        self.assertEqual('stock_test', stock_test._name)
        self.assertEqual(100, stock_test.check_value())

        # test evolve of Stock
        stock_test.evolve()
        # we set mu = 0, sigma = 0 in stock noise, so the stock price is the same after evolution.
        self.assertAlmostEqual(100, stock_test.check_value(), delta=1e-6)


class TestCash(TestCase):
    def test_evolve(self):
        cash_test = Cash(1000)

        # test creation of Cash
        self.assertEqual('Cash', cash_test._name)
        self.assertEqual(1000, cash_test.check_value())

        # test evolve of Cash
        cash_test.evolve()
        self.assertEqual(1000, cash_test.check_value())

