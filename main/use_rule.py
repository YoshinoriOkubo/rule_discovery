import csv
import sys
import math
import random
sys.path.append('../models')
from ship import Ship
sys.path.append('../public')
from my_modules import *
from constants  import *

def load_ship_rules(type):
    if type == 2:
        path = '../output/rule-discovered/rule.csv'
        rule = []
        with open(path) as f:
            reader = csv.reader(f)
            temp = []
            for row in reader:
                if row[0] != 'a':
                    temp.append(row)
            one_rule_col = DEFAULT_NUM_OF_ACTION_INTEGRATE+1
            for i in range(0,int(len(temp)/one_rule_col),one_rule_col):
                list = []
                for x in range(one_rule_col):
                    list.append([])
                    if (x + 1) % one_rule_col == 0:
                        for j in range(2):
                            list[x].append(float(temp[i+x][j]))
                    else:
                        for k in range(DEFAULT_NUM_OF_CONDITION*2):
                            list[-1].append(float(temp[i+x][k]))
                rule.append(list)
    else:
        if type == 0:
            path = '../output/rule-discovered/ship_one_rule.csv'
        if type == 1:
            path = '../output/rule-discovered/ship_rule.csv'
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
    return rule[0]

def adapt_rule(oil_price,freight,exchange,own_ship,rule,freight_data,time,type,actionlist=None):
    average_freight = 0
    for data_index in range(10):
        if time - data_index < 0:
            average_freight += FREIGHT_PREV[time - data_index]
        else:
            average_freight += freight_data[time - data_index]['price']
    average_freight /= 10
    compare_list = [oil_price,freight,exchange,own_ship,average_freight]
    if type == 2:
        if rule is None:
            return [[False],[False],[False],[False],[False]]
        result = [[False,0],[False,0],[False,0],[False,0],[False,0]]
        for which_action in range(DEFAULT_NUM_OF_ACTION_INTEGRATE):
            rule_s = rule[which_action]
            flag = True
            for cond in range(DEFAULT_NUM_OF_CONDITION):
                lower = rule_s[cond*2]
                upper = rule_s[cond*2+1]
                if (lower < compare_list[cond] or lower == DO_NOT_CARE) and (compare_list[cond] < upper or upper == DO_NOT_CARE):
                    pass
                else:
                    flag = False
            if flag == True:
                result[which_action][0] = True
                result[which_action][1] = 1
                if actionlist is not None:
                    actionlist[which_action][1] += 1
        return result
    else:
        if rule is None:
            return [False]
        flag = True
        for cond in range(DEFAULT_NUM_OF_CONDITION):
            lower = rule[cond*2]
            upper = rule[cond*2+1]
            if (lower < compare_list[cond] or lower == DO_NOT_CARE) and (compare_list[cond] < upper or upper == DO_NOT_CARE):
                pass
            else:
                flag = False
        if flag == True:
            result = [True]
            result.append([])
            result[1].append(PURCHASE_NUMBER[int(rule[-5])])
            result[1].append(PURCHASE_NUMBER[int(rule[-4])])
            result[1].append(SELL_NUMBER[int(rule[-3])])
            result[1].append(CHARTER_IN_NUMBER[int(rule[-2])])
            result[1].append(CHARTER_OUT_NUMBER[int(rule[-1])])
            if actionlist is not None:
                actionlist[0][int(rule[8])] += 1
                actionlist[1][int(rule[9])] += 1          
                actionlist[2][int(rule[10])] += 1
                actionlist[3][int(rule[11])] += 1
                actionlist[4][int(rule[12])] += 1
            return result
        return [False]

def fitness_function(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,rule,actionlist,type):
    Record = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,100)
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
                    current_newbuilding = newbuilding_data[pattern][year*12+month]['price']
                    current_secondhand = secondhand_data[pattern][year*12+month]['price']
                    result = adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,rule,freight_outward_data[pattern],year*12+month,type,actionlist)
                    if type != 2:
                        if result[0]:
                            ship.change_speed(result[1][0])
                            cash_flow += ship.buy_new_ship(current_newbuilding,result[1][0])
                            cash_flow += ship.buy_secondhand_ship(current_secondhand,result[1][1])
                            cash_flow += ship.sell_ship(current_secondhand,result[1][2])
                            ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][3],DECISION_CHARTER_IN)
                            ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][4],DECISION_CHARTER_OUT)
                    else:
                        if result[0][0]:
                            cash_flow += ship.buy_new_ship(current_newbuilding,result[0][1])
                        if result[1][0]:
                            cash_flow += ship.buy_secondhand_ship(current_secondhand,result[1][1])
                        if result[2][0]:
                            cash_flow += ship.sell_ship(current_secondhand,result[2][1])
                        if result[3][0]:
                            ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[3][1],DECISION_CHARTER_IN)
                        if result[4][0]:
                            ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[4][1],DECISION_CHARTER_OUT)
                if ship.charter_flag == True:
                    cash_flow += ship.charter()
                    ship.end_charter()
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        fitness /= HUNDRED_MILLION
        #fitness /= SCALING
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma]

def main():
    actionlist = [[0]*4,[0]*4,[0]*4,[0]*4,[0]*4]
    one_rule = 0
    multi_rule = 1
    integrate = 2
    type = 2
    rule = load_ship_rules(type)
    for sign in [TRAIN_DATA_SET,TEST_DATA_SET]:
        oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data = load_generated_sinario(sign)
        e,sigma = fitness_function(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,rule,actionlist,type)
        print(sign)
        print(e,'億円')
        print(sigma)
        print(actionlist)

if __name__ == "__main__":
    main()
