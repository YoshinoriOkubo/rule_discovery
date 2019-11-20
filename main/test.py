import numpy as np
import sys
sys.path.append('../models')
from ship import Ship
import time
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

def generate_specific_scenario():
    oil = [50]*180
    freight_outward = [{'price':400}]*180
    freight_return = [{'price':200}] * 180
    exchange = [100]*180
    return [oil,freight_outward,freight_return,exchange]

def fitness_function(rule):
    oil_price_data,freight_rate_outward_data,freight_rate_return_data,exchange_rate_data,demand_data,supply_data = load_generated_sinario()
    Record = []
    f_sunc = 0
    number = 0
    f = 0
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
        for year in range(DEFAULT_PREDICT_YEARS):
            cash_flow = 0
            for month in range(12):
                current_oil_price = oil_price_data[pattern][year*12+month]['price']
                current_freight_rate_outward = freight_rate_outward_data[pattern][year*12+month]['price']
                f += current_freight_rate_outward
                current_freight_rate_return = freight_rate_return_data[pattern][year*12+month]['price']
                total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                current_exchange = exchange_rate_data[pattern][year*12+month]['price']
                current_demand = demand_data[pattern][year*12+month]['price']
                current_supply = supply_data[pattern][year*12+month]['price']
                result = adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,rule)
                if result[0]:
                    cash_flow += ship.buy_new_ship(freight_rate_outward_data[pattern],year*12+month,result[1][0])
                    cash_flow += ship.buy_secondhand_ship(freight_rate_outward_data[pattern],year*12+month,result[1][1])
                    cash_flow += ship.sell_ship(freight_rate_outward_data[pattern],year*12+month,result[1][2])
                    f_sunc += current_freight_rate_outward
                    number += 1
                    ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][3],DECISION_CHARTER_IN)
                    ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][4],DECISION_CHARTER_OUT)
                    if ship.charter_flag == True:
                        cash_flow += ship.charter()
                        ship.end_charter()
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
                ship.change_speed(INITIAL_SPEED)
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_rate_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        ship.sell_ship(freight_rate_outward_data[pattern],DEFAULT_PREDICT_YEARS*12-1,ship.exist_number)
        fitness /= HUNDRED_MILLION
        fitness /= INITIAL_NUMBER_OF_SHIPS
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    if number > 0:
        f_ave = f_sunc / number
    else:
        f_ave = None
    #print(f/(DEFAULT_PREDICT_PATTERN_NUMBER*180))
    return [e,sigma,f_ave]

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

each_rule = [0,50,1300,2000,100,130,97,105,0,1,0,0,0,[2.074606535,0.658025584]]
e,sigma,f_ave = fitness_function(each_rule)
print(e,f_ave)
