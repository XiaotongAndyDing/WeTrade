from unittest import TestCase

from Source.Agent import Agent, HumanTrader
from Source.Market import Market, Stock


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
        agent_test.trade(market_test)

        self.assertEqual(1000 - 5 * 100, agent_test._asset['Cash'])
        self.assertEqual(5, agent_test._asset['StockTest'])

        agent_test._trading_intention = {'StockTest': -5}  # agent_test wants to sell $500 and buy 5 shares of stocks
        agent_test.trade(market_test)

        self.assertEqual(1000, agent_test._asset['Cash'])
        self.assertEqual(0, agent_test._asset['StockTest'])

    def test_evaluate_holding_asset_values(self):
        asset_test = {'Cash': 1000, 'StockTest': 0}
        agent_test = Agent('agent_test', asset_test)

        market_test = Market([Stock('StockTest', 100, 0, 0)])
        agent_test.evaluate_holding_asset_values(market_test)

        self.assertEqual(1, len(agent_test._historical_performance))
        self.assertEqual(1000, agent_test._historical_performance[0])

        agent_test._trading_intention = {'StockTest': 5}  # agent_test wants to spend $500 and buy 5 shares of stocks
        agent_test.trade(market_test)

        agent_test.evaluate_holding_asset_values(market_test)

        self.assertEqual(2, len(agent_test._historical_performance))
        self.assertEqual(1000, agent_test._historical_performance[1])
