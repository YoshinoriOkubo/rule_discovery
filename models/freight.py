import numpy as np
import sys
import math
import datetime
import os
import random
from ship_demand import ShipDemand
from ship_supply import ShipSupply
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

class Freight:
    def __init__(self, ship_demand_data,ship_supply_data,history_data=None):
        self.ship_demand_data = ship_demand_data
        self.ship_supply_data = ship_supply_data
        if history_data is None:
            self.history_data = load_monthly_history_data(FREIGHT_TYPE,CCFI)

    def calc_freight(self,pattern,time):
        return max(0,self.ship_demand_data[pattern][time]['price']/self.ship_supply_data[pattern][time]['price']*(-1809432.357) + 4770.569817)


    # generate predicted sinario
    def generate_sinario(self,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years
        dt   = np.dtype({'names': ('date', 'price'),
                         'formats': (np.float , np.float)})
        self.predicted_data = np.array([], dtype=dt)

        for pattern in range(predict_pattern_number):
            for year in range(self.predict_years):
                for month in range(12):
                    self.predicted_data = np.append(self.predicted_data, np.array([(year*12+month, self.calc_freight(pattern,year*12+month))], dtype=dt))
        self.predicted_data = self.predicted_data.reshape(DEFAULT_PREDICT_PATTERN_NUMBER,VESSEL_LIFE_TIME*12)
        return
