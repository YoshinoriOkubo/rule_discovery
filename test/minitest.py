import numpy as np
import sys
sys.path.append('../models')
from freight_rate_outward import FreightOutward
from ga import GA
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

x = FreightOutward()
x.generate_sinario(DERIVE_SINARIO_MODE['binomial'])
print(x.predicted_data)
