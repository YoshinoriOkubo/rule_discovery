# for testing whether or not , buying secondhand vessel is good in terms of profits

import time
import numpy as np
from multiprocessing import Pool
import multiprocessing as multi
import sys
sys.path.append('../models')
from ship import Ship
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

def process(TIME,oil_price_data,freight_rate_outward_data,freight_rate_homeward_data,exchange_rate_data,demand_data,supply_data,newbuilding_data,secondhand_data):
    e,sigma,f_ave = fitness_function(TIME,oil_price_data,freight_rate_outward_data,freight_rate_homeward_data,exchange_rate_data,demand_data,supply_data,newbuilding_data,secondhand_data)
    return[e,sigma,f_ave]

def wrapper_process(args):
    return process(*args)

def multiprocessing():
    num_pool = multi.cpu_count()
    num_pool = int(num_pool*0.9)
    oil_price_data,freight_rate_outward_data,freight_rate_homeward_data,exchange_rate_data,demand_data,supply_data,newbuilding_data,secondhand_data = load_generated_sinario(TRAIN_DATA_SET)
    e_all = 0
    tutumimono = [[time,oil_price_data,freight_rate_outward_data,freight_rate_homeward_data,exchange_rate_data,demand_data,supply_data,newbuilding_data,secondhand_data] for time in range(180)]
    with Pool(num_pool) as pool:
        p = pool.map(wrapper_process, tutumimono)
        for element in p:
            e_all += element[0]
    print('平均',e_all/180,'億円')


def fitness_function(TIME,oil_price_data,freight_rate_outward_data,freight_rate_homeward_data,exchange_rate_data,demand_data,supply_data,newbuilding_data,secondhand_data):
    Record = []
    f_sunc = 0
    number = 0
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,0)
        for year in range(DEFAULT_PREDICT_YEARS):
            cash_flow = 0
            if year >= PAYBACK_PERIOD and ship.exist_number <= 0:
                    break
            for month in range(0,12,TIME_STEP):
                current_oil_price = oil_price_data[pattern][year*12+month]['price']
                current_freight_rate_outward = freight_rate_outward_data[pattern][year*12+month]['price']
                current_freight_rate_homeward = freight_rate_homeward_data[pattern][year*12+month]['price']
                total_freight = ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_homeward * LOAD_FACTOR_EUROPE_TO_ASIA)
                current_exchange = exchange_rate_data[pattern][year*12+month]['price']
                current_demand = demand_data[pattern][year*12+month]['price']
                current_supply = supply_data[pattern][year*12+month]['price']
                current_newbuilding = newbuilding_data[pattern][year*12+month]['price']
                current_secondhand = secondhand_data[pattern][year*12+month]['price']
                if year*12+month == TIME:
                    #cash_flow += ship.buy_new_ship(current_newbuilding,1)
                    cash_flow += ship.buy_secondhand_ship(current_secondhand,1)
                    f_sunc += current_freight_rate_outward
                    number += 1
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
    multiprocessing()
    '''
    oil_price_data,freight_rate_outward_data,freight_rate_homeward_data,exchange_rate_data,demand_data,supply_data,newbuilding_data,secondhand_data = load_generated_sinario()
    e_all = 0
    for time in range(180):
        e,sigma,f_ave = fitness_function(time,oil_price_data,freight_rate_outward_data,freight_rate_homeward_data,exchange_rate_data,demand_data,supply_data,newbuilding_data,secondhand_data)
        e_all += e
        print(e,'億円','平均運賃',f_ave)
    print('平均',e_all/180,'億円')
    '''

if __name__ == "__main__":
    start = time.time()
    main()
    print(time.time() - start, 'second')
