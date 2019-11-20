import csv
import sys
import random
sys.path.append('../models')
from ship import Ship
sys.path.append('../public')
from my_modules import *
from constants  import *

def fitness_function_ave():
    Record = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,1)
        ship.agelist[0] = 0
        for year in range(VESSEL_LIFE_TIME):
            cash_flow = 0
            for month in range(12):
                current_oil_price = 41.269672901071544
                current_demand = 10.773913037102997
                current_freight_rate_outward = 1468.1572093902791
                current_freight_rate_return = 909.3065453615974
                total_freight =( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                current_supply = 5292.034884937528
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            fitness += cash_flow / DISCOUNT
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma]

def fitness_function():
    Record = []
    oil_price_data,freight_rate_outward_data,freight_rate_return_data,exchange_rate_data,demand_data,supply_data = load_generated_sinario()
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        fitness = 0
        ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,1)
        ship.agelist[0] = 0
        for year in range(VESSEL_LIFE_TIME):
            cash_flow = 0
            for month in range(12):
                current_oil_price = oil_price_data[pattern][year*12+month]['price']
                current_freight_rate_outward = freight_rate_outward_data[pattern][year*12+month]['price']
                current_freight_rate_return = freight_rate_return_data[pattern][year*12+month]['price']
                total_freight = ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                #current_exchange = exchange_rate_data[pattern][year*12+month]['price']
                current_demand = demand_data[pattern][year*12+month]['price']
                current_supply = supply_data[pattern][year*12+month]['price']
                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                cash_flow += ship.add_age()
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            fitness += cash_flow / DISCOUNT
        Record.append(fitness)
    e, sigma = calc_statistics(Record)
    return [e,sigma]
print(fitness_function_ave())
#print(fitness_function())
