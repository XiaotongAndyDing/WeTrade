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

    def if_trade_invalid(self, market: Market, tmp_trading_intention):
        # Attention: If the trade intention is invalid, return true!
        __tmp_trader_asset = self._asset

        for asset_name, asset_trading_unit in tmp_trading_intention.items():
            current_price = market.check_value(asset_name)
            __tmp_trader_asset['Cash'] -= current_price * asset_trading_unit
            __tmp_trader_asset[asset_name] += asset_trading_unit
            if __tmp_trader_asset['cash'] < 0:
                return True
        return False

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
    __TRADER_ACTIONS = ("buy", "sell", "pass")

    # TODO: Human Trader has interactive interface to command line window
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)

    def evaluate_holding_asset_values(self, market: Market):
        # An example to show interactive interface
        super().evaluate_holding_asset_values(market)
        print(f"{self._name}: total: {self._historical_performance[-1]}")

    def get_asset_in_command_line(self):
        # This function gives an interface to show the asset that human trader has in command line.
        print("This is your asset:")
        for asset_name in self._asset:
            print(f'Asset name:{asset_name}\tNumber of units:{self._asset[asset_name]}')

    def get_trading_intention(self, market: Market):
        # This function gives an interface to get only one human trader's intention.
        # If trader wants to trade more than one asset, we should invoke the function again.
        # So if the trade time renew, we should empty the self._trading_intention

        # First, we show all the trader's asset
        HumanTrader.get_asset_in_command_line(self)

        __tmp_trading_intention = self._trading_intention
        trader_action = input('Please input "buy", "sell" or "pass" to trade')
        while trader_action not in self.__TRADER_ACTIONS:
            print("This is an invalid input, please try again.")
            trader_action = input('Please input "buy" or "sell" to trade')
        print('Input successful!')

        if trader_action == "pass":
            __tmp_trading_intention = None
            return self._trading_intention

        else:
            asset_name_to_be_traded = input('Please input the asset name you want ')
            if asset_name_to_be_traded in __tmp_trading_intention:
                print("Attention: If you input the same asset name, your last input will overwrite the previous one.")

            # TODO: We could provide the list of asset that can be traded in case the asset name is invalid

            asset_trading_unit = input('Please input the number you want')
            if trader_action == "buy":
                __tmp_trading_intention[asset_name_to_be_traded] = asset_trading_unit
            else:
                __tmp_trading_intention[asset_name_to_be_traded] = (-1) * asset_trading_unit

            if Agent.if_trade_invalid(self, market, __tmp_trading_intention):
                # If the trade intention is invalid, we will return the function.
                print("Your trade intention is invalid, maybe your cash is not enough."
                      "Please consider your input again.")
                return HumanTrader.get_trading_intention(self, market)
            else:
                self._trading_intention = __tmp_trading_intention
                return self._trading_intention


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
