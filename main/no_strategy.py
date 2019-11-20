import csv
import sys
import random
sys.path.append('../models')
from ship import Ship
sys.path.append('../public')
from my_modules import *
from constants  import *

def adapt_rule(oil_price,freight,exchange,own_ship,rule,ship,type=None):
    if type is None:
        if own_ship != 100:
            return[True,100-own_ship]
    else:
        if True:
            number = 0
            for index in range(len(ship.agelist)):
                if ship.agelist[index] == 180 - ORDER_TIME:
                    number += 1
            return [True,number]
    return [False]

def fitness_function(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,rule):
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
                result = adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,rule,ship)
                if result[0] and year < PAYBACK_PERIOD:
                    #cash_flow += ship.buy_new_ship(freight_outward_data[pattern],year*12+month,result[1])
                    cash_flow += ship.buy_secondhand_ship(freight_outward_data[pattern],year*12+month,result[1])
                    #print(ship.total_number)
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
                ship.change_speed(INITIAL_SPEED)
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        fitness /= HUNDRED_MILLION
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma]

def main():
    rule = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
    oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data = load_generated_sinario()
    e,sigma = fitness_function(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,rule)
    print(e,'100万')

if __name__ == "__main__":
    main()
