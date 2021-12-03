import numpy as np


class Market(object):
    def __init__(self):
        pass


class FinancialProduct(object):
    def __init__(self, name, initial_value):
        self._name = name
        self._current_value = initial_value

    def check_value(self):
        return self._current_value

    def evolve(self):
        pass


class Cash(FinancialProduct):
    def __init__(self, initial_value):
        super().__init__('Cash', initial_value)


class Stock(FinancialProduct):
    def __init__(self, name, initial_value, mu, sigma):
        super().__init__(name, initial_value)
        self._mu = mu
        self._sigma = sigma

    def evolve(self):
        self._current_value += np.random.normal(self._mu, self._sigma)

