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
first = time.time()

x = Sinario()
x.generate_sinario()
num = len(x.history_data)
X = range(15*12+num)
for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
    y = []
    for i in range(180+num):
        if i < num:
            y.append(x.history_data[i][1])
        else:
            y.append(x.predicted_data[pattern][i-num]['price'])
    plt.plot(X, y)#,label='pattern {0}'.format(pattern+1))
plt.title('Transition of oil price', fontsize = 20)
plt.xlabel('month', fontsize = 16)
plt.ylabel('oil price', fontsize = 16)
plt.tick_params(labelsize=14)
plt.grid(True)
plt.legend(loc = 'lower right')
plt.xlim(0,600)
plt.ylim(0, 160)
plt.show()


'''
freight_outward = FreightOutward()
freight_return  = FreightReturn()
'''
#x = Sinario()
#x.generate_sinario()
#x.depict()
#print(x.predicted_data)
#'''
'''
y = FreightReturn()
y.generate_sinario()
print(time.time() - first)
_x = range(VESSEL_LIFE_TIME*12)
for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
    _y = []
    for i in range(VESSEL_LIFE_TIME*12):
        _y.append(y.predicted_data[pattern][i]['price'])
    plt.plot(_x, _y)#,label='pattern {0}'.format(pattern+1))
plt.title('Transition of freight rate', fontsize = 20)
plt.xlabel('month', fontsize = 16)
plt.ylabel('freight rate', fontsize = 16)
plt.tick_params(labelsize=14)
plt.grid(True)
plt.legend(loc = 'lower right')
plt.show()
plt.close()
'''
