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


sinario = Sinario()
sinario.generate_sinario()
sinario.depict()
freight_outward = FreightOutward()
freight_outward.generate_sinario()
freight_outward.depict()
freight_return = FreightReturn()
freight_return.generate_sinario()
freight_return.depict()
ga = GA(sinario.predicted_data,freight_outward.predicted_data,freight_return.predicted_data,TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,DECISION_SPEED)
ga.execute_GA()
ga.depict()

#x = range(180)
#y = ga.speed_history
#for e in y:
#    print(e)
#plt.plot(x, y, marker='o',label='best')
#plt.title('Transition of fitness', fontsize = 20)
#plt.xlabel('generation', fontsize = 16)
#plt.ylabel('fitness value', fontsize = 16)
#plt.tick_params(labelsize=14)
#plt.grid(True)
#plt.show()
