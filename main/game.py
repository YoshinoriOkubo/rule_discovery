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

def depict(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,pattern,time):
    sns.set()
    sns.set_style('whitegrid')
    sns.set_palette('gray')

    fig = plt.figure()

    list1 = [oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data]
    list2 = [fig.add_subplot(2, 3, 1),fig.add_subplot(2, 3, 2),fig.add_subplot(2, 3, 3),fig.add_subplot(2, 3, 4),fig.add_subplot(2, 3, 5),fig.add_subplot(2, 3, 6)]
    list3 = ['oil_price','freight_outward','freight_return','exchange_rate','ship_demand','ship_supply']
    list4 = [59.29,1250,810,119.8,10.65,5103]
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
    plt.show()

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

def fitness_function(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data):
    Record = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
        for year in range(2):#VESSEL_LIFE_TIME):
            cash_flow = 0
            for month in range(12):
                current_oil_price = oil_data[pattern][year*12+month]['price']
                current_freight_rate_outward = freight_outward_data[pattern][year*12+month]['price']
                current_freight_rate_return = freight_return_data[pattern][year*12+month]['price']
                total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                current_exchange = exchange_data[pattern][year*12+month]['price']
                current_demand = demand_data[pattern][year*12+month]['price']
                current_supply = supply_data[pattern][year*12+month]['price']
                print('Now your company own {} ships'.format(ship.exist_number))
                print('Please enter purcahse number')
                print('Purchase number is limited to whether 0 or 1')
                depict(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,pattern,year*12+month)
                #sys.exit()
                flag = True
                error = False
                while flag:
                    if error:
                        print('You can enter only 0 or 1')
                    input_line1 = input()
                    if input_line1 == '1' or input_line1 == '0':
                        flag = False
                    error = True
                cash_flow += ship.buy_new_ship(freight_outward_data[pattern],year*12+month,int(input_line1))
                #input_line2 = input()
                #cash_flow += ship.buy_secondhand_ship(freight_outward_data[pattern],year*12+month,int(input_line2))
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
                ship.change_speed(INITIAL_SPEED)
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        ship.sell_ship(freight_outward_data[pattern],VESSEL_LIFE_TIME*12-1,ship.exist_number)
        fitness /= HUNDRED_MILLION
        fitness /= INITIAL_NUMBER_OF_SHIPS
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma]

def main():
    oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data = load_generated_sinario()
    e,sigma = fitness_function(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data)
    print(e)

if __name__ == "__main__":
    main()
    #input_line1 = input()
    #print(input_line1 + " is written")
