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
    def __init__(self, ship_demand,history_data=None):
        self.ship_demand_data = ship_demand.predicted_data
        self.ship_age_distribution = []
        self.orderbook = []
        self.lack_number = 0
        self.ini_sup = 5103
        if history_data is None:
            self.monthly_history_data = load_history_data(MONTH,SUPPLY_TYPE)

    def generate_distribution(self):
        self.ship_age_distribution = []
        five_year = 60
        ten_year = 120
        sum = WITHIN_FIVE + WITHIN_TEN + WITHIN_FIF
        for time in range(VESSEL_LIFE_TIME*12):
            if time < five_year:
                self.ship_age_distribution.append(self.ini_sup*WITHIN_FIVE/sum/60)
            elif time < ten_year:
                self.ship_age_distribution.append(self.ini_sup*WITHIN_TEN/sum/60)
            else:
                self.ship_age_distribution.append(self.ini_sup*WITHIN_FIF/sum/60)
        for time in range(VESSEL_LIFE_TIME*12,(VESSEL_LIFE_TIME+5)*12):
            self.ship_age_distribution.append(0)

    def generate_orderbook(self):
        self.orderbook = []
        for time in range(1,ORDER_TIME):
            order_number = self.ship_age_distribution[-(60+time)]
            self.orderbook.append([order_number*1.2,time])

    def add_age(self):
        if self.lack_number > 0:
            age = VESSEL_LIFE_TIME*12
            list = [0]*60
            while self.lack_number > 0 and age < (VESSEL_LIFE_TIME+5)*12:
                remain_number = self.ship_age_distribution[age-1]
                if remain_number > self.lack_number:
                    remain_number = self.lack_number
                list[age-VESSEL_LIFE_TIME*12] = remain_number
                self.lack_number -= remain_number
                age += 1
            for ship_over_age in range(VESSEL_LIFE_TIME*12,(VESSEL_LIFE_TIME+5)*12):
                self.ship_age_distribution[ship_over_age] = list[ship_over_age-VESSEL_LIFE_TIME*12]
        for ship_age in reversed(range(0,VESSEL_LIFE_TIME*12)):
            if ship_age == 0:
                self.ship_age_distribution[ship_age] = 0
            else:
                self.ship_age_distribution[ship_age] = self.ship_age_distribution[ship_age-1]
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

    def forecast_demand(self,pattern,now,term):
        ship_demand_now = self.ship_demand_data[pattern][now]['price']
        ship_demand_before = self.ship_demand_data[pattern][now-term]['price']
        future_demand = (ship_demand_now - ship_demand_before)*ORDER_TIME/term + ship_demand_now
        return future_demand*1.2

    def calc_ship_supply_future(self):
        supply = 0
        for construct in self.orderbook:
            supply += construct[0]
        for in_operation in range(0,(VESSEL_LIFE_TIME+5)*12-ORDER_TIME):
            supply += self.ship_age_distribution[in_operation]
        return supply

    def order_ship(self,pattern,time):
        future_demand = 0
        for term in range(1,ORDER_TIME+1):
            future_demand += self.forecast_demand(pattern,time,term)
        future_demand /= ORDER_TIME
        future_supply = self.calc_ship_supply_future()
        order_number = future_demand*SHIP_NUMBER_PER_DEMAND - future_supply
        if order_number > 0:
            if order_number > ORDER_CAPACITY:
                self.lack_number = order_number - ORDER_CAPACITY
                order_number = ORDER_CAPACITY
            self.orderbook.append([order_number,ORDER_TIME])
        return

    def calc_ship_supply(self):
        return sum(self.ship_age_distribution)

    # generate predicted sinario
    def generate_sinario(self,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years
        # predicted data type
        self.predicted_data = []
        for p_num in range(predict_pattern_number):
            self.predicted_data.append([])

        for pattern in range(predict_pattern_number):
            self.generate_distribution()
            self.generate_orderbook()
            for time in range(self.predict_years*12+FREIGHT_MAX_DELAY):
                self.order_ship(pattern,time)
                self.predicted_data[pattern].append({'date':self.ship_demand_data[pattern][time]['date'],'price': self.calc_ship_supply()})
                self.add_age()
        for pattern in range(predict_pattern_number):
            point = self.predicted_data[pattern][ORDER_TIME]['price']
            start = self.predicted_data[pattern][0]['price']
            inclination = (point-start)/ORDER_TIME
            for i in range(ORDER_TIME):
                self.predicted_data[pattern][i]['price'] = start + inclination*i*random.random()
        return
