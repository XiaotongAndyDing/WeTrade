from unittest import TestCase

from Source.Agent import Agent


class TestAgent(TestCase):
    def test_creation(self):
        asset_test = {'Cash': 1000, 'StockTest': 0}
        agent_test = Agent('agent_test', asset_test)

        # test creation of Stock
        self.assertEqual('agent_test', agent_test._name)
        self.assertEqual(1000, agent_test._asset['Cash'])
        self.assertEqual(0, agent_test._asset['StockTest'])

