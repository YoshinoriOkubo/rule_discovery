import numpy as np
import sys
sys.path.append('../models')
from oil_price import Sinario
from freight_rate_outward import FreightOutward
from freight_rate_return import FreightReturn
import matplotlib.pyplot as plt
from ga import GA
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *
from ship import Ship

rule =

sinario = Sinario()
sinario.generate_sinario()
freight_outward = FreightOutward()
freight_outward.generate_sinario()
freight_return = FreightReturn()
freight_return.generate_sinario()
ga = GA(sinario.predicted_data,freight_outward.predicted_data,freight_return.predicted_data,TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,DECISION_SELL)

average_fitness = 0
for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
    ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
    ship_exist = True
    for year in range(15):
        cash_flow = 0
        if ship_exist:
            for month in range(12):
                if ship_exist:
                    current_oil_price = sinario.predicted_data[pattern][year*12+month]['price']
                    current_freight_rate_outward = freight_outward.predicted_data[pattern][year*12+month]['price']
                    current_freight_rate_return = freight_return.predicted_data[pattern][year*12+month]['price']
                    freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    result = ga.adapt_rule(current_oil_price,freight,rule)
                    if result[0] and result[1] == ACTION_SELL:
                        cash_flow += INITIAL_COST_OF_SHIPBUIDING*(1 - (year*12+month)/180)
                        ship_exist = False
                        print('sell')
                    else:
                        cash_flow += ship.calculate_income_per_month(current_oil_price,freight)
    DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
    average_fitness += cash_flow / DISCOUNT
    ship.chagne_speed_to_initial()
average_fitness /= DEFAULT_PREDICT_PATTERN_NUMBER
average_fitness /= 100000000
print(average_fitness)
