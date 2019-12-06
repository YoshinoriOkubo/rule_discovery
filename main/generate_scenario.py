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
    for sign in [TRAIN_DATA_SET,TEST_DATA_SET]:
        oil = Oil()
        oil.generate_scenario()
        demand = ShipDemand()
        demand.generate_scenario()
        supply = ShipSupply(demand)
        supply.generate_scenario(sign)
        freight_outward = Freight(demand,supply,oil,OUTWARD)
        freight_outward.generate_scenario()
        freight_homeward = Freight(demand,supply,oil,HOMEWARD)
        freight_homeward.generate_scenario()
        exchange = ExchangeRate()
        exchange.generate_scenario()
        new_ship = NewShipMarket(demand,supply)
        new_ship.generate_scenario()
        secondhand_ship = SecondhandShipMarket(demand,supply)
        secondhand_ship.generate_scenario()
        export_binomial_parameter(sign,oil,exchange,demand)
        export_statistical_feature(sign,oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship)
        export_scenario_csv(sign,oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship)
        depict_scenario(sign,oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship)
        depict_whole_scenario(sign,oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship)
        depict_distribution(sign,oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship)

    print(time.time()-start)

if __name__ == "__main__":
    main()
