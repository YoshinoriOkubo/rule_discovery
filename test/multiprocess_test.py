import numpy as np
import sys
sys.path.append('../models')
from oil_price import Sinario
from freight_rate_outward import FreightOutward
from freight_rate_return import FreightReturn
from exchange_rate import ExchangeRate
from ship import Ship
import matplotlib.pyplot as plt
from ga import GA
import time
from multiprocessing import Pool
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

sinario = Sinario()
sinario.generate_sinario()
freight_outward = FreightOutward()
freight_outward.generate_sinario()
freight_return = FreightReturn(freight_outward.predicted_data)
freight_return.generate_sinario()
exchange_rate = ExchangeRate()
exchange_rate.generate_sinario()
oil_price_data = sinario.predicted_data
freight_rate_outward_data = freight_outward.predicted_data
freight_rate_return_data = freight_return.predicted_data
exchange_rate = exchange_rate.predicted_data
decision = DECISION_SPEED

def convert2to10_in_list(list):
    result = 0
    length = len(list)
    for i in range(len(list)):
        x = length - 1 - i
        result += list[i] * 2 ** (x)
    if len(list) == 4:
        return GRAY_CODE_4[result]
    elif len(list) == 2:
        return GRAY_CODE_2[result]
    elif len(list) == 1:
        return result
    else:
        return None

def adapt_rule(oil_price,freight,exchange,rule):
    if decision == DECISION_INTEGRATE:
        result = []
        for rule_index in range(len(rule)-1):
            rule_for_X = rule[rule_index]
            result.append([False])
            a = OIL_PRICE_LIST[convert2to10_in_list(rule_for_X[0])]
            b = OIL_PRICE_LIST[convert2to10_in_list(rule_for_X[1])]
            if a == b or ( a <= oil_price and oil_price <= b):
                c = FREIGHT_RATE_LIST[convert2to10_in_list(rule_for_X[2])]
                d = FREIGHT_RATE_LIST[convert2to10_in_list(rule_for_X[3])]
                if c == d or ( c <= freight and freight <= d):
                    e = EXCHANGE_RATE_LIST[convert2to10_in_list(rule_for_X[4])]
                    f = EXCHANGE_RATE_LIST[convert2to10_in_list(rule_for_X[5])]
                    if e == f or (e <= exchange and exchange <= f):
                        if RULE_SET[rule_index] == DECISION_SPEED:
                            result[rule_index][0] = True
                            result[rule_index].append(VESSEL_SPEED_LIST[convert2to10_in_list(rule_for_X[-1])])
                        elif RULE_SET[rule_index] == DECISION_SELL:
                            result[rule_index][0] = True
                            result[rule_index].append(SELL_NUMBER[convert2to10_in_list(rule_for_X[-1])])
                        elif RULE_SET[rule_index] == DECISION_CHARTER and rule_for_X[-1][0] != ACTION_STAY:
                            result[rule_index][0] = True
                            result[rule_index].append(CHARTER_PERIOD[convert2to10_in_list(rule_for_X[-2])])
                            result[rule_index].append(CHARTER_NUMBER[convert2to10_in_list(rule_for_X[-1])])
        return result
    else:
        a = OIL_PRICE_LIST[convert2to10_in_list(rule[0])]
        b = OIL_PRICE_LIST[convert2to10_in_list(rule[1])]
        if a == b or ( a <= oil_price and oil_price <= b):
            c = FREIGHT_RATE_LIST[convert2to10_in_list(rule[2])]
            d = FREIGHT_RATE_LIST[convert2to10_in_list(rule[3])]
            if c == d or ( c <= freight and freight <= d):
                e = EXCHANGE_RATE_LIST[convert2to10_in_list(rule[4])]
                f = EXCHANGE_RATE_LIST[convert2to10_in_list(rule[5])]
                if e == f or (e <= exchange and exchange <= f):
                    if decision == DECISION_SPEED:
                        return [True,VESSEL_SPEED_LIST[convert2to10_in_list(rule[-2])]]
                    elif decision == DECISION_SELL:
                        return [True,SELL_NUMBER[convert2to10_in_list(rule[-2])]]
                    elif decision == DECISION_CHARTER:
                        return [True,CHARTER_PERIOD[convert2to10_in_list(rule[-3])],CHARTER_NUMBER[convert2to10_in_list(rule[-2])]]
                    else:
                        print('selected decision item does not exist')
                        sys.exit()
        return [False]

def fitness_function(rule,priority=None):
    Record = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
        for year in range(VESSEL_LIFE_TIME):
            cash_flow = 0
            for month in range(12):
                current_oil_price = oil_price_data[pattern][year*12+month]['price']
                current_freight_rate_outward = freight_rate_outward_data[pattern][year*12+month]['price']
                current_freight_rate_return = freight_rate_return_data[pattern][year*12+month]['price']
                total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                ship.calculate_idle_rate(current_freight_rate_outward)
                current_exchange = exchange_rate[pattern][year*12+month]['price']
                #change by argment
                if decision == DECISION_SPEED:
                    result = adapt_rule(current_oil_price,total_freight,current_exchange,rule)
                    if result[0]:
                        ship.change_speed(result[1])
                    cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                elif decision == DECISION_SELL:
                    result = adapt_rule(current_oil_price,total_freight,current_exchange,rule)
                    if result[0]:
                        cash_flow += ship.sell_ship(freight_rate_outward_data[pattern],year*12+month,result[1])
                    cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                elif decision == DECISION_CHARTER:
                    result = adapt_rule(current_oil_price,total_freight,current_exchange,rule)
                    if result[0] and result[2] > 0:
                        ship.charter_ship(current_oil_price,total_freight,result[2],result[1])
                    cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                    if ship.charter == True:
                        cash_flow += ship.in_charter()
                        ship.end_charter()
                elif decision == DECISION_INTEGRATE:
                    result = adapt_rule(current_oil_price,total_freight,current_exchange,rule)
                    if result[0][0] == True:
                        ship.change_speed(result[0][1])
                    if priority == PRIORITY_SELL_CHARTER:
                        if result[1][0] == True:
                            cash_flow += ship.sell_ship(freight_rate_outward_data[pattern],year*12+month,result[1][1])
                        if result[2][0] == True:
                            ship.charter_ship(current_oil_price,total_freight,result[2][2],result[2][1])
                    elif priority == PRIORITY_CHARTER_SELL:
                        if result[2][0] == True:
                            ship.charter_ship(current_oil_price,total_freight,result[2][2],result[2][1])
                        if result[1][0] == True:
                            cash_flow += ship.sell_ship(freight_rate_outward_data[pattern],year*12+month,result[1][1])
                    cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                    if ship.charter == True:
                        cash_flow += ship.in_charter()
                        ship.end_charter()
            if year < DEPRECIATION_TIME:
                cash_flow -= INITIAL_COST_OF_SHIPBUIDING*INITIAL_NUMBER_OF_SHIPS/DEPRECIATION_TIME
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_rate[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        fitness /= HUNDRED_MILLION
        fitness /= INITIAL_NUMBER_OF_SHIPS
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma]

rule = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[1,1],[0,0,0,0],[0,0]]
n = 400
def process(i):
    fitness_function(rule)
start = time.time()
with Pool() as pool:
    pool.map(process, range(n))
print(time.time()-start)

start = time.time()
for i in range(n):
    process(i)
print(time.time()-start)
