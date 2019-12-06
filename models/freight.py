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
    def __init__(self, ship_demand,ship_supply,oil,type,history_data=None):
        self.ship_demand_data = ship_demand.predicted_data
        self.ship_supply_data = ship_supply.predicted_data
        self.oil_data = oil.predicted_data
        self.type = type
        if history_data is None:
            if self.type == OUTWARD:
                self.monthly_history_data = load_history_data(MONTH,FREIGHT_TYPE,OUTWARD)
            elif self.type == HOMEWARD:
                    self.monthly_history_data = load_history_data(MONTH,FREIGHT_TYPE,HOMEWARD)

    def calc_freight(self,type,pattern,time):
        if type == OUTWARD:
            inclination_oil = F_OUTWARD_INCLINATION_OIL
            inclination_demand = F_OUTWARD_INCLINATION_DEMAND
            intercept = F_OUTWARD_INTERCEPT
        elif type == HOMEWARD:
            inclination_oil = F_HOMEWARD_INCLINATION_OIL
            inclination_demand = F_HOMEWARD_INCLINATION_DEMAND
            intercept = F_HOMEWARD_INTERCEPT
        current_oil = self.oil_data[pattern][time]['price']
        current_demand = self.ship_demand_data[pattern][time]['price']
        current_supply = self.ship_supply_data[pattern][time]['price']
        minimum_freight = 0
        return max(minimum_freight,inclination_oil*current_oil + inclination_demand*current_demand/current_supply + intercept)

    # generate predicted scenario
    def generate_scenario(self,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years
        self.predicted_data = []
        for p_num in range(predict_pattern_number):
            self.predicted_data.append([])
        for pattern in range(predict_pattern_number):
            for time in range(self.predict_years*12):
                self.predicted_data[pattern].append({'date':self.ship_demand_data[pattern][time]['date'], 'price':self.calc_freight(self.type,pattern,time)})
        return
