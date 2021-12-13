from typing import Dict

from Source import Market
import random
import pandas as pd


class Agent(object):
    def __init__(self, name, initial_asset: Dict[str, float]):
        # add type hint if the type is not obvious
        self._name = name
        if 'Cash' not in initial_asset:
            raise Exception('Cash is required in the initialization')
        else:
            self._asset = initial_asset  # Dict[asset_name, num_of_units]
            self._initial_asset = initial_asset

        self._trading_intention = {}  # Dict[asset_name, num_of_units_to_be_traded]
        # num_of_units_to_be_traded > 0 means we want to buy, < 0 means we want to sell

        self._trading_history = pd.DataFrame(columns=['Time', 'Asset Name', 'Asset Unit'])
        # Todo: Add Trading History after a trade
        # Trading History is an n•4 dataframe
        # Column0: Label; Column1: Time (corresponds to price_record in Market)
        # Column3: Asset unit (>0 means bought; <0 means sold; =0 means hold)
        self._historical_performance = []
        # add a new attribute
        # otherwise 'generate_performance_report' will interfere with 'evaluate_holding_asset_values'
        # otherwise there will be two methods making changes in self._historical_performance
        self._holding_asset_value = 0

    def decision_making(self):
        # decision_making is the thinking process to make trading decisions.
        # Agent would save her decision in self._trading_intention
        pass

    def generate_performance_report(self, market: Market):
        # Agent could look performance report based on her previous trades (saved in self._trading_history)
        # TODO: We could provide multiple performance measures, such as return, hit rate, sharpe ratio, max drawdown,...
        trade_return = self.calculate_return(market)
        self._historical_performance.append(trade_return)
        trade_hit_rate = self.calculate_hit_rate(market)
        self._historical_performance.append(trade_hit_rate)
        trade_sharpe = self.calculate_sharpe()
        self._historical_performance.append(trade_sharpe)
        trade_max_drawdown = self.calculate_max_drawdown()
        self._historical_performance.append(trade_max_drawdown)

    def calculate_init_asset(self, market: Market):
        init_asset_value = 0
        for asset_name, asset_unit in self._initial_asset.items():
            if asset_name == 'Cash':
                init_asset_value += self._initial_asset[asset_name]
            else:
                init_asset_value += market.check_initial_value(asset_name) * asset_unit
        return init_asset_value

    def calculate_return(self, market: Market):
        self.evaluate_holding_asset_values(market)
        init_asset_value = self.calculate_init_asset(market)
        return (self._holding_asset_value - init_asset_value) / init_asset_value

    def calculate_hit_rate(self, market: Market):
        win_num = 0
        for i in range(self._trading_history.shape[0]):
            time = self._trading_history['Time'][i]
            asset_name = self._trading_history['Asset Name'][i]
            asset_unit = self._trading_history['Asset Unit'][i]
            now_price = market.check_record_value(asset_name, time)
            future_price = market.check_record_value(asset_name, time + 1)
            # price rises, buying and holding would win
            if now_price < future_price:
                if asset_unit >= 0:
                    win_num += 1
            # price drops, selling would win
            elif now_price > future_price:
                if asset_unit < 0:
                    win_num += 1
            # price unchanged, holding would win
            else:
                if asset_unit == 0:
                    win_num += 1
        return win_num / self._trading_history.shape[0]

    def calculate_sharpe(self):
        pass

    def calculate_max_drawdown(self):
        pass

    def trade(self, market: Market, time):
        for asset_name, asset_trading_unit in self._trading_intention.items():
            current_price = market.check_value(asset_name)
            if self._asset['Cash'] >= current_price * asset_trading_unit:
                self._asset['Cash'] -= current_price * asset_trading_unit
                self._asset[asset_name] += asset_trading_unit

                row_num = self._trading_history.shape[0]
                self._trading_history.loc[row_num] = [time, asset_name, asset_trading_unit]
            else:
                # if Cash is not enough, cancel the trade and don't make record
                pass

        # TODO: Add trading history record after a trade

    def evaluate_holding_asset_values(self, market: Market):
        holding_asset_value = 0
        for asset_name in self._asset:
            if asset_name == 'Cash':
                holding_asset_value += self._asset[asset_name]
            else:
                holding_asset_value += market.check_value(asset_name) * self._asset[asset_name]
        self._holding_asset_value = holding_asset_value


class HumanTrader(Agent):
    # TODO: Human Trader has interactive interface to command line window
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)

    def evaluate_holding_asset_values(self, market: Market):
        # An example to show interactive interface
        super().evaluate_holding_asset_values(market)
        print(f"{self._name}: total: {self._holding_asset_value}")

    def generate_performance_report(self, market: Market):
        super().generate_performance_report(market)
        print(f"{self._name}: trade_return: {self._historical_performance[-4]}")
        print(f"{self._name}: trade_hit_rate: {self._historical_performance[-3]}")
        print(f"{self._name}: trade_sharpe: {self._historical_performance[-2]}")
        print(f"{self._name}: trade_max_drawdown: {self._historical_performance[-1]}")


class AITrader(Agent):
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)


class RandomAITrader(AITrader):
    # RandomAITrader behaves randomly
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)

    def decision_making(self):
        # TODO: random trading
        # for each owned asset: 1/3 buy half, 1/3 sell half, 1/3 hold
        for AI_asset_name, AI_asset_units in self._asset.items():
            random_int = random.randint(1, 3)
            trade_num = max(int(AI_asset_units * 0.5), 1)
            if random_int == 1:
                # buy half
                self._trading_intention[AI_asset_name] = trade_num
            elif random_int == 2:
                # sell half
                self._trading_intention[AI_asset_name] = -trade_num
            else:
                # hold
                self._trading_intention[AI_asset_name] = 0
