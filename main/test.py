# for testing whether or not , buying secondhand vessel is good in terms of profits

import time
import numpy as np
import sys
sys.path.append('../models')
from ship import Ship
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

def adapt_rule(oil_price,freight,exchange,own_ship,rule):
    actionlist = rule[8:13]
    a = rule[0]
    b = rule[1]
    if a <= oil_price and oil_price <= b:
        c = rule[2]
        d = rule[3]
        if c <= freight and freight <= d:
            e = rule[4]
            f = rule[5]
            if e <= exchange and exchange <= f:
                g = rule[6]
                h = rule[7]
                if g <= own_ship and own_ship <= h:
                    result = [True]
                    result.append([])
                    result[1].append(PURCHASE_NUMBER[actionlist[0]])
                    result[1].append(PURCHASE_NUMBER[actionlist[1]])
                    result[1].append(SELL_NUMBER[actionlist[2]])
                    result[1].append(CHARTER_IN_NUMBER[actionlist[3]])
                    result[1].append(CHARTER_OUT_NUMBER[actionlist[4]])
                    return result
    return [False]

def fitness_function(rule,TIME):
    oil_price_data,freight_rate_outward_data,freight_rate_return_data,exchange_rate_data,demand_data,supply_data,newbuilding_data,secondhand_data = load_generated_sinario()
    Record = []
    f_sunc = 0
    number = 0
    f = 0
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,0)
        ship.agelist = []
        for year in range(DEFAULT_PREDICT_YEARS):
            cash_flow = 0
            for month in range(12):
                current_oil_price = oil_price_data[pattern][year*12+month]['price']
                current_freight_rate_outward = freight_rate_outward_data[pattern][year*12+month]['price']
                f += current_freight_rate_outward
                current_freight_rate_return = freight_rate_return_data[pattern][year*12+month]['price']
                total_freight = ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                current_exchange = exchange_rate_data[pattern][year*12+month]['price']
                current_demand = demand_data[pattern][year*12+month]['price']
                current_supply = supply_data[pattern][year*12+month]['price']
                current_newbuilding = newbuilding_data[pattern][year*12+month]['price']
                current_secondhand = secondhand_data[pattern][year*12+month]['price']
                if year*12+month == TIME:
                    #cash_flow += ship.buy_new_ship(current_newbuilding,1)
                    cash_flow += ship.buy_secondhand_ship(current_secondhand,1)
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_rate_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        fitness /= HUNDRED_MILLION
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    if number > 0:
        f_ave = f_sunc / number
    else:
        f_ave = None
    return [e,sigma,f_ave]

def main():
    '''
    path = '../output/ship_rule.csv'
    rule = []
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != 'a':
                list = []
                for index in range(len(row)):
                    if index > 12:
                        list.append(float(row[index]))
                    else:
                        list.append(int(row[index]))
                rule.append(list)
    a = 0
    for each_rule in rule:
        if a == 16:
            print('後半')
        a += 1
        e,sigma,f = fitness_function(each_rule)
        print(e,',',f)
    '''
    rule = [10,140,300,2200,70,200,0,120,0,1,0,0,1,6.939222582318641,5.420854999758004]
    e_all = 0
    for time in range(180):
        e,sigma,f_ave = fitness_function(rule,time)
        e_all += e
        print(e,'億円')
    print('平均',e_all/180,'億円')

if __name__ == "__main__":
    start = time.time()
    main()
    print(time.time() - start, 'second')
