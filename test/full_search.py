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
from ship import Ship

maxlist = []
for oil_price in OIL_PRICE_LIST:
    for freight in FREIGHT_RATE_LIST:
        list = []
        for speed in VESSEL_SPEED_LIST:
            ship = Ship(TEU_SIZE,speed,ROUTE_DISTANCE)
            cash_flow = ship.calculate_income_per_month(oil_price,freight)
            list.append([cash_flow,oil_price,freight,speed])
        list.sort(key=lambda x:x[0],reverse = True)
        maxlist.append([list[0][1],list[0][2],list[0][3]])

for i in range(len(maxlist)):
    print(maxlist[i])
