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

sinario = Sinario()
sinario.generate_sinario()
sinario.depict()
freight_outward = FreightOutward()
freight_outward.generate_sinario()
freight_outward.depict()
freight_return = FreightReturn(freight_outward.predicted_data)
freight_return.generate_sinario()
freight_return.depict()
exchange_rate = ExchangeRate()
exchange_rate.generate_sinario()
exchange_rate.depict()

ga = GA(sinario.predicted_data,freight_outward.predicted_data,freight_return.predicted_data,exchange_rate.predicted_data,
            TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
            DECISION_CHARTER)
e,sigma = ga.fitness_function([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[1,1],[0,0,0,0],[0,0]])
print('0 ships')
print(e)

e,sigma = ga.fitness_function([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[1,1],[0,0,0,1],[0,0]])
print('5 ships')
print(e)
e,sigma = ga.fitness_function([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[1,1],[1,0,0,0],[0,0]])
print('100 ships')
print(e)
print('100 ships with future eye')
print(ga.full_search_method_charter())
