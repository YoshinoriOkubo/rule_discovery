import numpy as np
import sys
sys.path.append('../models')
from oil_price import Sinario
from freight_rate_outward import FreightOutward
from freight_rate_return import FreightReturn
from exchange_rate import ExchangeRate
import matplotlib.pyplot as plt
from ga import GA
import time
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

generated_sinario = load_generated_sinario()
oil_data = generated_sinario[0]
freight_outward_data = generated_sinario[1]
freight_return_data = generated_sinario[2]
exchange_data = generated_sinario[3]
ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
            TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
            DECISION_CHARTER_IN)
rule = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0], [0, 0, 0, 0], [0.5869416810331666, 0.29862223356524636]]
e,sigma = ga.fitness_function(rule)
print(e)
rule = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [1, 1], [0, 0, 0, 1], [0.5869416810331666, 0.29862223356524636]]
e,sigma = ga.fitness_function(rule)
print(e)
