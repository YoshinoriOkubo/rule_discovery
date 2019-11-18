import csv
import sys
import random
sys.path.append('../models')
from ship import Ship
sys.path.append('../public')
from my_modules import *
from constants  import *

def load_ship_rules():
    path = '../output/ship_one_rule.csv'
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

def select_rules(rule,oil,freight,exchange,own_ship):
    max_fitness = -10
    result = None
    for one in rule:
        if adapt_rule(oil,freight,exchange,own_ship,one):
            if max_fitness < one[-2] or (max_fitness == one[-2] and random.randint(0,1) < 0.5):
                result = one
                max_fitness = one[-2]
            else:
                pass
    return result

def adapt_rule(oil_price,freight,exchange,own_ship,rule,actionlist=None):
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

def fitness_function(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,rule,actionlist):
    Record = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
        for i in range(len(ship.agelist)):
            if ship.agelist[i] == 0:
                fitness -= INITIAL_COST_OF_SHIPBUIDING*0.5*(1+ship.freight_impact(freight_outward_data,0))*(1 + INDIRECT_COST)
            else:
                fitness -= INITIAL_COST_OF_SHIPBUIDING*ship.age_impact(ship.agelist[i])*ship.freight_impact(freight_outward_data,0)*(1 + INDIRECT_COST)
        fitness *= exchange_data[pattern][0]['price']
        for year in range(VESSEL_LIFE_TIME):
            cash_flow = 0
            for month in range(12):
                current_oil_price = oil_data[pattern][year*12+month]['price']
                current_freight_rate_outward = freight_outward_data[pattern][year*12+month]['price']
                current_freight_rate_return = freight_return_data[pattern][year*12+month]['price']
                total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                current_exchange = exchange_data[pattern][year*12+month]['price']
                current_demand = demand_data[pattern][year*12+month]['price']
                current_supply = supply_data[pattern][year*12+month]['price']
                rule_selected = select_rules(rule,current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number)
                result = adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,rule_selected,actionlist)
                if result[0]:
                    ship.change_speed(result[1][0])
                    cash_flow += ship.buy_new_ship(freight_outward_data[pattern],year*12+month,result[1][0])
                    cash_flow += ship.buy_secondhand_ship(freight_outward_data[pattern],year*12+month,result[1][1])
                    cash_flow += ship.sell_ship(freight_outward_data[pattern],year*12+month,result[1][2])
                    ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][3],DECISION_CHARTER_IN)
                    ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][4],DECISION_CHARTER_OUT)
                    if ship.charter_flag == True:
                        cash_flow += ship.charter()
                        ship.end_charter()
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
                ship.change_speed(INITIAL_SPEED)
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        ship.sell_ship(freight_outward_data[pattern],VESSEL_LIFE_TIME*12-1,ship.exist_number)
        fitness /= HUNDRED_MILLION
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma]

def main():
    actionlist = [[0]*4,[0]*4,[0]*4,[0]*4,[0]*4,[0]*4]
    rule = load_ship_rules()
    oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data = load_generated_sinario()
    e,sigma = fitness_function(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,rule,actionlist)
    print(e)

if __name__ == "__main__":
    main()
