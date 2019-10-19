import sys
# import own modules #
sys.path.append('../public')
from constants  import *

class Ship:
    def __init__(self, size, speed, route):
        self.size = size
        self.speed = speed# km/h
        self.route = route
        self.exist = True
        self.charter = False
        self.charter_fee = 0
        self.charter_month_remain = 0
        self.idle_rate = 0

    def calculate_idle_rate(self,freight_outward):
        gap = 0.485597471 + freight_outward * -0.000325635
        if gap < 0:
            self.idle_rate = 0
        else:
            self.idle_rate = 1 - 1 /(1 + gap)

    def calculate_income_per_month(self,oil_price,freight):
        speed_km_h = self.change_knot_to_km_h(self.speed)
        time_spent_to_one_trip = self.route/(speed_km_h * 24) + 1
        number_of_trips = 30 / time_spent_to_one_trip
        income_in_one_trip = self.size * freight #1600doller/TEU http://www.jpmac.or.jp/relation/trend_graph/26_1_1.pdf
        cost_unfixed_in_one_trip = (self.route * self.change_dollers_per_Barrels_to_dollers_per_kg(oil_price) * self.calculate_fuel_consumption_from_speed())
        cost_fixed_in_one_trip = NON_FUELED_COST * time_spent_to_one_trip / 365
        profit_in_one_trip = income_in_one_trip - cost_unfixed_in_one_trip - cost_fixed_in_one_trip
        if profit_in_one_trip > 0:
            return (self.idle_rate*(-cost_fixed_in_one_trip)+(1-self.idle_rate)*profit_in_one_trip)*number_of_trips
        else:
            return -cost_fixed_in_one_trip * number_of_trips

    def sell_ship(self,freight_data,time):
        freight_criteria = freight_data[0]['price']
        freight_now = freight_data[time]['price']
        self.exist = False
        return INITIAL_COST_OF_SHIPBUIDING*(1 - time/180)*(freight_now/freight_criteria)

    def charter_ship(self,oil_price,freight):
        self.charter = True
        cash = self.calculate_income_per_month(oil_price,freight) * RISK_PREMIUM
        self.charter_fee = cash
        return cash

    def in_charter(self):
        cash = self.charter_fee
        self.charter_month_remain -= 1
        if self.charter_month_remain == 0:
            self.charter = False
        return cash


    def change_speed(self,speed):
        self.speed = speed

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
