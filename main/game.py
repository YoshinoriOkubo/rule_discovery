import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
import csv
import sys
import random
sys.path.append('../models')
from ship import Ship
sys.path.append('../public')
from my_modules import *
from constants  import *

def make_new_market(freight):
    list = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        list.append([])
        for time in range(DEFAULT_PREDICT_YEARS*12):
            freight_criteria = FREIGHT_3
            if time - 3 < 0:
                freight_three_month_before = FREIGHT_PREV[time-3]
            else:
                freight_three_month_before = freight[pattern][time-3]['price']
            list[pattern].append({'price':(0.5)*(1+INDIRECT_COST)*(1+freight_three_month_before/freight_criteria)})
    return list

def make_secondhand_market(freight):
    list = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        list.append([])
        for time in range(DEFAULT_PREDICT_YEARS*12):
            freight_criteria = FREIGHT_3
            if time - 3 < 0:
                freight_three_month_before = FREIGHT_PREV[time-3]
            else:
                freight_three_month_before = freight[pattern][time-3]['price']
            list[pattern].append({'price':(2/3)*(1+INDIRECT_COST)*(freight_three_month_before/freight_criteria)})
    return list

def make_new_market_from_demand_and_supply(demand,supply):
    list = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        list.append([])
        for time in range(DEFAULT_PREDICT_YEARS*12):
            price = NEW_BUILDING_INCLINATION * demand[pattern][time]['price']/supply[pattern][time]['price'] + NEW_BUILDING_INTERCEPT
            list[pattern].append({'price':price*(1+INDIRECT_COST)})
    return list

def depict_two_market(demand_data,supply_data):
    new = make_new_market_from_demand_and_supply(demand_data,supply_data)
    secondhand = make_secondhand_market_from_demand_and_supply(demand_data,supply_data)
    x = range(360)
    y = []
    pattern = 4
    for i in range(360):
        y.append(new[pattern][i]['price'])
    plt.plot(x,y)
    y = []
    for i in range(360):
        y.append(secondhand[pattern][i]['price'])
    plt.plot(x,y)
    save_dir = '../output/image'
    plt.savefig(os.path.join(save_dir, 'market.png'))


def make_secondhand_market_from_demand_and_supply(demand,supply):
    list = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        list.append([])
        for time in range(DEFAULT_PREDICT_YEARS*12):
            price = SECONDHAND_INCLINATION * demand[pattern][time]['price']/supply[pattern][time]['price'] + SECONDHAND_INTERCEPT
            list[pattern].append({'price':price*(1+INDIRECT_COST)})
    return list

def depict(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,pattern,time):
    sns.set()
    sns.set_style('whitegrid')
    sns.set_palette('gray')

    fig = plt.figure()
    #new = make_new_market(freight_outward_data)
    new = make_new_market_from_demand_and_supply(demand_data,supply_data)
    #secondhand = make_secondhand_market(freight_outward_data)
    secondhand = make_secondhand_market_from_demand_and_supply(demand_data,supply_data)
    list1 = [oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,new,secondhand]
    list2 = ([fig.add_subplot(2, 4, 1),fig.add_subplot(2, 4, 2),fig.add_subplot(2, 4, 3),fig.add_subplot(2, 4, 4),
              fig.add_subplot(2, 4, 5),fig.add_subplot(2, 4, 6),fig.add_subplot(2,4,7),fig.add_subplot(2,4,8)])
    list3 = ['oil_price','freight_outward','freight_homeward','exchange_rate','ship_demand','ship_supply','new_ship','secondhand']
    list4 = [59.29,1250,810,119.8,10.65,5103,1+INDIRECT_COST,(2/3)*(1+INDIRECT_COST)]
    for (data,ax,name,start) in zip(list1,list2,list3,list4):
        x, y = [-1], [start]
        if time > 10:
            for i in range(10):
                x.append(i)
                y.append(data[pattern][time-(10-i)]['price'])
        else:
            for i in range(time+1):
                x.append(i)
                y.append(data[pattern][i]['price'])
        ax.plot(x,y)
        ax.set_title(name)
    # show plots
    fig.tight_layout()
    fig.suptitle("uncertainties in {} period".format(time), fontsize=20)
    plt.subplots_adjust(top=0.80)
    plt.pause(.01)
    flag = True
    error = False
    while flag:
        if error:
            print('You can enter only 0 or 1')
        input_line1 = input()
        if input_line1 == '1' or input_line1 == '0':
            flag = False
        error = True
    plt.close()
    return int(input_line1)

def adapt_rule(oil_price,freight,exchange,own_ship,rule,ship):
    if own_ship != 100:
        return[True,100-own_ship]
    '''
    if True:
        number = 0
        for index in range(len(ship.agelist)):
            if ship.agelist[index] == 180 - ORDER_TIME:
                number += 1
        return [True,number]
    '''
    return [False]

def fitness_function(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data):
    Record = []
    depict_two_market(demand_data,supply_data)
    sys.exit()
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
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
                if year < PAYBACK_PERIOD:
                    print('Now your company own {} ships'.format(ship.exist_number))
                    print('Please enter purcahse number')
                    if year*12 + month == 0:
                        print('Purchase number is limited to whether 0 or 1')
                    number = depict(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,pattern,year*12+month)
                    #cash_flow += ship.buy_new_ship(freight_outward_data[pattern],year*12+month,number)
                    cash_flow += ship.buy_secondhand_ship(freight_outward_data[pattern],year*12+month,number)
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
                ship.change_speed(INITIAL_SPEED)
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        fitness /= HUNDRED_MILLION
        fitness /= INITIAL_NUMBER_OF_SHIPS
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma]

def main():
    oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data = load_generated_sinario()
    e,sigma = fitness_function(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data)
    print(e)

if __name__ == "__main__":
    main()
    #input_line1 = input()
    #print(input_line1 + " is written")
