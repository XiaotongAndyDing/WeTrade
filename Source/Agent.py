from typing import Dict

from Source import Market


class Agent(object):
    def __init__(self, name, initial_asset: Dict[str, float]):
        # add type hint if the type is not obvious
        self._name = name
        self._asset = initial_asset  # Dict[asset_name, num_of_units]

    def decision_making(self):
        pass

    def generate_performance_report(self):
        pass

    def trade(self, market: Market):
        pass

    def evaluate_holding_asset_values(self, market: Market):
        pass


class HumanTrader(Agent):
    # Human Trader has interactive interface to command line window
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)


class AITrader(Agent):
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)


class RandomAITrader(AITrader):
    # RandomAITrader behaves randomly
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)
