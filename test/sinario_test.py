import numpy as np
import sys
import os
sys.path.append('../models')
from oil_price import Sinario
from freight_rate_outward import FreightOutward
from freight_rate_return import FreightReturn
from exchange_rate import ExchangeRate
import matplotlib.pyplot as plt
from ga import GA
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *
import time
first = time.time()

oil = Sinario()
oil.generate_sinario()
num = len(oil.history_data)
x = range(15*12+num)
for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
    y = []
    for i in range(180+num):
        if i < num:
            y.append(oil.history_data[i][1])
        else:
            y.append(oil.predicted_data[pattern][i-num]['price'])
    plt.plot(x, y)#,label='pattern {0}'.format(pattern+1))
plt.title('Transition of oil price', fontsize = 20)
plt.xlabel('month', fontsize = 16)
plt.ylabel('oil price', fontsize = 16)
plt.grid(True)
plt.xlim(0,600)
plt.ylim(0, 160)
save_dir = '../output'
plt.savefig(os.path.join(save_dir, 'oil_scenario_whole_time.png'))
plt.close()

exchange = ExchangeRate()
exchange.generate_sinario()
exchange.depict()
num = len(exchange.history_data)
x = range(15*12+num)
for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
    y = []
    for i in range(180+num):
        if i < num:
            y.append(exchange.history_data[i][1])
        else:
            y.append(exchange.predicted_data[pattern][i-num]['price'])
    plt.plot(x, y)
plt.title('Transition of exchange rate', fontsize = 20)
plt.xlabel('month', fontsize = 16)
plt.ylabel('exchange rate', fontsize = 16)
plt.grid(True)
save_dir = '../output'
plt.savefig(os.path.join(save_dir, 'exchange_rate_scenario_whole_time.png'))
plt.close()

distribution = [0,0,0,0,0,0,0,0,0,0]
range_0 = [0,20,30,40,50,60,70,80,90,100,120]
for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
    for a in range(VESSEL_LIFE_TIME * 12):
        f = oil.predicted_data[pattern][a]['price']
        for i in range(10):
            if range_0[i] < f and f < range_0[i+1]:
                distribution[i] += 1
for index in range(len(distribution)):
    distribution[index] = distribution[index]/(pattern*180.0)
    print(distribution[index])
left = [0,1,2,3,4,5,6,7,8,9]
label = ['0','20','30','40','50','60','70','80','90','100']
plt.title('Oil price distribution')
plt.xlabel('oil price')
plt.ylabel('Propability')
plt.bar(left,distribution,tick_label=label,align='center')
save_dir = '../output'
plt.savefig(os.path.join(save_dir, 'oil_price_distribution.png'))
plt.close()

freight_outward = FreightOutward()
freight_outward.generate_sinario()
freight_return = FreightReturn()
freight_return.generate_sinario()

distribution = [0,0,0,0,0,0,0,0]
range_0 = [200,300,400,500,600,700,800,900,1000]
total_freight = []
for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
    total_freight.append([])
    for x in range(VESSEL_LIFE_TIME * 12):
        f = 0.5*(freight_outward.predicted_data[pattern][x]['price'] * LOAD_FACTOR_ASIA_TO_EUROPE + freight_return.predicted_data[pattern][x]['price'] * LOAD_FACTOR_EUROPE_TO_ASIA)
        total_freight[pattern].append(f)
        for i in range(8):
            if range_0[i] < f and f < range_0[i+1]:
                distribution[i] += 1
    _x = range(0,VESSEL_LIFE_TIME*12)
    plt.plot(_x, total_freight[pattern])
    plt.title('Transition of total freight', fontsize = 20)
    plt.xlabel('month', fontsize = 16)
    plt.ylabel('total freight rate value', fontsize = 16)
    plt.grid(True)
save_dir = '../output'
plt.savefig(os.path.join(save_dir, 'real_freight.png'))
plt.close()
#s'''

for index in range(len(distribution)):
    distribution[index] = distribution[index]/(pattern*180.0)
    print(distribution[index])
#left = [200,300,400,500,600,700,800,900]
left = [0,1,2,3,4,5,6,7]
label = ['200','300','400','500','600','700','800','900']
plt.title('Freight distribution')
plt.xlabel('real freight')
plt.ylabel('Propability')
plt.bar(left,distribution,tick_label=label,align='center')
save_dir = '../output'
plt.savefig(os.path.join(save_dir, 'freight_distribution.png'))
plt.close()
