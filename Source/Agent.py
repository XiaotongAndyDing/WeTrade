from typing import Dict

from Source import Market


class Agent(object):
    def __init__(self, name, initial_asset: Dict[str, float]):
        # add type hint if the type is not obvious
        self._name = name
        if 'Cash' not in initial_asset:
            raise Exception('Cash is required in the initialization')
        else:
            self._asset = initial_asset  # Dict[asset_name, num_of_units]

        self._trading_intention = {}  # Dict[asset_name, num_of_units_to_be_traded]
        # num_of_units_to_be_traded > 0 means we want to buy, < 0 means we want to sell

        self._trading_history = None  # Todo: Add Trading History after a trade
        self._historical_performance = []

    def decision_making(self):
        # decision_making is the thinking process to make trading decisions.
        # Agent would save her decision in self._trading_intention
        pass

    def generate_performance_report(self):
        # Agent could look performance report based on her previous trades (saved in self._trading_history)
        # TODO: We could provide multiple performance measures, such as return, hit rate, sharpe ratio, max drawdown,...
        pass

    def trade(self, market: Market):
        for asset_name, asset_trading_unit in self._trading_intention.items():
            current_price = market.check_value(asset_name)
            self._asset['Cash'] -= current_price * asset_trading_unit
            self._asset[asset_name] += asset_trading_unit

        # TODO: Add trading history record after a trade

    def evaluate_holding_asset_values(self, market: Market):
        holding_asset_value = 0
        for asset_name in self._asset:
            if asset_name == 'Cash':
                holding_asset_value += self._asset[asset_name]
            else:
                holding_asset_value += market.check_value(asset_name) * self._asset[asset_name]
        self._historical_performance.append(holding_asset_value)


class HumanTrader(Agent):
    # TODO: Human Trader has interactive interface to command line window
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)

    def evaluate_holding_asset_values(self, market: Market):
        # An example to show interactive interface
        super().evaluate_holding_asset_values(market)
        print(f"{self._name}: total: {self._historical_performance[-1]}")


class AITrader(Agent):
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)


class RandomAITrader(AITrader):
    # RandomAITrader behaves randomly
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)

    def decision_making(self):
        # TODO: random trading
        pass
