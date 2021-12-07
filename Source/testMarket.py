from unittest import TestCase
import numpy as np
from Source.Market import Stock, Market, StockGeometricBrownianMotion, StockMeanRevertingGeometricBrownianMotion


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

    def test_mark_current_value_to_record(self):
        test_market = Market([Stock('stock_test_1', 100, 1, 0), Stock('stock_test_2', 101, 2, 0)])
        test_market.mark_current_value_to_record(0)
        self.assertEqual(1, len(test_market._financial_product_dict['stock_test_1'].price_record))
        self.assertEqual(100, test_market._financial_product_dict['stock_test_1'].price_record[0])
        self.assertEqual(1, len(test_market._financial_product_dict['stock_test_2'].price_record))
        self.assertEqual(101, test_market._financial_product_dict['stock_test_2'].price_record[0])

        test_market.evolve()
        test_market.mark_current_value_to_record(1)
        self.assertEqual(2, len(test_market._financial_product_dict['stock_test_1'].price_record))
        self.assertEqual(100 + 1, test_market._financial_product_dict['stock_test_1'].price_record[1])
        self.assertEqual(2, len(test_market._financial_product_dict['stock_test_2'].price_record))
        self.assertEqual(101 + 2, test_market._financial_product_dict['stock_test_2'].price_record[1])


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

        stock_test = Stock('stock_test', 100, 1, 0)
        stock_test.evolve()
        self.assertAlmostEqual(101, stock_test.check_value(), delta=1e-6)

    def test_mark_current_value_to_record(self):
        stock_test = Stock('stock_test', 100, 1, 0)
        stock_test.mark_current_value_to_record(0)

        self.assertEqual(1, len(stock_test.price_record))
        self.assertEqual(100, stock_test.price_record[0])

        stock_test.evolve()
        stock_test.mark_current_value_to_record(1)
        self.assertEqual(2, len(stock_test.price_record))
        self.assertEqual(100, stock_test.price_record[0])
        self.assertEqual(101, stock_test.price_record[1])


class TestStockGeometricBrownianMotion(TestCase):
    def test_evolve(self):
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 0)
        stock_test.evolve()
        self.assertAlmostEqual(100, stock_test.check_value(), delta=1e-6)

        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0.01, 0)
        stock_test.evolve()
        self.assertAlmostEqual(100 * np.exp(0.01), stock_test.check_value(), delta=1e-6)

        stock_test._mu = 0.05
        stock_test.evolve()
        self.assertAlmostEqual(100 * np.exp(0.01) * np.exp(0.05), stock_test.check_value(), delta=1e-6)


class TestStockMeanRevertingGeometricBrownianMotion(TestCase):
    def test_evolve(self):
        stock_test = StockMeanRevertingGeometricBrownianMotion('stock_mr_gbm_test', 100, 0, 0,
                                                               equilibrium_price=100, mean_reversion_speed=0)
        stock_test.evolve()
        self.assertAlmostEqual(100, stock_test.check_value(), delta=1e-6)

        stock_test = StockMeanRevertingGeometricBrownianMotion('stock_mr_gbm_test', 200, 0, 0,
                                                               equilibrium_price=100, mean_reversion_speed=0.001)

        # initial stock price is higher than the equilibrium price. After long time, stock price is very close to the
        # equilibrium price
        for _ in range(100):
            stock_test.evolve()
        self.assertAlmostEqual(100, stock_test.check_value(), delta=0.01)

        stock_test = StockMeanRevertingGeometricBrownianMotion('stock_mr_gbm_test', 50, 0, 0,
                                                               equilibrium_price=100, mean_reversion_speed=0.001)

        # initial stock price is lower than the equilibrium price. After long time, stock price is very close to the
        # equilibrium price
        for _ in range(100):
            stock_test.evolve()
        self.assertAlmostEqual(100, stock_test.check_value(), delta=0.01)

