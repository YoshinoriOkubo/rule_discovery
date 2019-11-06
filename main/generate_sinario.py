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

start = time.time()

sinario = Sinario()
sinario.generate_sinario()
freight_outward = FreightOutward()
freight_outward.generate_sinario()
freight_return = FreightReturn(freight_outward.predicted_data)
freight_return.generate_sinario()
exchange_rate = ExchangeRate()
exchange_rate.generate_sinario()

depict_scenario(sinario,freight_outward,freight_return,exchange)
depict_whole_scenario(sinario,freight_outward,exchange)
depict_distribution(sinario,freight_outward,exchange)

print(time.time()-start)
