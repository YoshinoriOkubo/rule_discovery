import csv
import sys
import random
import math
import matplotlib.pyplot as plt
sys.path.append('../models')
from ship import Ship
sys.path.append('../public')
from my_modules import *
from constants  import *

def adapt_rule(oil_price,freight,exchange,own_ship,rule,ship,supply,strategy=None):
    if type(strategy) is list:
        result = []
        for each_strategy in strategy:
            if each_strategy == 100:
                result.append(1)
            elif each_strategy == 200:
                if freight > FREIGHT_RATE_LIST[6]:
                    result.append(1)
                else:
                    result.append(0)
            elif each_strategy == 300:
                if freight < FREIGHT_RATE_LIST[2]:
                    result.append(1)
                else:
                    result.append(0)
            elif each_strategy == 400:
                result.append(0)
        return result
    else:
        if strategy == 0 and ship.init_share > ship.calc_future_ship()/supply:
            return[True,1]
        elif strategy == 1 and ship.init_share > ship.total_number/supply:
            return[True,1]
        return [False]

def fitness_function(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,rule,strategy):
    Record = []
    data = []
    average_ship_number = 0
    try_number = 0
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        try_number += 1
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
        for year in range(DEFAULT_PREDICT_YEARS):
            cash_flow = 0
            if year >= PAYBACK_PERIOD and ship.exist_number <= 0:
                    break
            for month in range(0,12,TIME_STEP):
                current_oil_price = oil_data[pattern][year*12+month]['price']
                current_freight_rate_outward = freight_outward_data[pattern][year*12+month]['price']
                current_freight_rate_return = freight_homeward_data[pattern][year*12+month]['price']
                total_freight = ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                current_exchange = exchange_data[pattern][year*12+month]['price']
                current_demand = demand_data[pattern][year*12+month]['price']
                current_supply = supply_data[pattern][year*12+month]['price']
                current_newbuilding = newbuilding_data[pattern][year*12+month]['price']
                current_secondhand = secondhand_data[pattern][year*12+month]['price']
                if year < PAYBACK_PERIOD:
                    result = adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,rule,ship,current_supply,strategy)
                    if type(strategy) is list:
                        cash_flow += ship.buy_new_ship(current_newbuilding,result[0])
                        cash_flow += ship.buy_secondhand_ship(current_secondhand,result[1])
                        cash_flow += ship.sell_ship(current_secondhand,result[2])
                    else:
                        if result[0]:
                            if strategy == 0:
                                cash_flow += ship.buy_new_ship(current_newbuilding,result[1])
                            elif strategy == 1:
                                cash_flow += ship.buy_secondhand_ship(current_secondhand,result[1])
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
                if year == PAYBACK_PERIOD - 1 and month == 11:
                    average_ship_number += ship.total_number
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        fitness /= HUNDRED_MILLION
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma,average_ship_number/(try_number)]

def export(result,sign):
    path = '../output/rule-discovered/baseline_{}.csv'.format(sign)
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['New ship','Secondhand ship','sell ship','profit','stdev'])
    with open(path, 'a') as f:
        writer = csv.writer(f)
        for row in result:
            writer.writerow(row)

def main():
    rule = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
    always = 100
    if_high = 200
    if_low = 300
    no = 400
    dict = {always:'always',if_high:'if_high',if_low:'if_low',no:'no'}
    share_new = 0
    share_second = 1
    d = {share_new:'share new',share_second:'share_second'}
    for sign in [TRAIN_DATA_SET,TEST_DATA_SET]:
        result = []
        oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data = load_generated_sinario(sign)
        for new in [always,if_high,if_low,no]:
            for second in [always,if_high,if_low,no]:
                for sell in [always,if_high,if_low,no]:
                    strategy = [new, second, sell]
                    e,sigma,average_ship_number = fitness_function(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,rule,strategy)
                    result.append([dict[strategy[0]],dict[strategy[1]],dict[strategy[2]],e,math.sqrt(sigma)])
        for strategy in [share_new,share_second]:
            e,sigma,average_ship_number = fitness_function(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,rule,strategy)
            result.append([d[strategy],d[strategy],d[strategy],e,math.sqrt(sigma)])
        #result.sort(key=lambda x:x[-2],reverse = True)
        print(result[0])
        export(result,sign)

if __name__ == "__main__":
    main()
