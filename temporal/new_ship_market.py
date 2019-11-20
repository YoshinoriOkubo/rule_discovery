import numpy as np
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
    def __init__(self,oil,freight_outward,freight_return,exchange,demand,supply):
        self.oil_data = oil.predicted_data
        self.freight_outward_data = freight_outward.predicted_data
        self.freight_return_data = freight_return.predicted_data
        self.exchange_data = exchange.predicted_data
        self.demand_data = demand.predicted_data
        self.supply_data = supply.predicted_data

    def calcNPV(self,pattern,time):
        NPV = 0
        current_oil_price = self.oil_data[pattern][time]['price']
        freight_outward = self.freight_outward_data[pattern][time]['price']
        freight_return = self.freight_return_data[pattern][time]['price']
        total_freight = 0.5*(freight_outward*LOAD_FACTOR_ASIA_TO_EUROPE+freight_return*LOAD_FACTOR_EUROPE_TO_ASIA)
        current_demand = self.demand_data[pattern][time]['price']
        current_supply = self.supply_data[pattern][time]['price']
        cash_year = 0
        for future in range(1,ORDER_TIME+VESSEL_LIFE_TIME*12+1):
            ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,1)
            if future < ORDER_TIME:
                pass
            else:
                cash_year += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
            if future % 12 == 0:
                cash_year /= (1 + DISCOUNT_RATE) ** (future/12)
                NPV += cash_year
                cash_year = 0
        return max(0.3,NPV/INITIAL_COST_OF_SHIPBUIDING)

    # generate predicted sinario
    def generate_sinario(self,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years
        dt   = np.dtype({'names': ('date', 'price'),
                         'formats': (np.float , np.float)})
        self.predicted_data = np.array([], dtype=dt)
        for pattern in range(predict_pattern_number):
            for time in range(self.predict_years*12):
                self.predicted_data = np.append(self.predicted_data, np.array([(time,self.calcNPV(pattern,time))], dtype=dt))
        self.predicted_data = self.predicted_data.reshape(DEFAULT_PREDICT_PATTERN_NUMBER,predict_years*12)
        return
