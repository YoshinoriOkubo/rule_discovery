import numpy as np
import sys
sys.path.append('../models')
from oil_price import Sinario
from freight_rate_outward import FreightOutward
from freight_rate_return import FreightReturn
from ga import GA
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *
import matplotlib.pyplot as plt

#'''
sinario = Sinario()
sinario.generate_sinario()
freight_outward = FreightOutward()
freight_outward.generate_sinario()
#freight_outward.depict()
freight_return = FreightReturn()
freight_return.generate_sinario()
#freight_return.depict()
total_freight = []
for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
    total_freight.append([])
    for x in range(VESSEL_LIFE_TIME * 12):
        f = 0.5*(freight_outward.predicted_data[pattern][x]['price'] * LOAD_FACTOR_ASIA_TO_EUROPE + freight_return.predicted_data[pattern][x]['price'] * LOAD_FACTOR_EUROPE_TO_ASIA)
        total_freight[pattern].append(f)
    _x = range(0,VESSEL_LIFE_TIME*12)
    plt.plot(_x, total_freight[pattern], marker='o',label='price')
    plt.title('Transition of total freight', fontsize = 20)
    plt.xlabel('month', fontsize = 16)
    plt.ylabel('total freight rate value', fontsize = 16)
    plt.tick_params(labelsize=14)
    plt.grid(True)
    plt.legend(loc = 'lower right')
plt.show()
plt.close()
#s'''
