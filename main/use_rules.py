import csv
import sys
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
            for i in range(0,int(len(temp)/3),3):
                list = []
                for x in range(3):
                    if x % 3 == 0 or x % 3 == 1:
                        list.append([])
                        for j in range(8):
                            list[x].append(int(temp[i+x][j]))
                    else:
                        list.append([])
                        for k in range(2):
                            list[-1].append(float(temp[-1][k]))
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
    return rule

def select_rules(rule,oil,freight,exchange,own_ship,type):
    max_fitness = -100
    result = None
    for one in rule:
        if type != 2:
            if adapt_rule(oil,freight,exchange,own_ship,one,type)[0]:
                if max_fitness < one[-2] or (max_fitness == one[-2] and random.randint(0,1) < 0.5):
                    result = one
                    max_fitness = one[-2]
                else:
                    pass
        else:
            r = adapt_rule(oil,freight,exchange,own_ship,one,type)
            if r[0][0] == True or r[0][1] == True:
                if max_fitness < one[-1][0] or (max_fitness == one[-1][0] and random.randint(0,1) < 0.5):
                    result = one
                    max_fitness = one[-1][0]
                else:
                    pass
    return result

def adapt_rule(oil_price,freight,exchange,own_ship,rule,type,actionlist=None):
    if type != 2:
        if rule is None:
            return [False]
        a,b = rule[0],rule[1]
        if a <= oil_price and oil_price <= b:
            c,d = rule[2],rule[3]
            if c <= freight and freight <= d:
                e,f = rule[4],rule[5]
                if e <= exchange and exchange <= f:
                    g,h = rule[6],rule[7]
                    if g <= own_ship and own_ship <= h:
                        result = [True]
                        result.append([])
                        result[1].append(PURCHASE_NUMBER[int(rule[8])])
                        result[1].append(PURCHASE_NUMBER[int(rule[9])])
                        result[1].append(SELL_NUMBER[int(rule[10])])
                        result[1].append(CHARTER_IN_NUMBER[int(rule[11])])
                        result[1].append(CHARTER_OUT_NUMBER[int(rule[12])])
                        if actionlist is not None:
                            actionlist[0][int(rule[8])] += 1
                            actionlist[1][int(rule[9])] += 1
                            actionlist[2][int(rule[10])] += 1
                            actionlist[3][int(rule[11])] += 1
                            actionlist[4][int(rule[12])] += 1
                        return result
        return [False]
    else:
        if rule is None:
            return [[False],[False]]
        result = [[False,0],[False,0]]
        for which_action in range(2):
            rule_s = rule[which_action]
            a,b = rule_s[0],rule_s[1]
            if a <= oil_price and oil_price <= b:
                c,d = rule_s[2],rule_s[3]
                if c <= freight and freight <= d:
                    e,f = rule_s[4],rule_s[5]
                    if e <= exchange and exchange <= f:
                        g,h = rule_s[6],rule_s[7]
                        if g <= own_ship and own_ship <= h:
                            result[which_action][0] = True
                            result[which_action][1] = 1
                            if actionlist is not None:
                                actionlist[which_action][1] += 1
                            #result[1].append(PURCHASE_NUMBER[self.actionlist[0]])
                            #result[1].append(PURCHASE_NUMBER[self.actionlist[1]])
                            #result[1].append(SELL_NUMBER[self.actionlist[2]])
                            #result[1].append(CHARTER_IN_NUMBER[self.actionlist[3]])
                            #result[1].append(CHARTER_OUT_NUMBER[self.actionlist[4]])
        return result

def fitness_function(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,rule,actionlist,type):
    Record = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
        for i in range(len(ship.agelist)):
            if ship.agelist[i] == 0:
                fitness -= INITIAL_COST_OF_SHIPBUIDING*0.5*(1+ship.freight_impact(freight_outward_data,0))*(1 + INDIRECT_COST)
            else:
                fitness -= INITIAL_COST_OF_SHIPBUIDING*ship.age_impact(ship.agelist[i])*ship.freight_impact(freight_outward_data,0)*(1 + INDIRECT_COST)
        fitness *= exchange_data[pattern][11]['price']
        for year in range(DEFAULT_PREDICT_YEARS):
            cash_flow = 0
            for month in range(12):
                current_oil_price = oil_data[pattern][year*12+month]['price']
                current_freight_rate_outward = freight_outward_data[pattern][year*12+month]['price']
                current_freight_rate_return = freight_return_data[pattern][year*12+month]['price']
                total_freight = ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                current_exchange = exchange_data[pattern][year*12+month]['price']
                current_demand = demand_data[pattern][year*12+month]['price']
                current_supply = supply_data[pattern][year*12+month]['price']
                rule_selected = select_rules(rule,current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,type)
                result = adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,rule_selected,type,actionlist)
                if type != 2:
                    if result[0] and year < PAYBACK_PERIOD:
                        ship.change_speed(result[1][0])
                        cash_flow += ship.buy_new_ship(freight_outward_data[pattern],year*12+month,result[1][0])
                        cash_flow += ship.buy_secondhand_ship(freight_outward_data[pattern],year*12+month,result[1][1])
                        cash_flow += ship.sell_ship(freight_outward_data[pattern],year*12+month,result[1][2])
                        ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][3],DECISION_CHARTER_IN)
                        ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][4],DECISION_CHARTER_OUT)
                        if ship.charter_flag == True:
                            cash_flow += ship.charter()
                            ship.end_charter()
                else:
                    if result[0][0] and year < PAYBACK_PERIOD:
                        cash_flow += ship.buy_secondhand_ship(freight_outward_data[pattern],year*12+month,result[0][1])
                        pass
                    if result[1][0] and year < PAYBACK_PERIOD:
                        cash_flow += ship.sell_ship(freight_outward_data[pattern],year*12+month,result[1][1])
                        pass
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        fitness /= HUNDRED_MILLION
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma]

def main():
    actionlist = [[0]*4,[0]*4,[0]*4,[0]*4,[0]*4]
    one_rule = 0
    multi_rule = 1
    integrate = 2
    type = 0
    rule = load_ship_rules(type)
    oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data = load_generated_sinario()
    e,sigma = fitness_function(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,rule,actionlist,type)
    print(e,'億円')
    print(actionlist)

if __name__ == "__main__":
    main()
