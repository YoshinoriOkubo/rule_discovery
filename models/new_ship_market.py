import sys
import math
import datetime
import os
import random
from ship import Ship
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

class NewShipMarket:
    def __init__(self,demand,supply,history_data=None):
        self.demand_data = demand.predicted_data
        self.supply_data = supply.predicted_data
        if history_data is None:
            self.monthly_history_data = load_history_data(MONTH,NEWSHIPMARKET_TYPE)
        else:
            self.monthly_history_data = history_data

    # generate predicted scenario
    def generate_scenario(self,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years
        self.predicted_data = []
        for p_num in range(predict_pattern_number):
            self.predicted_data.append([])

        for pattern in range(predict_pattern_number):
            for time in range(self.predict_years*12):
                if time - 3 >= 0:
                    x = self.demand_data[pattern][time-3]['price']/self.supply_data[pattern][time-3]['price']
                else:
                    x = DEMAND_BEFORE[time-3]/SUPPLY_BEFORE[time-3]
                price = NEW_BUILDING_INCLINATION * x + NEW_BUILDING_INTERCEPT
                price *= 1000000
                self.predicted_data[pattern].append({'date':time,'price':price})
        return
