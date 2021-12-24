from collections import OrderedDict
from typing import Dict

from Source import Market
import random


class TradingHistoryRecord(object):
    def __init__(self, time, asset_name, unit):
        self.time = time
        self.asset_name = asset_name
        self.unit = unit


class HistoricalPerformanceRecord(object):
    def __init__(self, time, asset_return, trading_hit_rate, holding_asset_value, cumulative_pnl, one_day_pnl,
                 asset_sharpe_ratio, asset_max_drawdown):
        self.time = time
        self.asset_return = asset_return
        self.trading_hit_rate = trading_hit_rate
        self.holding_asset_value = holding_asset_value
        self.cumulative_pnl = cumulative_pnl
        self.one_day_pnl = one_day_pnl
        self.asset_sharpe_ratio = asset_sharpe_ratio
        self.asset_max_drawdown = asset_max_drawdown


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

        self._trading_history = []  # List[TradingHistoryRecord]

        self._historical_performance = OrderedDict()  # Dict[time, HistoricalPerformanceRecord]

        self._holding_asset_value = 0
        # TODO: Add Sanity Check, if an option is holding as an asset, its underlier should also be in asset

    def decision_making(self):
        # decision_making is the thinking process to make trading decisions.
        # Agent would save her decision in self._trading_intention
        pass

    def generate_performance_report(self, market: Market, time):
        self.evaluate_holding_asset_values(market)
        self._historical_performance[time] = HistoricalPerformanceRecord(time, self.calculate_return(market),
                                                                         self.calculate_hit_rate(market, time),
                                                                         self._holding_asset_value,
                                                                         self.calculate_cumulative_pnl(market),
                                                                         self.calculate_one_day_pnl(market, time),
                                                                         self.calculate_sharpe(),
                                                                         self.calculate_max_drawdown())

    def calculate_init_asset_value(self, market: Market):
        init_asset_value = 0
        for asset_name, asset_unit in self._initial_asset.items():
            if asset_name == 'Cash':
                init_asset_value += self._initial_asset[asset_name]
            else:
                init_asset_value += market.check_initial_value(asset_name) * asset_unit
        return init_asset_value

    def calculate_return(self, market: Market):
        self.evaluate_holding_asset_values(market)
        init_asset_value = self.calculate_init_asset_value(market)
        return (self._holding_asset_value - init_asset_value) / init_asset_value

    def calculate_cumulative_pnl(self, market: Market):
        self.evaluate_holding_asset_values(market)
        init_asset_value = self.calculate_init_asset_value(market)
        return self._holding_asset_value - init_asset_value

    def calculate_one_day_pnl(self, market: Market, time):
        self.evaluate_holding_asset_values(market)
        if time == 0:
            last_trading_day_asset_value = self.calculate_init_asset_value(market)
        else:
            last_trading_day_asset_value = self._historical_performance[time-1].holding_asset_value
        return self._holding_asset_value - last_trading_day_asset_value

    def calculate_hit_rate(self, market: Market, time):
        # hit rate describes the performance of trading in time horizon 1
        self.evaluate_holding_asset_values(market)
        win_num = 0
        for trade_record in self._trading_history:
            now_price = market.check_record_value(trade_record.asset_name, trade_record.time)
            if trade_record.time + 1 > time:
                # TODO: temp fix: cannot access future price
                continue
            future_price = market.check_record_value(trade_record.asset_name, trade_record.time + 1)

            # price rises, buying and holding would win
            if now_price < future_price and trade_record.unit >= 0:
                win_num += 1
            # price drops, selling would win
            elif now_price > future_price and trade_record.unit < 0:
                win_num += 1
            # price unchanged, holding would win
            elif trade_record.unit == 0:
                win_num += 1
        return win_num / len(self._trading_history)

    def calculate_sharpe(self):
        return None

    def calculate_max_drawdown(self):
        return None

    def trade(self, market: Market, time, print_log=False):
        for asset_name, asset_trading_unit in self._trading_intention.items():
            current_price = market.check_value(asset_name)
            if self._asset['Cash'] >= current_price * asset_trading_unit:
                self._asset['Cash'] -= current_price * asset_trading_unit
                self._asset[asset_name] += asset_trading_unit
                if print_log:
                    print(f"{self._name}: "
                          f" trades {asset_trading_unit} {asset_name} with Cash"
                          f" ${current_price * asset_trading_unit:.3f}")
                self._trading_history.append(TradingHistoryRecord(time, asset_name, asset_trading_unit))
            else:
                # if Cash is not enough, cancel the trade and don't make record
                pass

        self._trading_intention = {}

    def evaluate_holding_asset_values(self, market: Market, print_log=False):
        holding_asset_value = 0
        if print_log:
            print(f"{self._name}, Holding:")
        for asset_name in self._asset:
            if asset_name == 'Cash':
                holding_asset_value += self._asset[asset_name]
                if print_log:
                    print(f"Cash: ${self._asset[asset_name]}")
            else:
                holding_asset_value += market.check_value(asset_name) * self._asset[asset_name]
                if print_log:
                    print(f"{asset_name}: {self._asset[asset_name]} * ${market.check_value(asset_name):.3f} ="
                          f" ${market.check_value(asset_name) * self._asset[asset_name]:.3f}")
        self._holding_asset_value = holding_asset_value
        if print_log:
            print(f"Total: ${holding_asset_value:.3f}")


class HumanTrader(Agent):
    # TODO: Human Trader has interactive interface to command line window
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)

    def evaluate_holding_asset_values(self, market: Market):
        # An example to show interactive interface
        super().evaluate_holding_asset_values(market)
        print(f"{self._name}: total: {self._holding_asset_value}")

    def generate_performance_report(self, market: Market, time):
        super().generate_performance_report(market, time)
        print(f"{self._name}: trade_return: {self._historical_performance[-1].asset_return}")
        print(f"{self._name}: trade_hit_rate: {self._historical_performance[-1].trading_hit_rate}")
        print(f"{self._name}: trade_sharpe: {self._historical_performance[-1].asset_sharpe_ratio}")
        print(f"{self._name}: trade_max_drawdown: {self._historical_performance[-1].asset_max_drawdown}")


class AITrader(Agent):
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)


class RandomAITrader(AITrader):
    # RandomAITrader behaves randomly
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)

    def decision_making(self):
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


class DeltaHedger(Agent):
    # DeltaHedger is a trader who hedges her option portfolios. DeltaHedger could be either AI or human.
    def __init__(self, name, initial_asset):
        super().__init__(name, initial_asset)
        self.current_delta = {}  # Dict[asset_name, total_delta]

    def evaluate_holding_asset_deltas(self, market: Market):
        self.current_delta = {}
        for asset_name in self._asset:
            if market.check_type(asset_name) == 'Option':
                self.current_delta[asset_name] = market.check_delta(asset_name) * self._asset[asset_name]

    def generate_delta_hedging_plans(self, market: Market):
        self.evaluate_holding_asset_deltas(market)
        for asset_name in self._asset:
            if market.check_type(asset_name) == 'Option':
                underlier_name = market.check_underlier(asset_name)
                target_quantity = -round(self.current_delta[asset_name])
                if target_quantity != self._asset[underlier_name]:
                    self._trading_intention[underlier_name] = target_quantity - self._asset[underlier_name]

