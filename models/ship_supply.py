import numpy as np
import sys
import math
import datetime
import os
import random
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

class ShipSupply:
    def __init__(self, ship_demand_data,history_data=None):
        self.ship_demand_data = ship_demand_data
        self.ship_age_distribution = []
        self.orderbook = []
        if history_data is None:
            self.history_data = load_monthly_history_data(SUPPLY_TYPE)

    def generate_distribution(self):
        self.ship_age_distribution = []
        five_year = 60
        ten_year = 120
        sum = WITHIN_FIVE + WITHIN_TEN + WITHIN_FIF
        for time in range(VESSEL_LIFE_TIME*12):
            if time < five_year:
                self.ship_age_distribution.append(5000*WITHIN_FIVE/sum/60)
            elif time < ten_year:
                self.ship_age_distribution.append(5000*WITHIN_TEN/sum/60)
            else:
                self.ship_age_distribution.append(5000*WITHIN_FIF/sum/60)

    def generate_orderbook(self):
        self.orderbook = []
        for time in range(1,ORDER_TIME):
            order_number = self.ship_age_distribution[-time]
            self.orderbook.append([order_number,time])

    def add_age(self):
        for age in reversed(range(0,len(self.ship_age_distribution))):
            if age == 0:
                self.ship_age_distribution[age] = 0
            else:
                self.ship_age_distribution[age] = self.ship_age_distribution[age-1]
        self.under_construct()
        self.finish_construct()

    def under_construct(self):
        for index in range(len(self.orderbook)):
            self.orderbook[index][1] -= 1

    def finish_construct(self):
        if len(self.orderbook) > 0:
            if self.orderbook[0][1] == 0:
                number = self.orderbook[0][0]
                self.ship_age_distribution[0] = number
                self.orderbook.pop(0)

    def forecast_demand_in_two_years(self,pattern,now,term):
        ship_demand_now = self.ship_demand_data[pattern][now]['price']
        ship_demand_before = self.ship_demand_data[pattern][now-term]['price']
        future_demand = (ship_demand_now - ship_demand_before)*ORDER_TIME/term + ship_demand_now
        return future_demand

    def calc_ship_supply_future(self):
        supply = 0
        for construct in self.orderbook:
            supply += construct[0]
        for in_operation in range(0,VESSEL_LIFE_TIME*12-ORDER_TIME):
            supply += self.ship_age_distribution[in_operation]
        return supply

    def order_ship(self,pattern,time):
        future_demand = 0
        for term in range(1,ORDER_TIME+1):
            future_demand += self.forecast_demand_in_two_years(pattern,time,term)
        future_demand /= ORDER_TIME
        future_supply = self.calc_ship_supply_future()
        order_number = future_demand*12/SHIP_NUMBER_PER_DEMAND - future_supply
        if order_number > 0:
            #print('order',order_number)
            self.orderbook.append([order_number,ORDER_TIME])
        return

    def calc_ship_supply(self):
        return sum(self.ship_age_distribution)

    # generate predicted sinario
    def generate_sinario(self,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years
        dt   = np.dtype({'names': ('date', 'price'),
                         'formats': (np.float , np.float)})
        self.predicted_data = np.array([], dtype=dt)

        for pattern in range(predict_pattern_number):
            self.generate_distribution()
            self.generate_orderbook()
            for year in range(self.predict_years):
                for month in range(12):
                    self.order_ship(pattern,year*12+month)
                    self.predicted_data = np.append(self.predicted_data, np.array([(year*12+month, self.calc_ship_supply())], dtype=dt))
                    self.add_age()
        self.predicted_data = self.predicted_data.reshape(DEFAULT_PREDICT_PATTERN_NUMBER,VESSEL_LIFE_TIME*12)
        return
