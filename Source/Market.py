from typing import List

import numpy as np


class FinancialProduct(object):
    def __init__(self, name, initial_value):
        self.name = name
        self.current_value = initial_value

    def check_value(self):
        return self.current_value

    def evolve(self):
        pass


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

    def evolve(self):
        for financial_product in self._financial_product_dict.values():
            financial_product.evolve()


class Stock(FinancialProduct):
    def __init__(self, name, initial_value, mu, sigma):
        super().__init__(name, initial_value)
        self._mu = mu
        self._sigma = sigma

    def evolve(self):
        self.current_value += np.random.normal(self._mu, self._sigma)


class StockGeometricBrownianMotion(FinancialProduct):
    """Stocks with Geometric Brownian Motion dynamics"""
    def __init__(self, name, initial_value, mu, sigma):
        super().__init__(name, initial_value)
        self._mu = mu
        self._sigma = sigma

    def evolve(self):
        self.current_value *= np.exp(np.random.normal(self._mu, self._sigma))


class StockMeanRevertingGeometricBrownianMotion(FinancialProduct):
    """Stocks with 2 components, Mean reverting component to a equilibrium price and
    Geometric Brownian Motion dynamics"""
    def __init__(self, name, initial_value, mu, sigma, equilibrium_price, mean_reversion_speed):
        super().__init__(name, initial_value)
        self._mu = mu
        self._sigma = sigma
        self._equilibrium_price = equilibrium_price
        self._mean_reversion_speed = mean_reversion_speed

    def evolve(self):
        self.current_value *= np.exp(np.random.normal(self._mu + self._mean_reversion_speed *
                                     (self._equilibrium_price - self.current_value), self._sigma))
