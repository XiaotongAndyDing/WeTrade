from typing import List, Dict
from collections import OrderedDict
from scipy.stats import norm

import numpy as np


class FinancialProduct(object):
    BUSINESS_DAYS_PER_YEAR = 252

    def __init__(self, name, initial_value):
        self.name = name
        self.current_value = initial_value
        self.price_record = OrderedDict()

    def check_value(self):
        return self.current_value

    def evolve(self, time=0):
        pass

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

    def check_value(self, financial_product_name):
        if financial_product_name in self._financial_product_dict:
            return self._financial_product_dict[financial_product_name].current_value
        else:
            raise Exception('The name to check is NOT in the market')

    def evolve(self, time=0):
        for financial_product in self._financial_product_dict.values():
            financial_product.evolve(time)

    def mark_current_value_to_record(self, time):
        for financial_product in self._financial_product_dict.values():
            financial_product.mark_current_value_to_record(time)


class Stock(FinancialProduct):
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
    """Stocks with 2 components, Mean reverting component to a equilibrium price and
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

    def evolve(self, time=0):
        """https://www.investopedia.com/terms/b/blackscholes.asp"""
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
