from unittest import TestCase
import numpy as np
from Source.Market import Stock, Market, StockGeometricBrownianMotion, StockMeanRevertingGeometricBrownianMotion, \
    Derivative, Option, EuropeanCallOption, EuropeanPutOption


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

        stock_test.mu = 0.05
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


class TestDerivative(TestCase):
    def test_init(self):
        stock_test_1 = StockGeometricBrownianMotion('stock_gbm_test_1', 100, 0, 0)
        stock_test_2 = StockGeometricBrownianMotion('stock_gbm_test_2', 101, 0, 0)
        derivative_test = Derivative('derivative_test', [stock_test_1, stock_test_2])
        self.assertEqual(2, len(derivative_test.underlyings))
        self.assertEqual(100, derivative_test.underlyings[0].current_value)
        self.assertEqual(101, derivative_test.underlyings[1].current_value)


class TestOption(TestCase):
    def test_init(self):
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 0)
        option_test = Option('option_test', [stock_test], 110, 10)
        self.assertEqual(110, option_test.strike)
        self.assertEqual(10, option_test.expiry)
        self.assertEqual(100, option_test.underlying.current_value)


class TestEuropeanCallOption(TestCase):
    def test_evolve(self):
        # Limit Case: Deep ITM Option, Stock Volatility is very small.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1e-6)
        option_test = EuropeanCallOption('option_test', [stock_test], 90, 10)

        self.assertAlmostEqual(10, option_test.current_value, delta=1e-6)
        self.assertAlmostEqual(1, option_test.delta, delta=1e-6)
        self.assertAlmostEqual(0, option_test.gamma, delta=1e-6)
        self.assertAlmostEqual(0, option_test.vega, delta=1e-6)

        # Limit Case: Deep OTM Option, Stock Volatility is very small.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1e-6)
        option_test = EuropeanCallOption('option_test', [stock_test], 110, 10)

        self.assertAlmostEqual(0, option_test.current_value, delta=1e-6)
        self.assertAlmostEqual(0, option_test.delta, delta=1e-6)
        self.assertAlmostEqual(0, option_test.gamma, delta=1e-6)
        self.assertAlmostEqual(0, option_test.vega, delta=1e-6)

        # Limit Case: Option, Stock Volatility is very large.
        # you can win inf, with floored loss. So the price of the option is simply the price of stock, no matter strike
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1e6)
        option_test = EuropeanCallOption('option_test', [stock_test], 90, 10)

        self.assertAlmostEqual(100, option_test.current_value, delta=1e-6)
        self.assertAlmostEqual(1, option_test.delta, delta=1e-6)
        self.assertAlmostEqual(0, option_test.gamma, delta=1e-6)
        self.assertAlmostEqual(0, option_test.vega, delta=1e-6)

        # Limit Case: Already Expire.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1e-6)
        option_test = EuropeanCallOption('option_test', [stock_test], 110, 0)
        self.assertAlmostEqual(0, option_test.current_value, delta=1e-6)
        option_test = EuropeanCallOption('option_test', [stock_test], 90, 0)
        self.assertAlmostEqual(10, option_test.current_value, delta=1e-6)

        # Normal Case: ATM.
        # Online Option Price Calculator: https://goodcalculators.com/black-scholes-calculator/
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1 / np.sqrt(252))
        option_test = EuropeanCallOption('option_test', [stock_test], 100, 252)  # 252 business days per year

        self.assertAlmostEqual(38.292, option_test.current_value, delta=0.001)
        self.assertAlmostEqual(0.691, option_test.delta, delta=0.001)
        self.assertAlmostEqual(0.004, option_test.gamma, delta=0.001)
        self.assertAlmostEqual(35.207, option_test.vega, delta=0.001)

        # Normal Case: ITM.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1 / np.sqrt(252))
        option_test = EuropeanCallOption('option_test', [stock_test], 90, 252)  # 252 business days per year

        self.assertAlmostEqual(41.563, option_test.current_value, delta=0.001)
        self.assertAlmostEqual(0.728, option_test.delta, delta=0.001)
        self.assertAlmostEqual(0.004, option_test.gamma, delta=0.001)
        self.assertAlmostEqual(33.215, option_test.vega, delta=0.001)

        # Normal Case: OTM.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1 / np.sqrt(252))
        option_test = EuropeanCallOption('option_test', [stock_test], 110, 252)  # 252 business days per year

        self.assertAlmostEqual(35.375, option_test.current_value, delta=0.001)
        self.assertAlmostEqual(0.657, option_test.delta, delta=0.001)
        self.assertAlmostEqual(0.004, option_test.gamma, delta=0.001)
        self.assertAlmostEqual(36.758, option_test.vega, delta=0.001)


class TestEuropeanPutOption(TestCase):
    def test_evolve(self):
        # Limit Case: Deep OTM Option, Stock Volatility is very small.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1e-6)
        option_test = EuropeanPutOption('option_test', [stock_test], 90, 10)

        self.assertAlmostEqual(0, option_test.current_value, delta=1e-6)
        self.assertAlmostEqual(0, option_test.delta, delta=1e-6)
        self.assertAlmostEqual(0, option_test.gamma, delta=1e-6)
        self.assertAlmostEqual(0, option_test.vega, delta=1e-6)

        # Limit Case: Deep OTM Option, Stock Volatility is very small.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1e-6)
        option_test = EuropeanPutOption('option_test', [stock_test], 110, 10)

        self.assertAlmostEqual(10, option_test.current_value, delta=1e-6)
        self.assertAlmostEqual(-1, option_test.delta, delta=1e-6)
        self.assertAlmostEqual(0, option_test.gamma, delta=1e-6)
        self.assertAlmostEqual(0, option_test.vega, delta=1e-6)

        # Limit Case: Option, Stock Volatility is very large.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1e6)
        option_test = EuropeanPutOption('option_test', [stock_test], 110, 10)

        self.assertAlmostEqual(110, option_test.current_value, delta=1e-6)
        self.assertAlmostEqual(0, option_test.delta, delta=1e-6)
        self.assertAlmostEqual(0, option_test.gamma, delta=1e-6)
        self.assertAlmostEqual(0, option_test.vega, delta=1e-6)

        # Limit Case: Already Expire.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1e-6)
        option_test = EuropeanPutOption('option_test', [stock_test], 110, 0)
        self.assertAlmostEqual(10, option_test.current_value, delta=1e-6)
        option_test = EuropeanPutOption('option_test', [stock_test], 90, 0)
        self.assertAlmostEqual(0, option_test.current_value, delta=1e-6)

        # Normal Case: ATM.
        # Online Option Price Calculator: https://goodcalculators.com/black-scholes-calculator/
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1 / np.sqrt(252))
        option_test = EuropeanPutOption('option_test', [stock_test], 100, 252)  # 252 business days per year

        self.assertAlmostEqual(38.292, option_test.current_value, delta=0.001)
        self.assertAlmostEqual(-0.309, option_test.delta, delta=0.001)
        self.assertAlmostEqual(0.004, option_test.gamma, delta=0.001)
        self.assertAlmostEqual(35.207, option_test.vega, delta=0.001)

        # Normal Case: ITM.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1 / np.sqrt(252))
        option_test = EuropeanPutOption('option_test', [stock_test], 110, 252)  # 252 business days per year

        self.assertAlmostEqual(45.375, option_test.current_value, delta=0.001)
        self.assertAlmostEqual(-0.343, option_test.delta, delta=0.001)
        self.assertAlmostEqual(0.004, option_test.gamma, delta=0.001)
        self.assertAlmostEqual(36.758, option_test.vega, delta=0.001)

        # Normal Case: OTM.
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1 / np.sqrt(252))
        option_test = EuropeanPutOption('option_test', [stock_test], 90, 252)  # 252 business days per year

        self.assertAlmostEqual(31.563, option_test.current_value, delta=0.001)
        self.assertAlmostEqual(-0.272, option_test.delta, delta=0.001)
        self.assertAlmostEqual(0.003, option_test.gamma, delta=0.001)
        self.assertAlmostEqual(33.215, option_test.vega, delta=0.001)
