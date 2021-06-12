import random
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

TRANSITION_MATRIX = pd.read_csv(
    './data/transition_matrices/transition_matrix_average.csv', index_col=0)


class Customer:
    """
    a single customer that moves through the supermarket
    in a MCMC simulation
    """

    def __init__(self, name, state):
        self.name = name
        self.state = state

    def __repr__(self):
        return f'customer_no {self.name} {self.state}'

    def next_state(self):
        '''
        Propagates the customer to the next state.
        Returns nothing.
        '''
        self.state = random.choices(['checkout', 'dairy', 'drinks', 'fruit', 'spices'], list(
            TRANSITION_MATRIX.loc[self.state]))
        self.state = self.state[0]

    def is_active(self):

        if self.state == 'checkout':
            return True


class Supermarket:
    """manages multiple Customer instances that are currently in the market."""

    def __init__(self, market_name, opening, closing):
        self.market_name = market_name
        self.opening = opening
        self.closing = closing
        self.customers = []
        self.current_time = 0
        self.index = 0
        self.customer_index = 0
        self.state = 0
        self.dti = pd.date_range(self.opening, self.closing, freq="T").time

    def __repr__(self):
        return f'{len(self.dti)}'

    def is_open(self):
        if self.index <= len(self.dti)-2:
            return datetime.strptime(self.opening, '%H:%M:%S') <= datetime.strptime(self.get_time(), '%H:%M:%S') <= datetime.strptime(self.closing, '%H:%M:%S')

    def get_time(self):
        """current time in HH:MM format,"""
        self.current_time = self.dti[self.index]
        self.current_time = str(self.current_time)
        return self.current_time

    def print_customers(self):
        """print all customers with the current time and id in CSV format.
        """
        return self.customers

    def next_minute(self):
        """"propagates all customers to the next state."""

        self.index += 1
        next_time = self.dti[self.index]

        for customer in self.customers:
            customer.next_state()

    def add_new_customers(self):
        """randomly creates new customers.
        """
        self.state = random.choices(['dairy', 'drinks', 'fruit', 'spices'])
        self.state = self.state[0]
        self.customer_index += 1
        new_customer = Customer(self.customer_index, self.state)
        self.customers.append(new_customer)

    def remove_exitsting_customers(self):
        """removes every customer that is not active any more.
        """
        for customer in self.customers:
            if customer.is_active():
                self.customers.remove(customer)


if __name__ == "__main__":
    supermarket = Supermarket('MarketRangers', '07:00:00', '07:59:00')
    market_rangers = pd.DataFrame()

    while supermarket.is_open():
        supermarket.add_new_customers()
        for customer in supermarket.customers:
            market_rangers = market_rangers.append({'timestamp': supermarket.get_time(),
                                                    'customer_no': str(customer.name),
                                                    'location': customer.state
                                                    }, ignore_index=True)

        supermarket.remove_exitsting_customers()
        supermarket.next_minute()

    market_rangers.set_index('timestamp', inplace=True)
    market_rangers.to_csv(
        './data/Simulated_Market_Table/simulated_market_table_average.csv')
