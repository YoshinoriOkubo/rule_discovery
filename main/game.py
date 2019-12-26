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

def depict(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,cash_data,pattern,time):
    x_length = 48
    sns.set()
    sns.set_style('whitegrid')
    sns.set_palette('gray')

    fig = plt.figure()
    list1 = [oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,cash_data]
    list2 = ([fig.add_subplot(3, 3, 1),fig.add_subplot(3, 3, 2),fig.add_subplot(3, 3, 3),fig.add_subplot(3, 3, 4),
                fig.add_subplot(3, 3, 5),fig.add_subplot(3, 3, 6),fig.add_subplot(3, 3, 7),fig.add_subplot(3, 3, 8),
                fig.add_subplot(3, 3, 9)])
    list3 = ['oil price','freight outward','freight homeward','exchange rate','ship demand','ship supply','new ship','secondhand','cash data']
    list4 = [59.29,1250,810,119.8,10.65,5103,(1+INDIRECT_COST)*66472628.1,(1+INDIRECT_COST)*42139681.02,0]
    list5 = [0,0,500,0,0,0,0,0,-20*10**7]
    list6 = [200,2000,1250,200,200,10000,10*10**7,10*10**7,20*10**7]
    for (data,ax,name,start,lower,upper) in zip(list1,list2,list3,list4,list5,list6):
        x, y = [-1], [start]
        if time > x_length:
            for i in range(x_length):
                x.append(i)
                y.append(data[pattern][time-(x_length-i)]['price'])
        else:
            for i in range(time+1):
                x.append(i)
                y.append(data[pattern][i]['price'])
        ax.plot(x,y)
        ax.set_xlim([0, x_length])
        ax.set_ylim([lower,upper])
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

def fitness_function(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,time_step):
    Record = []
    cash_data = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        cash_data.append([{'price':0}])
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,0)
        for year in range(0,DEFAULT_PREDICT_YEARS):
            cash_flow = 0
            if year >= PAYBACK_PERIOD and ship.exist_number <= 0:
                    break
            for month in range(0,12,time_step):
                time = year*12+month
                current_oil_price = oil_data[pattern][time]['price']
                current_freight_rate_outward = freight_outward_data[pattern][time]['price']
                current_freight_rate_return = freight_homeward_data[pattern][time]['price']
                total_freight = ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                current_exchange = exchange_data[pattern][time]['price']
                current_demand = demand_data[pattern][time]['price']
                current_supply = supply_data[pattern][time]['price']
                current_newbuilding = newbuilding_data[pattern][time]['price']
                current_secondhand = secondhand_data[pattern][time]['price']
                if year < PAYBACK_PERIOD and month == 11:
                    print('Now your company own {} ships'.format(ship.exist_number))
                    print('Please enter purcahse number')
                    number = depict(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,cash_data,pattern,time)
                    cash_flow += ship.buy_new_ship(newbuilding_data[pattern][time]['price'],number)
                    #cash_flow += ship.buy_secondhand_ship(secondhand_data[pattern][time]['price'],time,number)
                elif month == 11:
                    depict(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,cash_data,pattern,time)
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply,time_step)
                cash_flow += ship.add_age(time_step)
                cash_data[pattern].append({'price':cash_data[pattern][year*12]['price'] + cash_flow/((1 + DISCOUNT_RATE) ** (year + 1))})
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        fitness /= HUNDRED_MILLION# one hundred millon JPY
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma]

def main():
    time_step = 1
    oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data = load_generated_sinario(TEST_DATA_SET)
    e,sigma = fitness_function(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,time_step)
    print('profit = ',e)

if __name__ == "__main__":
    main()
    #input_line1 = input()
    #print(input_line1 + " is written")
