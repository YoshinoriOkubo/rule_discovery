import sys
# import own modules #
sys.path.append('../public')
from constants  import *

class Ship:
    def __init__(self, size, speed, route):
        self.size = size
        self.speed = speed# km/h
        self.route = route

    def calculate_income_per_month(self,oil_price,freight_outward,freight_return):
        speed_km_h = self.change_knot_to_km_h(self.speed)
        time_spent_to_one_trip = self.route/(speed_km_h * 24) + 1
        number_of_trips = 30 / time_spent_to_one_trip
        #fixed income
        freight = 0.5 * ( freight_outward * LOAD_FACTOR_ASIA_TO_EUROPE + freight_return * LOAD_FACTOR_EUROPE_TO_ASIA)
        income_in_one_trip = self.size * freight #1600doller/TEU http://www.jpmac.or.jp/relation/trend_graph/26_1_1.pdf
        cost_unfixed_in_one_trip = self.route * self.change_dollers_per_Barrels_to_dollers_per_kg(oil_price) * self.calculate_fuel_consumption_from_speed()
        cost_fixed_in_one_trip = NON_FUELED_COST * time_spent_to_one_trip / 365

        #print(income_in_one_trip)
        #print(cost_fixed_in_one_trip)
        #print(cost_unfixed_in_one_trip)
        return (income_in_one_trip - cost_unfixed_in_one_trip - cost_fixed_in_one_trip) * number_of_trips

    def change_speed(self,speed):
        self.speed = speed  if speed > MINIMUM_SHIP_SPEED else MINIMUM_SHIP_SPEED

    def chagne_speed_to_initial(self):
        self.speed = INITIAL_SPEED

    def calculate_fuel_consumption_from_speed(self):
        speed_km_h = self.change_knot_to_km_h(self.speed)
        DWT = 10.8 * self.size + 12400
        DSP = 1.37 * DWT + 1660
        k_c0 = 6.87 * 10**(-5)
        k_c1 = 0.65
        LF = 0.8
        FO = speed_km_h*speed_km_h*k_c0*(DSP-DWT+k_c1*LF*DWT)*DSP**(-1/3)
        return FO #kg/km
        #http://www.nilim.go.jp/lab/bcg/siryou/tnn/tnn0494pdf/ks049404.pdf

    def change_knot_to_km_h(self,speed):
        return speed * 1.852

    def change_dollers_per_Barrels_to_dollers_per_kg(self,oil_price):
        return oil_price / 135
        #1barrels = 135kg
