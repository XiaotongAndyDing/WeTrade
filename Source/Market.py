from typing import List, Dict
from collections import OrderedDict
from scipy.stats import norm
import copy
import numpy as np
import pandas as pd


class FinancialProduct(object):
    BUSINESS_DAYS_PER_YEAR = 252

    def __init__(self, name, initial_value):
        self.name = name
        self.initial_value = initial_value
        self.current_value = initial_value
        self.price_record = OrderedDict()

    def check_value(self):
        return self.current_value

    def check_initial_value(self):
        return self.initial_value

    def evolve(self, time=0):
        """evolve is a method for Financial products to update its price """
        pass

    def simulate_price_moves(self, time=0, simulation_horizon=1, num_of_trails=1e3):
        """the price simulation method simulate future prices based on Monte Carlo Simulation"""
        """It can price a financial product in P measure (Real measure, historical measure)"""
        future_price_list = []
        for _ in range(int(num_of_trails)):
            tamp_asset_in_one_realization = copy.deepcopy(self)
            for time_in_simulation in range(time + 1, time + int(simulation_horizon) + 1):
                tamp_asset_in_one_realization.evolve(time=time_in_simulation)
            future_price_list.append(tamp_asset_in_one_realization.current_value)
        return future_price_list

    def mark_current_value_to_record(self, time):
        if time in self.price_record:
            raise Exception(f'There has been a price record in time {time}')
        else:
            self.price_record[time] = self.current_value


class Market(object):
    def __init__(self, financial_product_list: List[FinancialProduct]):
        if len(set([i.name for i in financial_product_list])) < len(financial_product_list):
            raise Exception('Multiple financial products have same name')
        else:
            self._financial_product_dict = {i.name: i for i in financial_product_list}
        # Sanity Check: If an option is in market, its underlier should also be in a list
        for financial_product in financial_product_list:
            if self.check_type(financial_product.name) == 'Option':
                assert financial_product.name in self._financial_product_dict

    def check_value(self, financial_product_name):
        if financial_product_name in self._financial_product_dict:
            return self._financial_product_dict[financial_product_name].current_value
        else:
            raise Exception('The name to check is NOT in the market')

    def check_initial_value(self, financial_product_name):
        if financial_product_name in self._financial_product_dict:
            return self._financial_product_dict[financial_product_name].initial_value
        else:
            raise Exception('The name to check initial value is NOT in the market')

    def check_delta(self, financial_product_name):
        if financial_product_name in self._financial_product_dict:
            if isinstance(self._financial_product_dict[financial_product_name], Option):
                return self._financial_product_dict[financial_product_name].delta
            else:
                raise Exception('check_delta only supports Options')
        else:
            raise Exception('The name to check is NOT in the market')

    def check_type(self, financial_product_name):
        if financial_product_name == 'Cash':
            return 'Cash'
        if financial_product_name in self._financial_product_dict:
            if isinstance(self._financial_product_dict[financial_product_name], Option):
                return 'Option'
            elif isinstance(self._financial_product_dict[financial_product_name], Stock) or \
                    isinstance(self._financial_product_dict[financial_product_name], StockGeometricBrownianMotion) or\
                    isinstance(self._financial_product_dict[financial_product_name],
                               StockMeanRevertingGeometricBrownianMotion) or\
                    isinstance(self._financial_product_dict[financial_product_name],
                               StockTrendingGeometricBrownianMotion):
                return 'Stock'
            else:
                return 'Others'
        else:
            raise Exception('The name to check is NOT in the market')

    def check_underlier(self, financial_product_name):
        if isinstance(self._financial_product_dict[financial_product_name], Option):
            return self._financial_product_dict[financial_product_name].underlying.name
        else:
            Exception('Only Option has an underlier. The financial product you checked is NOT an Option.')

    def check_record_value(self, financial_product_name, time):
        if financial_product_name in self._financial_product_dict:
            if time in self._financial_product_dict[financial_product_name].price_record:
                return self._financial_product_dict[financial_product_name].price_record[time]
            else:
                raise Exception(f'There has not been a price record in time {time}')
        else:
            raise Exception('The name to check record value is NOT in the market')

    def evolve(self, time=0):
        for financial_product in self._financial_product_dict.values():
            financial_product.evolve(time)

    def mark_current_value_to_record(self, time):
        for financial_product in self._financial_product_dict.values():
            financial_product.mark_current_value_to_record(time)


class Stock(FinancialProduct):
    # TODO: Refactor Stock and Fix the inheritance structure of Stock
    def __init__(self, name, initial_value, mu, sigma):
        super().__init__(name, initial_value)
        self.mu = mu
        self.sigma = sigma

    def evolve(self, time=0):
        self.current_value += np.random.normal(self.mu, self.sigma)


class StockGeometricBrownianMotion(FinancialProduct):
    """Stocks with Geometric Brownian Motion dynamics"""

    def __init__(self, name, initial_value, mu, sigma):
        super().__init__(name, initial_value)
        self.mu = mu
        self.sigma = sigma

    def evolve(self, time=0):
        self.current_value *= np.exp(np.random.normal(self.mu, self.sigma))


class StockMeanRevertingGeometricBrownianMotion(FinancialProduct):
    """Stocks with 2 components, Mean reverting component to an equilibrium price and
    Geometric Brownian Motion dynamics"""

    def __init__(self, name, initial_value, mu, sigma, equilibrium_price, mean_reversion_speed):
        super().__init__(name, initial_value)
        self.mu = mu
        self.sigma = sigma
        self.equilibrium_price = equilibrium_price
        self.mean_reversion_speed = mean_reversion_speed

    def evolve(self, time=0):
        self.current_value *= np.exp(np.random.normal(self.mu + self.mean_reversion_speed *
                                                      (self.equilibrium_price - self.current_value), self.sigma))


class StockTrendingGeometricBrownianMotion(FinancialProduct):
    """Stocks with 2 components, Trending component and Geometric Brownian Motion dynamics"""
    """S(t+1)/ S(t) = N(mu + trend_scale_param * trend_factor, sigma)
        trend_factor = sum of historical stock log returns, weighted by exponential decay factor
        exponential decay factor = exp( - time difference * trend_decay_param)"""

    def __init__(self, name, initial_value, mu, sigma, trend_scale_param, trend_decay_param):
        super().__init__(name, initial_value)
        self.mu = mu
        self.sigma = sigma
        self.trend_scale_param = trend_scale_param
        self.trend_decay_param = trend_decay_param

    def evolve(self, time=0):
        df = pd.DataFrame(list(self.price_record.values()), columns=['price'])
        df['time'] = self.price_record.keys()
        df['log_ret'] = np.log(df.price) - np.log(df.price.shift(1))
        df['time_diff'] = time - df['time']
        df['trend_factor'] = df['log_ret'] * np.exp(-self.trend_decay_param * df['time_diff'])
        self.current_value *= np.exp(np.random.normal(self.mu + self.trend_scale_param * df['trend_factor'].sum(),
                                                      self.sigma))


class Derivative(FinancialProduct):
    """Derivative is a financial product which price is determined or influenced by other financial products"""

    def __init__(self, name, underlyings):  # underlyings: List[FinancialProduct]
        super().__init__(name, 0)  # we first create a financial product without initial value
        self.underlyings = underlyings
        # Derivative's value is determined on its underlyings.
        # it is the child class's duty to update initial value by evolve(0)


class Option(Derivative):
    # Assume there is no interest rate
    def __init__(self, name, underlyings, strike, expiry):  # underlyings: List[FinancialProducts]
        super().__init__(name, underlyings)
        self.strike = strike
        self.expiry = expiry
        self.delta = 0
        self.gamma = 0
        self.vega = 0
        self.underlying = None
        if len(underlyings) != 1:
            raise Exception('Option has exactly one underlying')
        else:
            self.underlying = underlyings[0]


class EuropeanCallOption(Option):
    def __init__(self, name, underlyings, strike, expiry):
        super().__init__(name, underlyings, strike, expiry)
        self.evolve(0)
        self.initial_value = self.current_value

    def evolve(self, time=0):
        """https://www.investopedia.com/terms/b/blackscholes.asp"""
        """The evolve method prices derivative under the Arbitrage Free Assumption"""
        """In other words, it prices a financial product in Q measure"""
        if not hasattr(self.underlying, 'sigma'):
            raise Exception('underlying should have volatility parameter sigma')

        time_to_maturity = (self.expiry - time) / FinancialProduct.BUSINESS_DAYS_PER_YEAR
        annual_volatility = self.underlying.sigma * np.sqrt(FinancialProduct.BUSINESS_DAYS_PER_YEAR)
        # TODO: A little bit confusing. Stock Sigma is unit in daily vol while option pricing is using annualized vol

        if time_to_maturity < 0:
            raise Exception('Option has expired')
        elif time_to_maturity < 1e-6:
            self.delta = 0
            self.gamma = 0
            self.vega = 0
            self.current_value = max(0, self.underlying.current_value - self.strike)
            return

        d_1 = (np.log(self.underlying.current_value / self.strike) +
               0.5 * np.power(annual_volatility, 2) * time_to_maturity) / \
              (annual_volatility * np.sqrt(time_to_maturity))

        d_2 = d_1 - (annual_volatility * np.sqrt(time_to_maturity))

        self.current_value = self.underlying.current_value * norm.cdf(d_1) - self.strike * norm.cdf(d_2)
        self.delta = norm.cdf(d_1)
        self.gamma = norm.pdf(d_1) / (self.underlying.current_value * annual_volatility * np.sqrt(time_to_maturity))
        self.vega = self.underlying.current_value * norm.pdf(d_1) * np.sqrt(time_to_maturity)


class EuropeanPutOption(Option):
    def __init__(self, name, underlyings, strike, expiry):
        super().__init__(name, underlyings, strike, expiry)
        self.evolve(0)
        self.initial_value = self.current_value

    def evolve(self, time=0):
        if not hasattr(self.underlying, 'sigma'):
            raise Exception('underlying should have volatility parameter sigma')

        time_to_maturity = (self.expiry - time) / FinancialProduct.BUSINESS_DAYS_PER_YEAR
        annual_volatility = self.underlying.sigma * np.sqrt(FinancialProduct.BUSINESS_DAYS_PER_YEAR)

        if time_to_maturity < 0:
            raise Exception('Option has expired')
        elif time_to_maturity < 1e-6:
            self.delta = 0
            self.gamma = 0
            self.vega = 0
            self.current_value = max(0, self.strike - self.underlying.current_value)
            return

        d_1 = (np.log(self.underlying.current_value / self.strike) +
               0.5 * np.power(annual_volatility, 2) * time_to_maturity) / \
              (annual_volatility * np.sqrt(time_to_maturity))

        d_2 = d_1 - (annual_volatility * np.sqrt(time_to_maturity))

        self.current_value = self.strike * norm.cdf(-d_2) - self.underlying.current_value * norm.cdf(-d_1)
        self.delta = norm.cdf(d_1) - 1
        self.gamma = norm.pdf(d_1) / (self.underlying.current_value * annual_volatility * np.sqrt(time_to_maturity))
        self.vega = self.underlying.current_value * norm.pdf(d_1) * np.sqrt(time_to_maturity)
