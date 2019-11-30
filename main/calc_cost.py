import csv
import sys
import random
import matplotlib.pyplot as plt
sys.path.append('../models')
from ship import Ship
sys.path.append('../public')
from my_modules import *
from constants  import *

def fitness_function_ave():
    Record = []
    #data = []
    for pattern in range(1):
        fitness = 0
        #fitness = -INITIAL_COST_OF_SHIPBUIDING
        #ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,1)
        #ship.agelist[0] = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
        for i in range(len(ship.agelist)):
            if ship.agelist[i] == 0:
                fitness -= INITIAL_COST_OF_SHIPBUIDING*0.5*(1+1)*(1 + INDIRECT_COST)
            else:
                fitness -= INITIAL_COST_OF_SHIPBUIDING*ship.age_impact(ship.agelist[i])*1*(1 + INDIRECT_COST)
        for year in range(DEFAULT_PREDICT_YEARS):
            cash_flow = 0
            for month in range(12):
                current_oil_price = 20
                current_demand = 10.4
                current_freight_rate_outward = 1103
                current_freight_rate_return = 750
                total_freight =( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                current_supply = 4862
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
                #data.append(cash_flow/(INITIAL_COST_OF_SHIPBUIDING))
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            fitness += cash_flow / DISCOUNT
        Record.append(fitness)
    #x = range(DEFAULT_PREDICT_YEARS*12)
    #plt.plot(x,data[0:360])
    #plt.show()
    e, sigma = calc_statistics(Record)
    return [e,sigma]

def fitness_function():
    Record = []
    #data = []
    oil_price_data,freight_rate_outward_data,freight_rate_return_data,exchange_rate_data,demand_data,supply_data = load_generated_sinario()
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        fitness = -INITIAL_COST_OF_SHIPBUIDING
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,1)
        ship.agelist[0] = 0
        for year in range(DEFAULT_PREDICT_YEARS):
            cash_flow = 0
            if year >= PAYBACK_PERIOD and ship.exist_number <= 0:
                    break
            for month in range(0,12,TIME_STEP):
                current_oil_price = oil_price_data[pattern][year*12+month]['price']
                current_freight_rate_outward = freight_rate_outward_data[pattern][year*12+month]['price']
                current_freight_rate_return = freight_rate_return_data[pattern][year*12+month]['price']
                total_freight = ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                #current_exchange = exchange_rate_data[pattern][year*12+month]['price']
                current_demand = demand_data[pattern][year*12+month]['price']
                current_supply = supply_data[pattern][year*12+month]['price']
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
                #data.append(cash_flow/(INITIAL_COST_OF_SHIPBUIDING))
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            fitness += cash_flow / DISCOUNT
        Record.append(fitness)
    #x = range(DEFAULT_PREDICT_YEARS*12)
    #plt.plot(x,data[0:360])
    #plt.show()
    e, sigma = calc_statistics(Record)
    return [e,sigma]
#print(fitness_function_ave()[0]/INITIAL_COST_OF_SHIPBUIDING)
print(fitness_function()[0]/INITIAL_COST_OF_SHIPBUIDING)
