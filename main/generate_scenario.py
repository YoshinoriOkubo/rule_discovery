import time
import sys
sys.path.append('../models')
from oil_price import Oil
from exchange_rate import ExchangeRate
from ship_demand import ShipDemand
from ship_supply import ShipSupply
from freight import Freight
from new_ship_market import NewShipMarket
from secondhand_ship_market import SecondhandShipMarket
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

def main():
    start = time.time()

    oil = Oil()
    oil.generate_sinario()
    demand = ShipDemand()
    demand.generate_sinario()
    supply = ShipSupply(demand)
    supply.generate_sinario()
    freight_outward = Freight(demand,supply,oil,OUTWARD)
    freight_outward.generate_sinario()
    freight_homeward = Freight(demand,supply,oil,HOMEWARD)
    freight_homeward.generate_sinario()
    exchange = ExchangeRate()
    exchange.generate_sinario()
    new_ship = NewShipMarket(demand,supply)
    new_ship.generate_sinario()
    secondhand_ship = SecondhandShipMarket(demand,supply)
    secondhand_ship.generate_sinario()
    #export_binomial_parameter(oil,exchange,demand)
    #export_statistical_feature(oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship)
    #export_scenario_csv(oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship)
    #depict_scenario(oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship)
    #depict_whole_scenario(oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship)
    #depict_distribution(oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship)

    print(time.time()-start)

if __name__ == "__main__":
    main()
