from unittest import TestCase

from Source.Market import Stock, Market


class TestMarket(TestCase):
    def test_check_current_value(self):
        test_market = Market([Stock('stock_test_1', 100, 0, 0), Stock('stock_test_2', 101, 0, 0)])

        # test creation of Stock
        self.assertIn('stock_test_1', test_market._financial_product_dict)
        self.assertIn('stock_test_2', test_market._financial_product_dict)

        self.assertEqual(100, test_market.check_value('stock_test_1'))
        self.assertEqual(101, test_market.check_value('stock_test_2'))

        test_market.evolve()
        self.assertEqual(100, test_market.check_value('stock_test_1'))
        self.assertEqual(101, test_market.check_value('stock_test_2'))


class TestStock(TestCase):
    def test_evolve(self):
        stock_test = Stock('stock_test', 100, 0, 0)

        # test creation of Stock
        self.assertEqual('stock_test', stock_test.name)
        self.assertEqual(100, stock_test.check_value())

        # test evolve of Stock
        stock_test.evolve()
        # we set mu = 0, sigma = 0 in stock noise, so the stock price is the same after evolution.
        self.assertAlmostEqual(100, stock_test.check_value(), delta=1e-6)


