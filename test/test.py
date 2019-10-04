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


sinario = Sinario()
sinario.generate_sinario()
sinario.depict()
freight_outward = FreightOutward()
freight_outward.generate_sinario(DERIVE_SINARIO_MODE['binomial'])
freight_outward.depict()
freight_return = FreightReturn()
freight_return.generate_sinario(DERIVE_SINARIO_MODE['binomial'])
freight_return.depict()
ga = GA(sinario.predicted_data,freight_outward.predicted_data,freight_return.predicted_data,TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
ga.execute_GA()
ga.depict_best_individual()
