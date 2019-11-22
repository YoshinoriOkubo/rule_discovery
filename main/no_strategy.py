import csv
import sys
import random
import matplotlib.pyplot as plt
sys.path.append('../models')
from ship import Ship
sys.path.append('../public')
from my_modules import *
from constants  import *

def adapt_rule(oil_price,freight,exchange,own_ship,rule,ship,type=None):
    if type is None:
        if own_ship < 100:
            return [True, 1]
            #return[True,100-own_ship]
    else:
        if True:
            number = 0
            for index in range(len(ship.agelist)):
                if ship.agelist[index] == 180 - ORDER_TIME:
                    number += 1
            return [True,number]
    return [False]

def fitness_function(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,rule,type):
    Record = []
    data = []
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
                result = adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,rule,ship)
                if result[0] and year < PAYBACK_PERIOD:
                    if type == 0:
                        pass
                    elif type == 1:
                        cash_flow += ship.buy_new_ship(freight_outward_data[pattern],year*12+month,result[1])
                    elif type == 2:
                        cash_flow += ship.buy_secondhand_ship(freight_outward_data[pattern],year*12+month,result[1])
                    elif type == 3:
                        cash_flow += ship.sell_ship(freight_outward_data[pattern],year*12+month,result[1])
                    elif type == 4:
                        ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1],DECISION_CHARTER_IN)
                    elif type == 5:
                        ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1],DECISION_CHARTER_OUT)
                    #print(ship.total_number)
                    if ship.charter_flag == True:
                        cash_flow += ship.charter()
                        ship.end_charter()
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            cash_flow *= exchange_data[pattern][year*12+11]['price']
            fitness += cash_flow / DISCOUNT
        fitness /= HUNDRED_MILLION
        Record.append(fitness)
    #x = range(DEFAULT_PREDICT_YEARS*12)
    #plt.plot(x,data)
    #plt.show()
    e, sigma = calc_statistics(Record)
    return [e,sigma]

def main():
    rule = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
    oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data = load_generated_sinario()
    nothing = 0
    buy_new = 1
    buy_second = 2
    sell = 3
    charte_in = 4
    charte_out = 5
    dict = {nothing:'Nothing',buy_new:'Buy new',buy_second:'Buy secondhand',sell:'Sell',charte_in:'charte_in',charte_out:'charte_out'}
    for type in [nothing,buy_new,buy_second,sell,charte_in,charte_out]:
        e,sigma = fitness_function(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,rule,type)
        print(dict[type])
        print(e,'億円')


if __name__ == "__main__":
    main()
