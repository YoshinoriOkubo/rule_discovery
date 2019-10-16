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
import time


f = FreightOutward()
f.generate_sinario()
f.depict()
f2 = FreightReturn()
f2.generate_sinario()
f2.depict()
