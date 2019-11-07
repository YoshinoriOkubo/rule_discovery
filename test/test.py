import numpy as np
import sys
sys.path.append('../models')
from oil_price import Sinario
from freight_rate_outward import FreightOutward
from freight_rate_return import FreightReturn
from exchange_rate import ExchangeRate
import matplotlib.pyplot as plt
from ship import Ship
import time
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

def adapt_rule(oil_price,freight,exchange,own_ship,rule):
    actionlist = rule[8:14]
    a = OIL_PRICE_LIST[convert2to10_in_list(rule[0])]
    b = OIL_PRICE_LIST[convert2to10_in_list(rule[1])]
    if a == b or ( a <= oil_price and oil_price <= b):
        c = FREIGHT_RATE_LIST[convert2to10_in_list(rule[2])]
        d = FREIGHT_RATE_LIST[convert2to10_in_list(rule[3])]
        if c == d or ( c <= freight and freight <= d):
            e = EXCHANGE_RATE_LIST[convert2to10_in_list(rule[4])]
            f = EXCHANGE_RATE_LIST[convert2to10_in_list(rule[5])]
            if e == f or (e <= exchange and exchange <= f):
                g = OWN_SHIP_LIST[convert2to10_in_list(rule[6])]
                h = OWN_SHIP_LIST[convert2to10_in_list(rule[7])]
                if g == h or (g <= own_ship and own_ship <= h):
                    result = [True]
                    result.append([])
                    result[1].append(VESSEL_SPEED_LIST[actionlist[0]])
                    result[1].append(PURCHASE_NUMBER[actionlist[1]])
                    result[1].append(PURCHASE_NUMBER[actionlist[2]])
                    result[1].append(SELL_NUMBER[actionlist[3]])
                    result[1].append(CHARTER_IN_NUMBER[actionlist[4]])
                    result[1].append(CHARTER_OUT_NUMBER[actionlist[5]])
                    return result
    return [False]

def generate_specific_scenario():
    oil = [50]*180
    freight_outward = [{'price':400}]*180
    freight_return = [{'price':200}] * 180
    exchange = [100]*180
    return [oil,freight_outward,freight_return,exchange]

def fitness_function(rule):
    oil_price_data,freight_outward_data,freight_return_data,exchange_rate_data = generate_specific_scenario()
    fitness = 0
    ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
    for year in range(VESSEL_LIFE_TIME):
        cash_flow = 0
        for month in range(12):
            current_oil_price = oil_price_data[year*12+month]
            current_freight_rate_outward = freight_outward_data[year*12+month]['price']
            current_freight_rate_return = freight_return_data[year*12+month]['price']
            total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
            current_exchange = exchange_rate_data[year*12+month]
            result = adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,rule)
            if result[0]:
                ship.change_speed(result[1][0])
                cash_flow += ship.buy_new_ship(freight_outward_data,year*12+month,result[1][1])
                cash_flow += ship.buy_secondhand_ship(freight_outward_data,year*12+month,result[1][2])
                cash_flow += ship.sell_ship(freight_outward_data,year*12+month,result[1][3])
                ship.charter_ship(oil,total_freight,result[1][4],DECISION_CHARTER_IN)
                ship.charter_ship(oil,total_freight,result[1][5],DECISION_CHARTER_OUT)
                if ship.charter_flag == True:
                    cash_flow += ship.charter()
                    ship.end_charter()
            cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
            cash_flow += ship.add_age()
            ship.change_speed(INITIAL_SPEED)
        DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
        cash_flow *= exchange_rate_data[year*12+11]
        fitness += cash_flow / DISCOUNT
    ship.sell_ship(freight_outward_data,VESSEL_LIFE_TIME*12-1,ship.exist_number)
    fitness -= INITIAL_COST_OF_SHIPBUIDING*INITIAL_NUMBER_OF_SHIPS*exchange_rate_data[0]
    fitness /= HUNDRED_MILLION
    fitness /= INITIAL_NUMBER_OF_SHIPS
    return fitness

rule = [[0, 0, 1, 1], [1, 0, 1, 1], [0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [1, 0, 0, 1], 2, 2, 1, 1, 1, 1, [-0.23538951955387183, 0.0]]
f = fitness_function(rule)
print(f)
