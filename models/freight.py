import numpy as np
import sys
import math
import datetime
import os
import random
from ship_demand import ShipDemand
from ship_supply import ShipSupply
from ship import Ship
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

class Freight:
    def __init__(self, ship_demand_data,ship_supply_data,oil_data,history_data=None):
        self.ship_demand_data = ship_demand_data
        self.ship_supply_data = ship_supply_data
        self.oil_data = oil_data
        if history_data is None:
            self.history_data = load_monthly_history_data(FREIGHT_TYPE,CCFI)

    def calc_fuel_cost(self,oil):
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
        fuel_cost = ship.calc_fuel_cost(oil)
        return fuel_cost

    def calc_freight(self,type,pattern,time):
        if type == OUTWARD:
            inclination = -2661522.996
            intercept = 6834.623141
            delay = -9
        elif type == RETURN:
            inclination = -869948.0385
            intercept = 2578.502045
            delay = -3
        if time - delay < 0 or time - delay > VESSEL_LIFE_TIME*12-1:
            time = time + delay
        fuel_cost = self.calc_fuel_cost(self.oil_data[pattern][time]['price'])
        minimum_freight = fuel_cost/TEU_SIZE#100% LOAD_FACTOR
        return max(minimum_freight,self.ship_demand_data[pattern][time-delay]['price']/self.ship_supply_data[pattern][time-delay]['price']*(inclination) + intercept)

    # generate predicted sinario
    def generate_sinario(self,type,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years
        dt   = np.dtype({'names': ('date', 'price'),
                         'formats': (np.float , np.float)})
        self.predicted_data = np.array([], dtype=dt)
        for pattern in range(predict_pattern_number):
            for year in range(self.predict_years):
                for month in range(12):
                    self.predicted_data = np.append(self.predicted_data, np.array([(year*12+month, self.calc_freight(type,pattern,year*12+month))], dtype=dt))
        self.predicted_data = self.predicted_data.reshape(DEFAULT_PREDICT_PATTERN_NUMBER,predict_years*12)
        return
