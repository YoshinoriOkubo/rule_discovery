import sys
sys.path.append('../models')
from oil_price import Oil
from freight_rate_outward import FreightOutward
from freight_rate_return import FreightReturn
from exchange_rate import ExchangeRate
from ship_demand import ShipDemand
from ship_supply import ShipSupply
from freight import Freight
import matplotlib.pyplot as plt
from ga import GA
import time
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

start = time.time()

sinario = Oil()
sinario.generate_sinario()
demand = ShipDemand()
demand.generate_sinario()
supply = ShipSupply(demand)
supply.generate_sinario()
freight_outward = Freight(demand,supply,sinario,OUTWARD)
freight_outward.generate_sinario()
freight_return = Freight(demand,supply,sinario,RETURN)
freight_return.generate_sinario()
exchange = ExchangeRate()
exchange.generate_sinario()
export_scenario_csv(sinario,freight_outward,freight_return,exchange,demand,supply)
depict_scenario(sinario,freight_outward,freight_return,exchange,demand,supply)
depict_whole_scenario(sinario,freight_outward,freight_return,exchange,demand,supply)
depict_distribution(sinario,freight_outward,freight_return,exchange,demand,supply)
print(time.time()-start)
