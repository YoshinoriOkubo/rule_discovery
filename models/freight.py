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
    def __init__(self, ship_demand,ship_supply,oil,type,history_data=None):
        self.ship_demand_data = ship_demand.predicted_data
        self.ship_supply_data = ship_supply.predicted_data
        self.oil_data = oil.predicted_data
        self.type = type
        if history_data is None:
            if self.type == OUTWARD:
                self.monthly_history_data = load_history_data(MONTH,FREIGHT_TYPE,OUTWARD)
            elif self.type == RETURN:
                    self.monthly_history_data = load_history_data(MONTH,FREIGHT_TYPE,RETURN)

    def calc_fuel_cost(self,oil):
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
        fuel_cost = ship.calc_fuel_cost(oil)
        return fuel_cost

    def calc_freight(self,type,pattern,time):
        if type == OUTWARD:
            inclination = FREIGHT_OUTWARD_INCLINATION
            intercept = FREIGHT_OUTWARD_INTERCEPT
            delay = FREIGHT_OUTWARD_DELAY
        elif type == RETURN:
            inclination = FREIGHT_RETURN_INCLINATION
            intercept = FREIGHT_RETURN_INTERCEPT
            delay = FREIGHT_RETURN_DELAY
        current_demand = self.ship_demand_data[pattern][time-delay]['price']
        current_supply = self.ship_supply_data[pattern][time-delay]['price']
        fuel_cost = self.calc_fuel_cost(self.oil_data[pattern][time]['price'])
        minimum_freight = fuel_cost/TEU_SIZE#100% LOAD_FACTOR
        return max(minimum_freight,inclination*current_demand/current_supply + intercept)

    # generate predicted sinario
    def generate_sinario(self,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years
        self.predicted_data = []
        for p_num in range(predict_pattern_number):
            self.predicted_data.append([])
        for pattern in range(predict_pattern_number):
            for time in range(self.predict_years*12):
                self.predicted_data[pattern].append({'date':self.ship_demand_data[pattern][time]['date'], 'price':self.calc_freight(self.type,pattern,time)})
        return
