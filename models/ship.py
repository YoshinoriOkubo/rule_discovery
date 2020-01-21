import sys
# import own modules #
sys.path.append('../public')
from constants  import *

class Ship:
    def __init__(self, size, speed, route,number=None):
        self.size = size
        self.speed = speed# km/h
        self.route = route
        self.exist_number = number if number is not None else INITIAL_NUMBER_OF_SHIPS # ships own
        self.total_number = self.exist_number # ships own and ships charter in
        self.charter_flag = False
        self.charter_list = []
        self.idle_rate = 0
        self.agelist = []
        self.generate_agelist(self.exist_number)
        self.charter_out_agelist = []
        self.max_ship_number = 10000#int(INITIAL_NUMBER_OF_SHIPS * 1.5)
        self.min_ship_number = 0 #int(INITIAL_NUMBER_OF_SHIPS * 0.5)
        self.ship_order_list = []
        self.order_number = 0
        self.init_share = INITIAL_NUMBER_OF_SHIPS/5103.0

    def generate_agelist(self,number):
        sum = WITHIN_FIVE + WITHIN_TEN + WITHIN_FIF
        number_under_five = int(number * WITHIN_FIVE/sum)
        number_under_ten = int(number * WITHIN_TEN/sum)
        number_under_fif = number - number_under_five - number_under_ten
        for index in range(0,number_under_five):
            self.agelist.append(int(index*60/number_under_five))
        for index in range(0,number_under_ten):
            self.agelist.append(int(index*60/number_under_ten)+60)
        for index in range(0,number_under_fif):
            self.agelist.append(int(index*60/number_under_fif)+120)
        self.agelist.sort(reverse = True)
        
    def check(self):
        flag = len(self.agelist) == self.exist_number
        if flag:
            pass
        else:
            sys.exit()

    def add_age(self,time_step=TIME_STEP):
        self.agelist = [n+time_step for n in self.agelist]
        self.charter_out_agelist = [n+time_step for n in self.charter_out_agelist]
        old_flag = False
        old_number = 0
        for e in self.agelist:
            if e >= VESSEL_LIFE_TIME*12:
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
        self.ship_under_construct(time_step)
        return cash

    def ship_under_construct(self,time_step):
        if len(self.ship_order_list) > 0:
            for i in range(len(self.ship_order_list)):
                self.ship_order_list[i][1] -= time_step
            if self.ship_order_list[0][1] <= 0:
                self.exist_number += self.ship_order_list[0][0]
                self.total_number += self.ship_order_list[0][0]
                self.order_number -= self.ship_order_list[0][0]
                for number in range(self.ship_order_list[0][0]):
                    self.agelist.append(0)
                self.ship_order_list.pop(0)

    def calculate_idle_rate(self,demand,supply):
        if self.total_number > 0:
            demand_own = demand*(self.total_number/supply)
            ship_needed = demand_own*SHIP_NUMBER_PER_DEMAND
            if ship_needed > self.total_number:
                self.idle_rate = 0
            else:
                self.idle_rate = (self.total_number - ship_needed)/self.total_number
        else:
            self.idle_rate = 0

    def buy_new_ship(self,price,number):
        if self.exist_number + number > self.max_ship_number:
            number = self.max_ship_number - self.exist_number
        if number > 0:
            self.ship_order_list.append([number,ORDER_TIME])
            self.order_number += number
            return - price *(1 + INDIRECT_COST)*number
        else:
            return 0

    def buy_secondhand_ship(self,price,number):
        if self.exist_number + number > self.max_ship_number:
            number = self.max_ship_number - self.exist_number
        if number > 0:
            self.exist_number += number
            self.total_number += number
            for i in range(number):
                self.agelist.append(FIVE_YEARS_OLD)
            return - price *(1 + INDIRECT_COST)*number
        else:
            return 0

    def sell_ship(self,price,number):
        if self.exist_number - number < self.min_ship_number:
            number = self.exist_number - self.min_ship_number
        if number > 0:
            self.exist_number -= number
            self.total_number -= number
            cash = 0
            for i in range(number):
                if self.agelist[i] < VESSEL_LIFE_TIME*12:
                    price /= 10
                    price *= (180 - self.agelist[i])/12
                    cash += max(FINAL_VALUE,price)
                else:
                    cash += FINAL_VALUE
            for sold_ship in range(number):
                self.agelist.pop(0)
            return cash
        else:
            return 0

    def charter_ship(self,oil_price,freight,demand,supply,number,direction):
        p = CHARTER_TIME
        if direction == DECISION_CHARTER_OUT:
            if self.exist_number > 0:
                cash = self.calculate_income_per_time_step_month(oil_price,freight,demand,supply) * RISK_PREMIUM / self.total_number
                if self.exist_number < number:
                    number = self.exist_number
                if number > 0:
                    self.exist_number -= number
                    self.total_number -= number
                    cash *= number
                    self.charter_list.append([cash,number,p,direction])
                    for i in range(number):
                        self.charter_out_agelist.append(self.agelist.pop(0))
                    self.charter_flag = True
        elif direction == DECISION_CHARTER_IN:
            if number + self.total_number > self.max_ship_number:
                number = self.max_ship_number - self.total_number
            if number > 0:
                if self.total_number == 0:
                    self.total_number = 1
                    cash = -self.calculate_income_per_time_step_month(oil_price,freight,demand,supply) * RISK_PREMIUM * (1 + INDIRECT_COST)
                    self.total_number = 0
                else:
                    cash = -self.calculate_income_per_time_step_month(oil_price,freight,demand,supply) * RISK_PREMIUM * (1 + INDIRECT_COST) / self.total_number
                self.total_number += number
                cash *= number
                self.charter_list.append([cash,number,p,direction])
                self.charter_flag = True


    def charter(self,time_step=TIME_STEP):
        cash = 0
        for i in range(len(self.charter_list)):
            cash += self.charter_list[i][0]*time_step
            self.charter_list[i][2] -= time_step
        return cash

    def end_charter(self,time_step=TIME_STEP):
        end_index = []
        for i in range(len(self.charter_list)):
            if self.charter_list[i][2] <= 0:
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
        elif len(end_index) > 0:
            for reversed_index in reversed(range(0,len(end_index))):
                pop_index = end_index[reversed_index]
                self.charter_list.pop(pop_index)
        else:
            print('error')
            sys.exit()
        if self.charter_list == []:
            self.charter_flag = False

    def change_speed(self,speed):
        self.speed = speed

    def decide_best_speed(self,oil_price,freight,demand,supply,time_step):
        best_speed = VESSEL_SPEED_LIST[0]
        max = 0
        for speed in VESSEL_SPEED_LIST:
            speed_km_h = self.change_knot_to_km_h(speed)
            time_spent_to_one_trip = self.route/(speed_km_h * 24) + LOADING_DAYS
            number_of_trips = 30 * time_step/ time_spent_to_one_trip
            income_in_one_trip = self.size * freight
            cost_unfixed_in_one_trip = self.calc_fuel_cost(oil_price,speed)
            cost_fixed_in_one_trip = NON_FUELED_COST * time_spent_to_one_trip / 365
            profit_in_one_trip = income_in_one_trip - cost_unfixed_in_one_trip - cost_fixed_in_one_trip
            profit = profit_in_one_trip * number_of_trips
            if max < profit:
                max = profit
                best_speed = speed
        return 19#best_speed

    def calculate_income_per_time_step_month(self,oil_price,freight,demand,supply,time_step=TIME_STEP):
        self.change_speed(self.decide_best_speed(oil_price,freight,demand,supply,time_step))
        speed_km_h = self.change_knot_to_km_h(self.speed)
        time_spent_to_one_trip = 75#self.route/(speed_km_h * 24) + LOADING_DAYS
        number_of_trips = 30 * time_step / time_spent_to_one_trip
        income_in_one_trip = self.size * freight
        cost_unfixed_in_one_trip = self.calc_fuel_cost(oil_price,self.speed)
        cost_fixed_in_one_trip = NON_FUELED_COST * time_spent_to_one_trip / 365
        profit_in_one_trip = income_in_one_trip - cost_unfixed_in_one_trip - cost_fixed_in_one_trip
        if profit_in_one_trip > 0:
            self.calculate_idle_rate(demand,supply)
            return (self.idle_rate*(-cost_fixed_in_one_trip)+(1-self.idle_rate)*profit_in_one_trip)*number_of_trips * self.total_number
        else:
            return -cost_fixed_in_one_trip * number_of_trips * self.total_number

    def calc_fuel_cost(self,oil_price,speed):#in one trip
        return self.route * self.change_dollers_per_Barrels_to_dollers_per_kg(oil_price) * self.calculate_fuel_consumption_from_speed(speed)

    def calculate_fuel_consumption_from_speed(self,speed):
        speed_km_h = self.change_knot_to_km_h(speed)
        DWT = 10.8 * self.size + 12400
        DSP = 1.37 * DWT + 1660
        k_c0 = 6.87 * 10**(-5)
        k_c1 = 0.65
        FO = speed_km_h*speed_km_h*k_c0*(DSP-DWT+k_c1*LOAD_FACTOR_ASIA_TO_EUROPE*DWT)*DSP**(-1/3)
        FO += speed_km_h*speed_km_h*k_c0*(DSP-DWT+k_c1*LOAD_FACTOR_EUROPE_TO_ASIA*DWT)*DSP**(-1/3)
        FO /= 2.0
        return FO #kg/km
        #http://www.nilim.go.jp/lab/bcg/siryou/tnn/tnn0494pdf/ks049404.pdf

    def change_knot_to_km_h(self,speed):
        return speed * 1.852

    def change_dollers_per_Barrels_to_dollers_per_kg(self,oil_price):
        return oil_price / 135
        #1barrels = 135kg

    def calc_future_ship(self):
        number = self.order_number
        for e in self.agelist:
            if e  + ORDER_TIME < VESSEL_LIFE_TIME*12:
                number += 1
        return number
