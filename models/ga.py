import random
import copy
import time
import sys
import matplotlib.pyplot as plt
import numpy
import os
import openpyxl
from multiprocessing import Pool
import multiprocessing as multi
from oil_price import Sinario
from ship import Ship
# import own modules #
sys.path.append('../public')
sys.path.append('../output')
from constants  import *

class GA:

    def __init__(self,oil_price_data,freight_rate_outward,freight_rate_return,TEU_size,init_speed,route_distance,decision,generation=None,num=None,alpha=None,crossing_rate=None):
        self.oil_price_data = oil_price_data #oil_price_history_data
        self.freight_rate_outward_data = freight_rate_outward #feright rate outward history data
        self.freight_rate_return_data = freight_rate_return # freight rate return history data
        self.TEU_size = TEU_size #size of ship(TEU)
        self.init_speed = init_speed # initial speed of ship (km/h)
        self.route_distance = route_distance # distance of fixed route (km)
        self.decision = decision # decision of action parts. decision is speed change or sell ship
        self.generation = generation if generation else DEFAULT_GENERATION # the number of generation
        self.num = num if num else DEFAULT_NUM_OF_INDIVIDUAL  # the number of individual
        self.alpha = alpha if alpha else DEFAULT_ALPHA # the rate of mutation
        self.crossing_rate = crossing_rate if crossing_rate else DEFAULT_CROSSING_RATE
        self.group = [] # group that has individual
        self.bestgroup = [] # group that has the best individuals in each generation
        self.averagegroup = [] # the average value of fitness in each generation
        self.num_condition_part = DEFAULT_NUM_OF_CONDITION
        self.compare_rule = []
        for i in range(self.num_condition_part*2):
            self.compare_rule.append([0,0,0,0])
        if self.decision == DECISION_SPEED:
            self.compare_rule.append([1,1,0,1]) #19knot
        elif self.decision == DECISION_SELL:
            self.compare_rule.append([1])
        elif self.decision == DECISION_CHARTER:
            self.compare_rule.append([0])
            self.compare_rule.append([ACTION_STAY])
        self.compare_rule.append(0)
        #self.speed_history = []
        #for i in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        #    self.speed_history.append([])

    def convert2to10_in_list(self,list):
        result = 0
        length = len(list)
        for i in range(len(list)):
            x = length - 1 - i
            result += list[i] * 2 ** (x)
        if len(list) == 4:
            return GRAY_CODE_4[result]
        elif len(list) == 2:
            return GRAY_CODE_2[result]
        elif len(list) == 1:
            return result
        else:
            return None

    def adapt_rule(self,oil_price,freight,rule):
        a = OIL_PRICE_LIST[self.convert2to10_in_list(rule[0])]
        b = OIL_PRICE_LIST[self.convert2to10_in_list(rule[1])]
        if a == b or ( a <= oil_price and oil_price <= b):
            c = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule[2])]
            d = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule[3])]
            if c == d or ( c <= freight and freight <= d):
                if self.decision == DECISION_SPEED:
                    return [True,VESSEL_SPEED_LIST[self.convert2to10_in_list(rule[-2])]]
                elif self.decision == DECISION_SELL:
                    return [True,rule[-2][0]]
                elif self.decision == DECISION_CHARTER:
                    return [True,rule[-2][0],CHARTER_PERIOD[self.convert2to10_in_list(rule[-3])]]
                else:
                    print('selected decision item does not exist')
                    sys.exit()
        return [False]

    def crossing(self,a,b,num_block):
        #for exapmle,
        #speed = [ [1,0,0,0], [0,1,0,1],[1,1,0,0],[1,0,0,1],[1,0,0,1]]
        #sell =  [ [1,0,0,0], [0,1,0,1],[1,1,0,0],[1,0,0,1],[0]]
        #charter = [ [1,0,0,0], [0,1,0,1],[1,1,0,0],[1,0,0,1],[1,0],[0]]
        temp1 = []
        temp2 = []
        for x in range(num_block):
            temp1.append([])
            temp2.append([])
            point = random.randint(0,len(a[x]))
            for i in range(0,point):
                temp1[x].append(a[x][i])
                temp2[x].append(b[x][i])
            for i in range(point,len(a[x])):
                temp1[x].append(b[x][i])
                temp2[x].append(a[x][i])
        for x in range(num_block,len(a)):
            temp1.append(a[x])
            temp2.append(b[x])
        return [temp1,temp2]

    def mutation(self,individual):
        #for x in range(len(individual)-1):
        #    length = len(individual[x]) - 1
        #    point = random.randint(0,length)
        #    individual[x][point] = (individual[x][point] + 1) % 2
        if self.decision == DECISION_SPEED:
            mutation_block = random.randint(0,len(individual)-2)
        elif self.decision == DECISION_SELL:
            mutation_block = random.randint(0,len(individual)-3)
        elif self.decision == DECISION_CHARTER:
            mutation_block = random.randint(0,len(individual)-3)
        length = len(individual[mutation_block]) - 1
        point = random.randint(0,length)
        individual[mutation_block][point] = (individual[mutation_block][point] + 1) % 2
        return individual

    '''

    def process(self,pattern,rule):
        ship = Ship(self.TEU_size,self.init_speed,self.route_distance)
        fitness = -1 * INITIAL_COST_OF_SHIPBUIDING
        for year in range(VESSEL_LIFE_TIME):
            cash_flow = 0
            for month in range(12):
                current_oil_price = self.oil_price_data[pattern][month]['price']
                current_freight_rate_outward = self.freight_rate_outward_data[pattern][month]['price']
                current_freight_rate_return = self.freight_rate_return_data[pattern][month]['price']
                result = self.adapt_rule(current_oil_price,ship.speed,rule)
                if result[0]:
                    ship.change_speed(ship.speed + result[1])
                cash_flow += ship.calculate_income_per_month(current_oil_price,current_freight_rate_outward,current_freight_rate_return)
            DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
            self.average_fitness += cash_flow / DISCOUNT

    def wrap_process(self,num):
        return self.process(*num)

    def fitness_function(self,rule):
        self.average_fitness = 0
        with Pool(processes=multi.cpu_count()) as pool:
            args = [ (i, rule) for i in range(DEFAULT_PREDICT_PATTERN_NUMBER)]
            pool.map(self.wrap_process,args)
        #with Pool(processes=multi.cpu_count()) as pool:
        #    pool.map(self.process, range(DEFAULT_PREDICT_PATTERN_NUMBER))
        self.average_fitness /= DEFAULT_PREDICT_PATTERN_NUMBER
        self.average_fitness /= 1000000
        return max(0,self.average_fitness)
    '''

    def sell_ship(self,pattern,time):
        freight_criteria = self.freight_rate_outward_data[pattern][0]['price']
        freight_now = self.freight_rate_outward_data[pattern][time]['price']
        return INITIAL_COST_OF_SHIPBUIDING*(1 - time/180)*(freight_now/freight_criteria)

    def charter_ship(self,oil_price,freight):
        ship = Ship(self.TEU_size,self.init_speed,self.route_distance)
        cash = ship.calculate_income_per_month(oil_price,freight)
        return cash * RISK_PREMIUM

    def fitness_function(self,rule):
        ship = Ship(self.TEU_size,self.init_speed,self.route_distance)
        fitness = 0
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            ship_exist = True
            charter_ship = False
            charter_fee = 0
            charter_month_remain = 0
            for year in range(VESSEL_LIFE_TIME):
                cash_flow = 0
                if ship_exist:
                    for month in range(12):
                        if ship_exist:
                            current_oil_price = self.oil_price_data[pattern][year*12+month]['price']
                            current_freight_rate_outward = self.freight_rate_outward_data[pattern][year*12+month]['price']
                            current_freight_rate_return = self.freight_rate_return_data[pattern][year*12+month]['price']
                            total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                            #change by argment
                            #full_search
                            if type(rule) is int:
                                ship.change_speed(self.full_search_method_speed(current_oil_price,total_freight))
                                cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                            else:
                                if self.decision == DECISION_SPEED:
                                    #sets_of_group
                                    rule_number, result = 0, [False]
                                    if rule is None:
                                        while rule_number < len(self.group) and result[0] == False:
                                            result = self.adapt_rule(current_oil_price,total_freight,self.group[rule_number])
                                            rule_number += 1
                                    #one rule
                                    else:
                                        result = self.adapt_rule(current_oil_price,total_freight,rule)
                                    if result[0]:
                                        ship.change_speed(result[1])
                                    #if rule is None:
                                    #    self.speed_history[pattern].append(ship.speed)
                                    cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                                elif self.decision == DECISION_SELL:
                                    #sets_of_group
                                    rule_number, result = 0, [False]
                                    if rule is None:
                                        while rule_number < len(self.group) and result[0] == False:
                                            result = self.adapt_rule(current_oil_price,total_freight,self.group[rule_number])
                                            rule_number += 1
                                    #one rule
                                    else:
                                        result = self.adapt_rule(current_oil_price,total_freight,rule)
                                    if result[0] and result[1] == ACTION_SELL:
                                        cash_flow += self.sell_ship(pattern,year*12+month)
                                        ship_exist = False
                                    else:
                                        cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                                elif self.decision == DECISION_CHARTER:
                                    if charter_month_remain == 0:
                                        charter_ship = False
                                    if charter_ship == True:
                                        cash_flow += charter_fee
                                        charter_month_remain -= 1
                                    else:
                                        result = self.adapt_rule(current_oil_price,total_freight,rule)
                                        if result[0] and result[1] == ACTION_CHARTER:
                                            charter_ship = True
                                            charter_fee = self.charter_ship(current_oil_price,total_freight)
                                            charter_month_remain = result[2] - 1
                                            cash_flow += charter_fee
                                        else:
                                            cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                    if year < DEPRECIATION_TIME:
                        cash_flow -= INITIAL_COST_OF_SHIPBUIDING/DEPRECIATION_TIME
                    DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
                    fitness += cash_flow / DISCOUNT
            ship.chagne_speed_to_initial()
        fitness /= DEFAULT_PREDICT_PATTERN_NUMBER
        fitness /= HUNDRED_MILLION
        return max(0,fitness)

    def generateIndividual(self):
        temp = []
        if self.decision == DECISION_SPEED:
            for condition in range(self.num_condition_part*2+1):
                temp.append([])
                for a in range(4):
                    temp[condition].append(random.randint(0,1))
        elif self.decision == DECISION_SELL:
            for condition in range(self.num_condition_part*2):
                temp.append([])
                for a in range(4):
                    temp[condition].append(random.randint(0,1))
            #temp.append([random.randint(0,1)])
            temp.append([ACTION_SELL])
        elif self.decision == DECISION_CHARTER:
            for condition in range(self.num_condition_part*2):
                temp.append([])
                for a in range(4):
                    temp[condition].append(random.randint(0,1))
            temp.append([random.randint(0,1),random.randint(0,1)])
            temp.append([ACTION_CHARTER])
        else:
            print('selected decision item does not exist')
            sys.exit()
        temp.append(0)
        return temp

    def depict(self):
        x = range(0,len(self.bestgroup))
        y = []
        z = []
        for i in range(len(self.bestgroup)):
            y.append(self.bestgroup[i])
            z.append(self.averagegroup[i])
        plt.plot(x, y, marker='o',label='best')
        #if y[3] != z[3]:
        plt.plot(x, z, marker='x',label='average')
        plt.title('Transition of fitness', fontsize = 20)
        plt.xlabel('generation', fontsize = 16)
        plt.ylabel('fitness value', fontsize = 16)
        plt.tick_params(labelsize=14)
        plt.grid(True)
        plt.legend(loc = 'lower right')
        save_dir = '../output'
        if self.decision == DECISION_SPEED:
            name = 'speed'
        elif self.decision == DECISION_SELL:
            name = 'sell'
        elif self.decision == DECISION_CHARTER:
            name = 'charter'
        plt.savefig(os.path.join(save_dir, 'fitness_{}.png'.format(name)))

    def export_excel(self):
        rule_type = ''
        if self.decision == DECISION_SPEED:
            rule_type = 'speed'
        elif self.decision == DECISION_SELL:
            rule_type = 'sell'
        elif self.decision == DECISION_CHARTER:
            rule_type = 'charter'
        path = '../output/ship_rule_{0}.xlsx'.format(rule_type)
        wb = openpyxl.load_workbook(path)
        sheet = wb['Sheet1']
        for i in range(0,self.num):
            individual = self.group[i]
            sheet.cell(row = i + 1, column = 1).value = 'rule{}'.format(i+1)
            for j in range(self.num_condition_part*2):
                if j == 0 or j == 1:
                    sheet.cell(row = i + 1, column = j + 2).value = OIL_PRICE_LIST[self.convert2to10_in_list(individual[j])]
                else:
                    sheet.cell(row = i + 1, column = j + 2).value = FREIGHT_RATE_LIST[self.convert2to10_in_list(individual[j])]
            if self.decision == DECISION_SPEED:
                sheet.cell(row = i + 1, column = self.num_condition_part*2 + 2).value = VESSEL_SPEED_LIST[self.convert2to10_in_list(individual[-2])]
            elif self.decision == DECISION_SELL:
                sheet.cell(row = i + 1, column = self.num_condition_part*2 + 2).value = ('SELL'
                                                                                            if self.convert2to10_in_list(individual[-2]) == ACTION_SELL and self.check_rule_is_adapted(individual)
                                                                                            else 'NOT ADAPTED')
            elif self.decision == DECISION_CHARTER:
                sheet.cell(row = i + 1, column = self.num_condition_part*2 + 2).value = ('{}month charter'.format(CHARTER_PERIOD[self.convert2to10_in_list(individual[-3])])
                                                                                            if self.convert2to10_in_list(individual[-2]) == ACTION_CHARTER and self.check_rule_is_adapted(individual)
                                                                                            else 'NOT ADAPTED')
            sheet.cell(row = i + 1, column = self.num_condition_part*2 + 1 + 2).value = individual[-1]
        wb.save(path)
        wb.close()
        print('saving changes')

    def compare_rules(self):
        fitness_no_rule = self.fitness_function(self.compare_rule)
        if self.decision == DECISION_SPEED:
            name = 'speed'
            fitness_best = self.bestgroup[-1]
            fitness_full_search = self.fitness_function(FULL_SEARCH)
        elif self.decision == DECISION_SELL:
            name = 'sell'
            fitness_best = 0
            for i in range(self.num):
                if self.group[i][-2][0] == ACTION_SELL:
                    if self.check_rule_is_adapted(self.group[i]):
                        fitness_best = self.group[i][-1]
                        break
            fitness_full_search = self.full_search_method_sell()
        elif self.decision == DECISION_CHARTER:
            name = 'charter'
            fitness_best = 0
            for i in range(self.num):
                if self.group[i][-2][0] == ACTION_CHARTER:
                    if self.check_rule_is_adapted(self.group[i]):
                        fitness_best = self.group[i][-1]
                        break
            fitness_full_search = self.full_search_method_charter()
        else:
            print('selected decision item does not exist')
            sys.exit()
        print(fitness_no_rule,fitness_best,fitness_full_search)
        left = [1,2,3]
        height = [fitness_no_rule,fitness_best,fitness_full_search]
        label = ['no rule','best rule','full search']
        #fitness_set_of_rule = self.fitness_function(None)
        #print(fitness_no_rule,fitness_best,fitness_set_of_rule,fitness_full_search)
        #left = [1,2,3,4]
        #height = [fitness_no_rule,fitness_best,fitness_set_of_rule,fitness_full_search]
        #label = ['no rule','best rule','sets of rules','full search']
        plt.bar(left,height,tick_label=label,align='center')
        plt.title('Comparison among three decision rule')
        plt.ylabel('fitness')
        min_fit = min(fitness_no_rule,min(fitness_best,fitness_full_search))
        max_fit = max(fitness_no_rule,max(fitness_best,fitness_full_search))
        plt.ylim(min(0,min_fit-1),max_fit+1)
        save_dir = '../output'
        plt.savefig(os.path.join(save_dir, 'comparison_{}.png'.format(name)))
        plt.close()

    def full_search_method_speed(self,oil_price,freight):
        if self.decision == DECISION_SPEED:
            list = []
            for speed in VESSEL_SPEED_LIST:
                ship = Ship(TEU_SIZE,speed,ROUTE_DISTANCE)
                cash_flow = ship.calculate_income_per_month(oil_price,freight)
                list.append([cash_flow,speed,oil_price,freight])
            list.sort(key=lambda x:x[0],reverse = True)
            return list[0][1]

    def full_search_method_sell(self):
        list = []
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            ship = Ship(self.TEU_size,self.init_speed,self.route_distance)
            fitness_list = []
            for i in range(VESSEL_LIFE_TIME*12):
                fitness_list.append([-INITIAL_COST_OF_SHIPBUIDING,0,i])
            for time in range(VESSEL_LIFE_TIME*12):
                current_oil_price = self.oil_price_data[pattern][time]['price']
                current_freight_rate_outward = self.freight_rate_outward_data[pattern][time]['price']
                current_freight_rate_return = self.freight_rate_return_data[pattern][time]['price']
                total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                for index in range(VESSEL_LIFE_TIME*12):
                    if index < time:
                        pass
                    elif index == time:
                        fitness_list[index][1] += self.sell_ship(pattern,time)
                    else:
                        fitness_list[index][1] += ship.calculate_income_per_month(current_oil_price,total_freight)
                if (time + 1) % 12 == 0:
                    for index in range(VESSEL_LIFE_TIME*12):
                        if fitness_list[index][1] > 0:
                            DISCOUNT = (1 + DISCOUNT_RATE) ** (time/12)
                            fitness_list[index][0] += fitness_list[index][1]/DISCOUNT
                            fitness_list[index][1] = 0
            fitness_list.sort(key=lambda x:x[0],reverse = True)
            #print(fitness_list[0][2])
            list.append(fitness_list[0][0]/HUNDRED_MILLION)
        best = 0
        for e in range(len(list)):
            best += list[e]
        return best/DEFAULT_PREDICT_PATTERN_NUMBER

    def full_search_method_charter(self):
        fitness_list_charter = []
        checklist = []
        for period in [0,1,2,3]:
            fitness_list_charter.append([])
            checklist.append([0,period])
            charter_list = []
            for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
                fitness_list_charter[period].append([])
                ship = Ship(self.TEU_size,self.init_speed,self.route_distance)
                store = []
                store.append([0,[],0])
                for element in range(1,CHARTER_PERIOD[period]):
                    oil_price = self.oil_price_data[pattern][-element]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][-element]['price']
                    current_freight_rate_return = self.freight_rate_return_data[pattern][-element]['price']
                    freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    cash_0 = ship.calculate_income_per_month(oil_price,freight)
                    charter_0 = self.charter_ship(oil_price,freight)
                    if cash_0 + store[element-1][0] > charter_0*element:
                        store.append([cash_0 + store[element-1][0],[1],element])
                        charter_list.append(['STAY',180-element])
                    else:
                        store.append([charter_0*element,[0],element])
                        charter_list.append(['CHARTER',180-element])
                for x in range(CHARTER_PERIOD[period],VESSEL_LIFE_TIME*12+1):
                    oil_price_fx = self.oil_price_data[pattern][-x]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][-x]['price']
                    current_freight_rate_return = self.freight_rate_return_data[pattern][-x]['price']
                    freight_fx = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    cash = ship.calculate_income_per_month(oil_price_fx,freight_fx)
                    charter = self.charter_ship(oil_price_fx,freight_fx)
                    if cash + store[-1][0] > charter*CHARTER_PERIOD[period] + store[-CHARTER_PERIOD[period]][0]:
                        store.append([cash + store[-1][0],[1],x])
                        charter_list.append(['STAY',180-x])
                    else:
                        store.append([charter*CHARTER_PERIOD[period] + store[-CHARTER_PERIOD[period]][0],[0],x])
                        charter_list.append(['CHARTER',180-x])
                charter_list.reverse()

                if period == 3:
                    x = 0
                    for e in charter_list:
                        if x > 0:
                            x -= 1
                        else:
                            if e[0] == 'CHARTER':
                                #print(e)
                                x  = 35
                    path = '../output/full_rule.xlsx'
                    w = openpyxl.load_workbook(path)
                    sheet = w['Sheet1']
                    for i in range(VESSEL_LIFE_TIME*12):
                        sheet.cell(row = i + 1, column = 1).value = charter_list[i][0]
                    w.save(path)
                    w.close()
                    #print('saving changes')

                store.reverse()
                a = 0
                for year in range(0,VESSEL_LIFE_TIME):
                    cash_of_year = store[year*12][0] - store[year*12 + 12][0]
                    DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
                    a += cash_of_year/DISCOUNT
                checklist[period][0] += (a - INITIAL_COST_OF_SHIPBUIDING)/HUNDRED_MILLION
            checklist[period][0] /= DEFAULT_PREDICT_PATTERN_NUMBER
        checklist.sort(key=lambda x:x[0],reverse = True)
        return checklist[0][0]

    def check_rule_is_adapted(self,rule):
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            for year in range(VESSEL_LIFE_TIME):
                for month in range(12):
                    current_oil_price = self.oil_price_data[pattern][year*12+month]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][year*12+month]['price']
                    current_freight_rate_return = self.freight_rate_return_data[pattern][year*12+month]['price']
                    total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    result = self.adapt_rule(current_oil_price,total_freight,rule)
                    if result[0]:
                        return True
        return False

    def execute_GA(self):
        first = time.time()

        #randomly generating individual group
        for i in range(self.num):
            self.group.append(self.generateIndividual())

        #genetic algorithm
        for gene in range(self.generation):
            print('{}%finished'.format(gene*100.0/self.generation),time.time()-first)

            #crossing
            temp = copy.deepcopy(self.group)
            #store best individual unchanged
            temp.append(self.group[0])
            for i in range(0,self.num,2):
                if random.random() < self.crossing_rate:
                    if self.decision == DECISION_SPEED:
                        a,b = self.crossing(temp[i],temp[i+1],self.num_condition_part*2+1)
                    elif self.decision == DECISION_SELL:
                        a,b = self.crossing(temp[i],temp[i+1],self.num_condition_part*2)
                    elif self.decision == DECISION_CHARTER:
                        a,b = self.crossing(temp[i],temp[i+1],self.num_condition_part*2+1)
                    else:
                        print('selected decision item does not exist')
                        sys.exit()
                    temp.append(a)
                    temp.append(b)

            #mutation
            for individual in temp:
                if random.random() < self.alpha:
                    individual = self.mutation(individual)

            #rule check
            for k in range(len(temp)):
                rule = copy.deepcopy(temp[k])
                a = OIL_PRICE_LIST[self.convert2to10_in_list(rule[0])]
                b = OIL_PRICE_LIST[self.convert2to10_in_list(rule[1])]
                c = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule[2])]
                d = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule[3])]
                if a > b:
                    X = copy.deepcopy(temp[k])
                    for element in range(4):
                        temp[k][0][element] = X[1][element]
                        temp[k][1][element] = X[0][element]
                if c > d:
                    Y = copy.deepcopy(temp[k])
                    for element in range(4):
                        temp[k][2][element] = Y[3][element]
                        temp[k][3][element] = Y[2][element]

            #computation of fitness
            for one in range(len(temp)):
                rule = temp[one]
                rule[-1] = self.fitness_function(rule)


            #reduce the number of individual
            #num -= 10

            #selection

            #steady state ga
            '''
            for i in range(0,len(temp),2):
                if i + 1 < self.num:
                    store = []
                    store.append(temp[i])
                    store.append(temp[i+1])
                    if self.num + i < len(temp):
                        store.append(temp[self.num + i])
                    if self.num + i + 1 < len(temp):
                        store.append(temp[self.num + i+1])
                    store.sort(key=lambda x:x[-1],reverse = True)
                    self.group[i] = store[0]
                    self.group[i+1] = store[1]
            self.group.sort(key=lambda x:x[-1],reverse = True)
            self.bestgroup.append(self.group[0][-1])
            total = 0
            for e in range(self.num):
                total += self.group[e][-1]
            self.averagegroup.append(total/self.num)
            '''
            '''
            #tournament selection
            for select in range(self.num):
                tournament = []
                for _ in range(6):
                    tournament.append(temp[random.randint(0,2*self.num-1)])
                tournament.sort(key=lambda x:x[-1],reverse = True)
                self.group[select] = tournament[0]
            self.group.sort(key=lambda x:x[-1],reverse = True)
            self.bestgroup.append(self.group[0][-1])
            total = 0
            for e in range(self.num):
                total += self.group[e][-1]
            self.averagegroup.append(total/self.num)
            '''

            #'''
            #roulette selection and elite storing
            #store the best 5% individual
            temp.sort(key=lambda x:x[-1],reverse = True)
            elite_number = int(self.num * 0.05)
            for i in range(elite_number):
                self.group[i] = temp[i]
            random.shuffle(temp)
            ark = 0 # the number used to roulette in crossing
            probability = 0
            for i in range(len(temp)):
                probability += temp[i][-1]
            roulette = 0
            for i in range(elite_number,self.num):
                roulette = random.randint(0,int(probability))
                while roulette > 0:
                    roulette -= temp[ark][-1]
                    ark = (ark + 1) % self.num
                self.group[i] = temp[ark]
            self.group.sort(key=lambda x:x[-1],reverse = True)
            self.bestgroup.append(self.group[0][-1])
            total = 0
            for e in range(self.num):
                total += self.group[e][-1]
            self.averagegroup.append(total/self.num)
            if gene > 10 and self.bestgroup[-1] == self.bestgroup[-2] == self.bestgroup[-3]:
                break
            #'''

        #print result
        self.group.sort(key=lambda x:x[-1],reverse = True)
        for i in range(0,self.num):
            if i == 0:
                print('best rule', self.group[i])

            thisone = self.group[i]
            #if self.check_rule_is_adapted(thisone):
            a = OIL_PRICE_LIST[self.convert2to10_in_list(thisone[0])]
            b = OIL_PRICE_LIST[self.convert2to10_in_list(thisone[1])]
            c = FREIGHT_RATE_LIST[self.convert2to10_in_list(thisone[2])]
            d = FREIGHT_RATE_LIST[self.convert2to10_in_list(thisone[3])]
            if self.decision == DECISION_SPEED:
                e = VESSEL_SPEED_LIST[self.convert2to10_in_list(thisone[-2])]
            elif self.decision == DECISION_SELL:
                e = ('SELL'
                        if self.convert2to10_in_list(thisone[-2]) == ACTION_SELL and self.check_rule_is_adapted(thisone)
                        else 'NOT ADAPTED')
            elif self.decision == DECISION_CHARTER:
                e = ('{}month charter'.format(CHARTER_PERIOD[self.convert2to10_in_list(thisone[-3])])
                        if self.convert2to10_in_list(thisone[-2]) == ACTION_CHARTER and self.check_rule_is_adapted(thisone)
                        else 'NOT ADAPTED')
            print('{0} <= oil price <= {1} and {2} <= freight <= {3} -> {4}  fitness value = {5}'.format(a,b,c,d,e,thisone[-1]))
            if a > b or c > d:
                print('rule error')
                sys.exit()
        print('finish')
        exe = time.time() - first
        print('Spent time is {0}'.format(exe))
        self.export_excel()
        self.compare_rules()
