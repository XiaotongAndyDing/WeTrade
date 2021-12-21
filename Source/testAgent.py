from unittest import TestCase

import numpy as np

from Source.Agent import Agent, HumanTrader, DeltaHedger
from Source.Market import Market, Stock, StockGeometricBrownianMotion, EuropeanCallOption


class TestAgent(TestCase):
    def test_creation(self):
        asset_test = {'Cash': 1000, 'StockTest': 0}
        agent_test = Agent('agent_test', asset_test)

        # test creation of Stock
        self.assertEqual('agent_test', agent_test._name)
        self.assertEqual(1000, agent_test._asset['Cash'])
        self.assertEqual(0, agent_test._asset['StockTest'])

    def test_trade(self):
        asset_test = {'Cash': 1000, 'StockTest': 0}
        agent_test = Agent('agent_test', asset_test)

        market_test = Market([Stock('StockTest', 100, 0, 0)])
        agent_test._trading_intention = {'StockTest': 5}  # agent_test wants to spend $500 and buy 5 shares of stocks
        agent_test.trade(market_test, 0)

        self.assertEqual(1000 - 5 * 100, agent_test._asset['Cash'])
        self.assertEqual(5, agent_test._asset['StockTest'])

        self.assertEqual(1, len(agent_test._trading_history))
        self.assertEqual(0, agent_test._trading_history[0].time)
        self.assertEqual('StockTest', agent_test._trading_history[0].asset_name)
        self.assertEqual(5, agent_test._trading_history[0].unit)

        agent_test._trading_intention = {'StockTest': -5}  # agent_test wants to sell $500 and buy 5 shares of stocks
        agent_test.trade(market_test, 0)

        self.assertEqual(1000, agent_test._asset['Cash'])
        self.assertEqual(0, agent_test._asset['StockTest'])

        self.assertEqual(2, len(agent_test._trading_history))
        self.assertEqual(0, agent_test._trading_history[0].time)
        self.assertEqual('StockTest', agent_test._trading_history[0].asset_name)
        self.assertEqual(5, agent_test._trading_history[0].unit)
        self.assertEqual(0, agent_test._trading_history[1].time)
        self.assertEqual('StockTest', agent_test._trading_history[1].asset_name)
        self.assertEqual(-5, agent_test._trading_history[1].unit)

    def test_evaluate_holding_asset_values(self):
        asset_test = {'Cash': 1000, 'StockTest': 0}
        agent_test = Agent('agent_test', asset_test)

        market_test = Market([Stock('StockTest', 100, 1, 0)])
        agent_test.evaluate_holding_asset_values(market_test)

        self.assertEqual(1000, agent_test._holding_asset_value)

        agent_test._trading_intention = {'StockTest': 5}  # agent_test wants to spend $500 and buy 5 shares of stocks
        agent_test.trade(market_test, 0)

        agent_test.evaluate_holding_asset_values(market_test)
        self.assertEqual(1000, agent_test._holding_asset_value)

        market_test.evolve(1)
        agent_test.evaluate_holding_asset_values(market_test)
        self.assertEqual(1005, agent_test._holding_asset_value)

    def test_calculate_return(self):
        asset_test = {'Cash': 1000, 'StockTest': 0}
        agent_test = Agent('agent_test', asset_test)

        market_test = Market([Stock('StockTest', 100, 1, 0)])
        agent_test._trading_intention = {'StockTest': 5}
        agent_test.trade(market_test, 0)
        market_test.evolve(1)

        self.assertEqual(5 / 1000, agent_test.calculate_return(market_test))

        market_test.evolve(2)
        self.assertEqual(10 / 1000, agent_test.calculate_return(market_test))

    def test_hit_rate(self):
        asset_test = {'Cash': 1000, 'StockTest': 0}
        agent_test = Agent('agent_test', asset_test)

        market_test = Market([Stock('StockTest', 100, 1, 0)])
        market_test.mark_current_value_to_record(0)
        agent_test._trading_intention = {'StockTest': 5}
        agent_test.trade(market_test, 0)

        market_test.evolve(1)
        market_test.mark_current_value_to_record(1)

        self.assertEqual(1, agent_test.calculate_hit_rate(market_test))

        agent_test._trading_intention = {'StockTest': -1}
        agent_test.trade(market_test, 1)

        market_test.evolve(2)
        market_test.mark_current_value_to_record(2)
        self.assertEqual(0.5, agent_test.calculate_hit_rate(market_test))

    def test_generate_performance_report(self):
        asset_test = {'Cash': 1000, 'StockTest': 0}
        agent_test = Agent('agent_test', asset_test)

        market_test = Market([Stock('StockTest', 100, 1, 0)])
        market_test.mark_current_value_to_record(0)
        agent_test._trading_intention = {'StockTest': 5}
        agent_test.trade(market_test, 0)

        market_test.evolve(1)
        market_test.mark_current_value_to_record(1)

        agent_test.generate_performance_report(market_test, 1)
        self.assertEqual(1, len(agent_test._historical_performance))
        self.assertEqual(0.005, agent_test._historical_performance[0].asset_return)
        self.assertEqual(1, agent_test._historical_performance[0].trading_hit_rate)

        agent_test._trading_intention = {'StockTest': -5}
        agent_test.trade(market_test, 1)

        market_test.evolve(2)
        market_test.mark_current_value_to_record(2)

        agent_test.generate_performance_report(market_test, 2)
        self.assertEqual(2, len(agent_test._historical_performance))
        self.assertEqual(0.005, agent_test._historical_performance[0].asset_return)
        self.assertEqual(1, agent_test._historical_performance[0].trading_hit_rate)
        self.assertEqual(0, agent_test._historical_performance[1].asset_return)
        self.assertEqual(0.5, agent_test._historical_performance[1].trading_hit_rate)


class TestDeltaHedger(TestCase):
    def test_evaluate_holding_asset_deltas(self):
        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1 / np.sqrt(252))
        option_test = EuropeanCallOption('option_test', [stock_test], 100, 252)
        test_market = Market([stock_test, option_test])

        asset_test = {'Cash': 1000, 'stock_gbm_test': 0, 'option_test': 1}  # agent holds an option
        agent_test = DeltaHedger('agent_test', asset_test)

        agent_test.evaluate_holding_asset_deltas(test_market)

        self.assertEqual(1, len(agent_test.current_delta))
        self.assertAlmostEqual(0.691, agent_test.current_delta['option_test'], delta=0.001)

        stock_test = StockGeometricBrownianMotion('stock_gbm_test', 100, 0, 1 / np.sqrt(252))
        option_test = EuropeanCallOption('option_test', [stock_test], 100, 252)
        test_market = Market([stock_test, option_test])

        asset_test = {'Cash': 1000, 'stock_gbm_test': 0, 'option_test': -1}  # agent shorts an option
        agent_test = DeltaHedger('agent_test', asset_test)

        agent_test.evaluate_holding_asset_deltas(test_market)

        self.assertEqual(1, len(agent_test.current_delta))
        self.assertAlmostEqual(-0.691, agent_test.current_delta['option_test'], delta=0.001)
