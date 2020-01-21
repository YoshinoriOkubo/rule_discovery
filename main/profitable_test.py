import sys
sys.path.append('../models')
from ship import Ship
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *
import matplotlib.pyplot as plt

ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,1)
price = 57000000
oil = 100#47.22
X = []
y = []
for freight in range(0,2000,100):
    current_freight_rate_outward = freight
    x = (current_freight_rate_outward - oil * 5.744615088 - F_OUTWARD_INTERCEPT) / F_OUTWARD_INCLINATION_DEMAND
    current_freight_rate_homeward = F_HOMEWARD_INCLINATION_DEMAND * x + oil * F_HOMEWARD_INCLINATION_OIL  + F_HOMEWARD_INTERCEPT
    total_freight = ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_homeward * LOAD_FACTOR_EUROPE_TO_ASIA)
    cash_flow = ship.calculate_income_per_time_step_month(47.22,total_freight,1,1)
    cash = -price
    for year in range(15):
        DISCOUNT = (1 + DISCOUNT_RATE) ** (1 + year)
        cash += cash_flow * 4 / DISCOUNT
    print('freight outward = {0}, profit = {1}'.format(freight,cash))
    X.append(freight)
    y.append(cash/1000000)
print(X)
print(y)
'''
plt.bar(X,y)
plt.xlabel('freight outward', fontsize = 16)
plt.ylabel('profit', fontsize = 16)
#plt.tick_params(labelsize=14)
#plt.grid(True)
#plt.legend(loc = 'lower right')
save_dir = '..'
plt.savefig(os.path.join(save_dir, 'profit.png'))
plt.close()
'''
path = '../main/profit.csv'
with open(path, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['freight','profit'])
with open(path, 'a') as f:
    writer = csv.writer(f)
    for x1,y1 in zip(X,y):
        row = []
        row.append(x1)
        row.append(y1)
        writer.writerow(row)