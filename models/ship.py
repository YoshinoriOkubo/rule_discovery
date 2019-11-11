import sys
# import own modules #
sys.path.append('../public')
from constants  import *

class Ship:
    def __init__(self, size, speed, route):
        self.size = size
        self.speed = speed# km/h
        self.route = route
        self.exist_number = INITIAL_NUMBER_OF_SHIPS # ships own
        self.total_number = self.exist_number # ships own and ships charter in
        self.charter_flag = False
        self.charter_list = []
        self.idle_rate = 0
        self.agelist = [0]*self.exist_number
        self.charter_out_agelist = []
        self.max_ship_number = int(INITIAL_NUMBER_OF_SHIPS * 1.5)
        self.min_ship_number = 0 #int(INITIAL_NUMBER_OF_SHIPS * 0.5)
        self.ship_order_list = []
        self.order_number = 0

    def check(self):
        flag = len(self.agelist) == self.exist_number
        if flag:
            pass
        else:
            sys.exit()

    def add_age(self):
        self.agelist = [n+1 for n in self.agelist]
        self.charter_out_agelist = [n+1 for n in self.charter_out_agelist]
        old_flag = False
        old_number = 0
        for e in self.agelist:
            if e >= 180:
                old_flag = True
                old_number += 1
        self.agelist.sort(reverse = True)
        cash = 0
        if old_flag:
            cash = FINAL_VALUE * old_number
            for i in range(old_number):
                self.agelist.pop(0)
        self.agelist.sort()
        self.exist_number -= old_number
        self.total_number -= old_number
        self.ship_under_construct()
        return cash

    def calculate_idle_rate(self,freight):
        freight_outward = (2*freight - LOAD_FACTOR_EUROPE_TO_ASIA*625.7839568)/(LOAD_FACTOR_ASIA_TO_EUROPE + LOAD_FACTOR_EUROPE_TO_ASIA*0.128162493)
        gap = 0.485597471 + freight_outward * -0.000325635# mean (supply - demand)/demand
        self.idle_rate = 1 - 1 /(1 + gap)
        number_of_operating = INITIAL_NUMBER_OF_SHIPS - self.idle_rate * INITIAL_NUMBER_OF_SHIPS
        if self.total_number > 0:
            self.idle_rate = (self.total_number - number_of_operating)/self.total_number
            if self.idle_rate < 0:
                self.idle_rate = 0
        else:
            self.idle_rate = 0

    def calculate_income_per_month(self,oil_price,freight):
        speed_km_h = self.change_knot_to_km_h(self.speed)
        time_spent_to_one_trip = self.route/(speed_km_h * 24) + 1
        number_of_trips = 30 / time_spent_to_one_trip
        income_in_one_trip = self.size * freight
        cost_unfixed_in_one_trip = (self.route * self.change_dollers_per_Barrels_to_dollers_per_kg(oil_price) * self.calculate_fuel_consumption_from_speed())
        cost_fixed_in_one_trip = NON_FUELED_COST * time_spent_to_one_trip / 365
        profit_in_one_trip = income_in_one_trip - cost_unfixed_in_one_trip - cost_fixed_in_one_trip
        if profit_in_one_trip > 0:
            self.calculate_idle_rate(freight)
            return (self.idle_rate*(-cost_fixed_in_one_trip)+(1-self.idle_rate)*profit_in_one_trip)*number_of_trips * self.total_number
        else:
            return -cost_fixed_in_one_trip * number_of_trips * self.total_number

    def sell_ship(self,freight_data,time,number):
        freight_criteria = freight_data[0]['price']
        freight_now = freight_data[time]['price']
        if self.exist_number - number < self.min_ship_number:
            number = self.exist_number - self.min_ship_number
        self.exist_number -= number
        self.total_number -= number
        cash = 0
        for i in range(number):
            if self.agelist[i] < 180:
                cash += INITIAL_COST_OF_SHIPBUIDING*(1 - self.agelist[i]/180)*(freight_now/freight_criteria)
            else:
                cash += FINAL_VALUE
        for i in range(number):
            self.agelist.pop(0)
        return cash

    def buy_new_ship(self,freight_data,time,number):
        if number > 0:
            freight_criteria = freight_data[0]['price']
            freight_now = freight_data[time]['price']
            if self.exist_number + number > self.max_ship_number:
                number = self.max_ship_number - self.exist_number
            if time < VESSEL_LIFE_TIME*12 - ORDER_TIME:
                self.ship_order_list.append([number,ORDER_TIME])
                self.order_number += number
                return - INITIAL_COST_OF_SHIPBUIDING*0.5*(1+(freight_now/freight_criteria))*number
            else:
                return 0
        else:
            return 0

    def ship_under_construct(self):
        if len(self.ship_order_list) > 0:
            for i in range(len(self.ship_order_list)):
                self.ship_order_list[i][1] -= 1
            if self.ship_order_list[0][1] == 0:
                self.exist_number += self.ship_order_list[0][0]
                self.total_number += self.ship_order_list[0][0]
                self.order_number -= self.ship_order_list[0][0]
                for number in range(self.ship_order_list[0][0]):
                    self.agelist.append(0)
                self.ship_order_list.pop(0)

    def buy_secondhand_ship(self,freight_data,time,number):
        if number > 0:
            freight_criteria = freight_data[0]['price']
            freight_now = freight_data[time]['price']
            if self.exist_number + number > self.max_ship_number:
                number = self.max_ship_number - self.exist_number
            self.exist_number += number
            self.total_number += number
            for i in range(number):
                self.agelist.append(60)
            return -INITIAL_COST_OF_SHIPBUIDING*(1 - 60/180)*(freight_now/freight_criteria) * (1 + INDIRECT_COST) * number
        else:
            return 0


    def charter_ship(self,oil_price,freight,number,direction):
        if number > 0:
            p = CHARTER_PERIOD.index(12)
            if direction == DECISION_CHARTER_OUT:
                if self.exist_number > 0:
                    cash = self.calculate_income_per_month(oil_price,freight) * RISK_PREMIUM[p] / self.total_number
                    self.charter_flag = True
                    if self.exist_number < number:
                        number = self.exist_number
                    self.exist_number -= number
                    self.total_number -= number
                    cash *= number
                    self.charter_list.append([cash,number,p,direction])
                    for i in range(number):
                        self.charter_out_agelist.append(self.agelist.pop(0))
            elif direction == DECISION_CHARTER_IN:
                self.total_number += number
                if self.total_number > 0:
                    self.charter_flag = True
                    if number + self.total_number > self.max_ship_number:
                        number = self.max_ship_number - self.total_number
                    self.total_number -= number
                    cash = -self.calculate_income_per_month(oil_price,freight) * RISK_PREMIUM[p] * (1 + INDIRECT_COST) / self.total_number
                    self.total_number += number
                    cash *= number
                    self.charter_list.append([cash,number,p,direction])


    def charter(self):
        cash = 0
        for i in range(len(self.charter_list)):
            cash += self.charter_list[i][0]
            self.charter_list[i][2] -= 1
        return cash

    def end_charter(self):
        end_index = []
        for i in range(len(self.charter_list)):
            if self.charter_list[i][2] == 0:
                if self.charter_list[i][3] == DECISION_CHARTER_OUT:
                    self.exist_number += self.charter_list[i][1]
                    self.total_number += self.charter_list[i][1]
                    for j in range(self.charter_list[i][1]):
                        self.agelist.append(self.charter_out_agelist.pop(0))
                elif self.charter_list[i][3] == DECISION_CHARTER_IN:
                    self.total_number -= self.charter_list[i][1]
                end_index.append(i)
        if len(end_index) == 0:
            pass
        elif len(end_index) == 1:
            self.charter_list.pop(end_index[0])
        elif len(end_index) == 2:
            self.charter_list.pop(end_index[1])
            self.charter_list.pop(end_index[0])
        else:
            print('error')
            sys.exit()
        if self.charter_list == []:
            self.charter_flag = False

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
