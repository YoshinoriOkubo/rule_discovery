import numpy as np
import sys
sys.path.append('../models')
from oil_price import Sinario
from ga import GA
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *


x = Sinario()
x.generate_sinario(DERIVE_SINARIO_MODE['binomial'])
ga = GA(x.predicted_data)
ga.execute_GA()
