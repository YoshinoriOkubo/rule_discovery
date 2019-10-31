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

start = time.time()

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

print(time.time()-start)
