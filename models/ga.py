import random
import copy
import time
import sys
import matplotlib.pyplot as plt
import numpy as np
import os
import openpyxl
from multiprocessing import Pool
import multiprocessing as multi
from joblib import Parallel, delayed
from oil_price import Sinario
from ship import Ship
from tqdm import tqdm
from oil_price import Sinario
from freight_rate_outward import FreightOutward
from freight_rate_return import FreightReturn
from exchange_rate import ExchangeRate
# import own modules #
sys.path.append('../public')
sys.path.append('../output')
from constants  import *
from my_modules import *

class GA:

    def __init__(self,oil_price_data,freight_rate_outward,freight_rate_return,exchange_rate,TEU_size,init_speed,route_distance,decision,generation=None,num=None,alpha=None,crossing_rate=None):
        self.oil_price_data = oil_price_data #oil_price_history_data
        self.freight_rate_outward_data = freight_rate_outward #feright rate outward history data
        self.freight_rate_return_data = freight_rate_return # freight rate return history data
        self.exchange_rate = exchange_rate # exchange_rate history data
        self.TEU_size = TEU_size #size of ship(TEU)
        self.init_speed = init_speed # initial speed of ship (km/h)
        self.route_distance = route_distance # distance of fixed route (km)
        self.decision = decision # decision of action parts. decision is speed change or sell ship
        self.generation = generation if generation else DEFAULT_GENERATION # the number of generation
        self.num = num if num else DEFAULT_NUM_OF_INDIVIDUAL  # the number of individual
        self.alpha = alpha if alpha else DEFAULT_ALPHA # the rate of mutation
        self.crossing_rate = crossing_rate if crossing_rate else DEFAULT_CROSSING_RATE
        self.priority = []
        self.group = [] # group that has individual
        self.temp = [] #temporary group that has individuals
        self.bestgroup = [] # group that has the best individuals in each generation
        self.averagegroup = [] # the average value of fitness in each generation
        self.num_condition_part = DEFAULT_NUM_OF_CONDITION
        self.compare_rule = []
        if self.decision == DECISION_INTEGRATE:
            for rule_index in range(len(RULE_SET)):
                self.compare_rule.append([])
                for i in range(self.num_condition_part*2):
                    self.compare_rule[rule_index].append([0,0,0,0])
                if RULE_SET[rule_index] == DECISION_SPEED:
                    self.compare_rule[rule_index].append([1,1,0,1]) #19knot
                elif RULE_SET[rule_index] == DECISION_SELL:
                    self.compare_rule[rule_index].append(ACTION_STAY)
                elif RULE_SET[rule_index] == DECISION_CHARTER:
                    self.compare_rule[rule_index].append([0,0])#charter period
                    self.compare_rule[rule_index].append(ACTION_STAY)
        else:
            for i in range(self.num_condition_part*2):
                self.compare_rule.append([0,0,0,0])
            if self.decision == DECISION_SPEED:
                self.compare_rule.append([1,1,0,1]) #19knot
            elif self.decision == DECISION_SELL:
                self.compare_rule.append(ACTION_STAY)
            elif self.decision == DECISION_CHARTER:
                self.compare_rule.append([0,0])#charter period
                self.compare_rule.append(ACTION_STAY)
        #self.compare_rule.append(0) #average alone
        self.compare_rule.append([0,0])# average profit and varianve

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

    def adapt_rule(self,oil_price,freight,exchange,rule):
        if self.decision == DECISION_INTEGRATE:
            result = []
            for rule_index in range(len(rule)-1):
                rule_for_X = rule[rule_index]
                result.append([False])
                a = OIL_PRICE_LIST[self.convert2to10_in_list(rule_for_X[0])]
                b = OIL_PRICE_LIST[self.convert2to10_in_list(rule_for_X[1])]
                if a == b or ( a <= oil_price and oil_price <= b):
                    c = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule_for_X[2])]
                    d = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule_for_X[3])]
                    if c == d or ( c <= freight and freight <= d):
                        e = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule_for_X[4])]
                        f = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule_for_X[5])]
                        if e == f or (e <= exchange and exchange <= f):
                            if RULE_SET[rule_index] == DECISION_SPEED:
                                result[rule_index][0] = True
                                result[rule_index].append(VESSEL_SPEED_LIST[self.convert2to10_in_list(rule_for_X[-1])])
                            elif RULE_SET[rule_index] == DECISION_SELL:
                                result[rule_index][0] = True
                                result[rule_index].append(SELL_NUMBER[self.convert2to10_in_list(rule_for_X[-1])])
                            elif RULE_SET[rule_index] == DECISION_CHARTER and rule_for_X[-1][0] != ACTION_STAY:
                                result[rule_index][0] = True
                                result[rule_index].append(CHARTER_PERIOD[self.convert2to10_in_list(rule_for_X[-2])])
                                result[rule_index].append(CHARTER_NUMBER[self.convert2to10_in_list(rule_for_X[-1])])
            return result
        else:
            a = OIL_PRICE_LIST[self.convert2to10_in_list(rule[0])]
            b = OIL_PRICE_LIST[self.convert2to10_in_list(rule[1])]
            if a == b or ( a <= oil_price and oil_price <= b):
                c = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule[2])]
                d = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule[3])]
                if c == d or ( c <= freight and freight <= d):
                    e = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule[4])]
                    f = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule[5])]
                    if e == f or (e <= exchange and exchange <= f):
                        if self.decision == DECISION_SPEED:
                            return [True,VESSEL_SPEED_LIST[self.convert2to10_in_list(rule[-2])]]
                        elif self.decision == DECISION_SELL:
                            return [True,SELL_NUMBER[self.convert2to10_in_list(rule[-2])]]
                        elif self.decision == DECISION_CHARTER:
                            return [True,CHARTER_PERIOD[self.convert2to10_in_list(rule[-3])],CHARTER_NUMBER[self.convert2to10_in_list(rule[-2])]]
                        else:
                            print('selected decision item does not exist')
                            sys.exit()
            return [False]

    def crossing(self,a,b,num_block=None):
        #for exapmle,
        #speed = [ [1,0,0,0], [0,1,0,1],[1,1,0,0],[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0,0,1],fitness]
        #sell =  [ [1,0,0,0], [0,1,0,1],[1,1,0,0],[1,0,0,1],[0,1,1,1],[1,0,0,1],[1,0,0,1],fitness]
        #charter = [ [1,0,0,0], [0,1,0,1],[1,1,0,0],[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0],[0,1,1,1],fitness]
        #interate = [ [speed rule],[sell rule], [charter rule],fitness]
        temp1 = []
        temp2 = []
        if num_block == None:
            if self.decision == DECISION_INTEGRATE:
                for rule_index in range(len(a)-1):
                    temp1.append([])
                    temp2.append([])
                    if RULE_SET[rule_index] == DECISION_SPEED:
                        num_block = self.num_condition_part*2 + 1
                    elif RULE_SET[rule_index] == DECISION_SELL:
                        num_block = self.num_condition_part*2 + 1
                    elif RULE_SET[rule_index] == DECISION_CHARTER:
                        num_block = self.num_condition_part*2 + 2
                    crossing_block = random.randint(0,num_block-1)
                    for x in range(num_block):
                        if x == crossing_block:
                            temp1[rule_index].append([])
                            temp2[rule_index].append([])
                            length = len(a[rule_index][x]) - 1
                            crossing_point = random.randint(0,length)
                            for i in range(0,crossing_point):
                                temp1[rule_index][x].append(a[rule_index][x][i])
                                temp2[rule_index][x].append(b[rule_index][x][i])
                            for i in range(crossing_point,len(a[rule_index][x])):
                                temp1[rule_index][x].append(b[rule_index][x][i])
                                temp2[rule_index][x].append(a[rule_index][x][i])
                        else:
                            temp1[rule_index].append(a[rule_index][x])
                            temp2[rule_index].append(b[rule_index][x])
                    for x in range(num_block,len(a[rule_index])):
                        temp1[rule_index].append(a[rule_index][x])
                        temp2[rule_index].append(b[rule_index][x])
            else:
                print('function crossing needs one more argment')
                sys.exit()
        else:
            crossing_block = random.randint(0,num_block-1)
            for x in range(num_block):
                if x == crossing_block:
                    temp1.append([])
                    temp2.append([])
                    length = len(a[x]) - 1
                    crossing_point = random.randint(0,length)
                    for i in range(0,crossing_point):
                        temp1[x].append(a[x][i])
                        temp2[x].append(b[x][i])
                    for i in range(crossing_point,len(a[x])):
                        temp1[x].append(b[x][i])
                        temp2[x].append(a[x][i])
                else:
                    temp1.append(a[x])
                    temp2.append(b[x])
            for x in range(num_block,len(a)-1):
                temp1.append(a[x])
                temp2.append(b[x])
        temp1.append([0,0])
        temp2.append([0,0])
        return [temp1,temp2]

    def mutation(self,individual):
        #for x in range(len(individual)-1):
        #    length = len(individual[x]) - 1
        #    point = random.randint(0,length)
        #    individual[x][point] = (individual[x][point] + 1) % 2
        if self.decision == DECISION_INTEGRATE:
            for rule_index in range(len(individual)-1):
                if random.random() < 1/(len(individual)-1):
                    rule_for_X = individual[rule_index]
                    if RULE_SET[rule_index] == DECISION_SPEED:
                        mutation_block = random.randint(0,len(rule_for_X)-1)
                    elif RULE_SET[rule_index] == DECISION_SELL:
                        mutation_block = random.randint(0,len(rule_for_X)-1)
                    elif RULE_SET[rule_index] == DECISION_CHARTER:
                        mutation_block = random.randint(0,len(rule_for_X)-1)
                    length = len(rule_for_X[mutation_block]) - 1
                    point = random.randint(0,length)
                    rule_for_X[mutation_block][point] = (rule_for_X[mutation_block][point] + 1) % 2
        else:
            if self.decision == DECISION_SPEED:
                mutation_block = random.randint(0,len(individual)-2)
            elif self.decision == DECISION_SELL:
                mutation_block = random.randint(0,len(individual)-2)
            elif self.decision == DECISION_CHARTER:
                mutation_block = random.randint(0,len(individual)-2)
            length = len(individual[mutation_block]) - 1
            if length < 1:
                print(mutation_block)
                print(individual)
            point = random.randint(0,length)
            individual[mutation_block][point] = (individual[mutation_block][point] + 1) % 2
        return individual

    def fitness_function(self,rule,priority=None):
        Record = []
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            fitness = 0
            ship = Ship(self.TEU_size,self.init_speed,self.route_distance)
            for year in range(VESSEL_LIFE_TIME):
                cash_flow = 0
                for month in range(12):
                    current_oil_price = self.oil_price_data[pattern][year*12+month]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][year*12+month]['price']
                    current_freight_rate_return = self.freight_rate_return_data[pattern][year*12+month]['price']
                    total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    ship.calculate_idle_rate(current_freight_rate_outward)
                    current_exchange = self.exchange_rate[pattern][year*12+month]['price']
                    #change by argment
                    if self.decision == DECISION_SPEED:
                        #sets_of_group
                        rule_number, result = 0, [False]
                        if rule is None:
                            while rule_number < len(self.group) and result[0] == False:
                                result = self.adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,self.group[rule_number])
                                rule_number += 1
                        #one rule
                        else:
                            result = self.adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,rule)
                        if result[0]:
                            ship.change_speed(result[1])
                        cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                    elif self.decision == DECISION_SELL:
                        #sets_of_group
                        rule_number, result = 0, [False]
                        if rule is None:
                            while rule_number < len(self.group) and result[0] == False:
                                result = self.adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,self.group[rule_number])
                                rule_number += 1
                        #one rule
                        else:
                            result = self.adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,rule)
                        if result[0]:
                            cash_flow += ship.sell_ship(self.freight_rate_outward_data[pattern],year*12+month,result[1])
                        cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                    elif self.decision == DECISION_CHARTER:
                        #sets_of_group
                        rule_number, result = 0, [False]
                        if rule is None:
                            while rule_number < len(self.group) and result[0] == False:
                                result = self.adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,self.group[rule_number])
                                rule_number += 1
                        #one rule
                        else:
                            result = self.adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,rule)
                        if result[0] and result[2] > 0:
                            ship.charter_ship(current_oil_price,total_freight,result[2],result[1])
                        cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                        if ship.charter == True:
                            cash_flow += ship.in_charter()
                            ship.end_charter()
                    elif self.decision == DECISION_INTEGRATE:
                        result = self.adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,rule)
                        if result[0][0] == True:
                            ship.change_speed(result[0][1])
                        if priority == PRIORITY_SELL_CHARTER:
                            if result[1][0] == True:
                                cash_flow += ship.sell_ship(self.freight_rate_outward_data[pattern],year*12+month,result[1][1])
                            if result[2][0] == True:
                                ship.charter_ship(current_oil_price,total_freight,result[2][2],result[2][1])
                        elif priority == PRIORITY_CHARTER_SELL:
                            if result[2][0] == True:
                                ship.charter_ship(current_oil_price,total_freight,result[2][2],result[2][1])
                            if result[1][0] == True:
                                cash_flow += ship.sell_ship(self.freight_rate_outward_data[pattern],year*12+month,result[1][1])
                        cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight)
                        if ship.charter == True:
                            cash_flow += ship.in_charter()
                            ship.end_charter()
                DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
                cash_flow *= self.exchange_rate[pattern][year*12+11]['price']
                fitness += cash_flow / DISCOUNT
            fitness -= INITIAL_COST_OF_SHIPBUIDING*INITIAL_NUMBER_OF_SHIPS*self.exchange_rate[pattern][0]['price']
            fitness /= HUNDRED_MILLION
            fitness /= INITIAL_NUMBER_OF_SHIPS
            Record.append(fitness)
        e, sigma = calc_statistics(Record)
        return [e,sigma]

    def multiproces_fitness(self,i):
        e, sigma = self.fitness_function(self.temp[i],self.priority)
        return [i,[e,sigma]]

    def generateIndividual(self):
        temp = []
        if self.decision == DECISION_SPEED:
            for condition in range(self.num_condition_part*2+1):
                temp.append([])
                for a in range(4):
                    temp[condition].append(random.randint(0,1))
        elif self.decision == DECISION_SELL:
            for condition in range(self.num_condition_part*2+1):
                temp.append([])
                for a in range(4):
                    temp[condition].append(random.randint(0,1))
        elif self.decision == DECISION_CHARTER:
            for condition in range(self.num_condition_part*2):
                temp.append([])
                for a in range(4):
                    temp[condition].append(random.randint(0,1))
            temp.append([random.randint(0,1),random.randint(0,1)])
            temp.append([])
            for i in range(4):
                temp[-1].append(random.randint(0,1))
        elif self.decision == DECISION_INTEGRATE:
            #Individual have three rule
            temp.append([])
            for condition in range(self.num_condition_part*2+1):
                temp[0].append([])
                for a in range(4):
                    temp[0][condition].append(random.randint(0,1))
            temp.append([])
            for condition in range(self.num_condition_part*2+1):
                temp[1].append([])
                for a in range(4):
                    temp[1][condition].append(random.randint(0,1))
            temp.append([])
            for condition in range(self.num_condition_part*2):
                temp[2].append([])
                for a in range(4):
                    temp[2][condition].append(random.randint(0,1))
            temp[2].append([random.randint(0,1),random.randint(0,1)])
            temp[2].append([])
            for i in range(4):
                temp[2][-1].append(random.randint(0,1))
        else:
            print('selected decision item does not exist')
            sys.exit()
        temp.append([0,0])
        return temp

    def depict_fitness(self):
        x = range(0,len(self.bestgroup))
        y = []
        z = []
        for i in range(len(self.bestgroup)):
            y.append(self.bestgroup[i][-1][0])
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
        elif self.decision == DECISION_INTEGRATE:
            name = 'integrate'
        plt.savefig(os.path.join(save_dir, 'fitness_{}.png'.format(name)))
        plt.close()

    def depict_average_variance(self,gene=None,list=None):
        x = []
        y = []
        for i in range(self.num):
            if gene == 0:
                x.append(list[i][-1][0])
                y.append(list[i][-1][1])
            else:
                x.append(self.group[i][-1][0])
                y.append(self.group[i][-1][1])
        plt.scatter(x,y)
        x_min = min(x)
        x_min = x_min*0.9 if x_min>0 else x_min*1.1
        plt.xlim(x_min,max(x)*1.1)
        plt.ylim(0,max(y)*1.1)
        plt.title("Rule Performance")
        plt.xlabel("Expectation")
        plt.ylabel("Variance")
        plt.grid(True)
        save_dir = '../output'
        if self.decision == DECISION_SPEED:
            name = 'speed'
        elif self.decision == DECISION_SELL:
            name = 'sell'
        elif self.decision == DECISION_CHARTER:
            name = 'charter'
        elif self.decision == DECISION_INTEGRATE:
            name = 'integrate'
        if gene == 0:
            plt.savefig(os.path.join(save_dir, 'Evaluation_{}_initial.png'.format(name)))
        else:
            plt.savefig(os.path.join(save_dir, 'Evaluation_{}.png'.format(name)))
        plt.close()

    def export_excel(self):
        rule_type = ''
        if self.decision == DECISION_SPEED:
            rule_type = 'speed'
        elif self.decision == DECISION_SELL:
            rule_type = 'sell'
        elif self.decision == DECISION_CHARTER:
            rule_type = 'charter'
        elif self.decision == DECISION_INTEGRATE:
            rule_type = 'integrate'
        path = '../output/ship_rule_{0}.xlsx'.format(rule_type)
        wb = openpyxl.load_workbook(path)
        sheet = wb['Sheet1']
        if self.decision == DECISION_INTEGRATE:
            for i in range(0,self.num*4,4):
                individual = self.group[int(i/4)]
                sheet.cell(row = i + 1, column = 1).value = 'rule{}'.format(i+1)
                for rule_index in range(len(RULE_SET)):
                    rule_for_X = individual[rule_index]
                    for j in range(self.num_condition_part*2):
                        if j == 0 or j == 1:
                            sheet.cell(row = i + 1 + rule_index, column = j + 2).value = OIL_PRICE_LIST[self.convert2to10_in_list(rule_for_X[j])]
                        elif j == 2 or j == 3:
                            sheet.cell(row = i + 1 + rule_index, column = j + 2).value = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule_for_X[j])]
                        else:
                            sheet.cell(row = i + 1 + rule_index, column = j + 2).value = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule_for_X[j])]
                    if RULE_SET[rule_index] == DECISION_SPEED:
                        sheet.cell(row = i + 1 + rule_index, column = self.num_condition_part*2 + 2).value = (VESSEL_SPEED_LIST[self.convert2to10_in_list(rule_for_X[-1])]
                                                                                                                if self.check_rule_is_adapted(rule_for_X)
                                                                                                                else 'NOT ADAPTED')
                    elif RULE_SET[rule_index] == DECISION_SELL:
                        sheet.cell(row = i + 1 + rule_index, column = self.num_condition_part*2 + 2).value = (SELL_NUMBER[self.convert2to10_in_list(rule_for_X[-1])]
                                                                                                                if self.check_rule_is_adapted(rule_for_X)
                                                                                                                else 'NOT ADAPTED')
                    elif RULE_SET[rule_index] == DECISION_CHARTER:
                        sheet.cell(row = i + 1 + rule_index, column = self.num_condition_part*2 + 2).value = ('{0}month charter, {1} ships'.format(CHARTER_PERIOD[self.convert2to10_in_list(rule_for_X[-2])],CHARTER_NUMBER[self.convert2to10_in_list(rule_for_X[-1])])
                                                                                                                if self.check_rule_is_adapted(rule_for_X)
                                                                                                                else 'NOT ADAPTED')
                sheet.cell(row = i + 1 + len(RULE_SET), column = 2).value = individual[-1][0]
                sheet.cell(row = i + 1 + len(RULE_SET), column = 3).value = individual[-1][1]
        else:
            for i in range(0,self.num):
                individual = self.group[i]
                sheet.cell(row = i + 1, column = 1).value = 'rule{}'.format(i+1)
                for j in range(self.num_condition_part*2):
                    if j == 0 or j == 1:
                        sheet.cell(row = i + 1, column = j + 2).value = OIL_PRICE_LIST[self.convert2to10_in_list(individual[j])]
                    elif j == 2 or j == 3:
                        sheet.cell(row = i + 1, column = j + 2).value = FREIGHT_RATE_LIST[self.convert2to10_in_list(individual[j])]
                    else:
                        sheet.cell(row = i + 1, column = j + 2).value = EXCHANGE_RATE_LIST[self.convert2to10_in_list(individual[j])]
                if self.decision == DECISION_SPEED:
                    sheet.cell(row = i + 1, column = self.num_condition_part*2 + 2).value = (VESSEL_SPEED_LIST[self.convert2to10_in_list(individual[-2])]
                                                                                                if self.check_rule_is_adapted(individual)
                                                                                                else 'NOT ADAPTED')
                elif self.decision == DECISION_SELL:
                    sheet.cell(row = i + 1, column = self.num_condition_part*2 + 2).value = (SELL_NUMBER[self.convert2to10_in_list(individual[-2])]
                                                                                                if self.check_rule_is_adapted(individual)
                                                                                                else 'NOT ADAPTED')
                elif self.decision == DECISION_CHARTER:
                    sheet.cell(row = i + 1, column = self.num_condition_part*2 + 2).value = ('{0}month charter, {1} ships'.format(CHARTER_PERIOD[self.convert2to10_in_list(individual[-3])],CHARTER_NUMBER[self.convert2to10_in_list(individual[-2])])
                                                                                                if self.check_rule_is_adapted(individual)
                                                                                                else 'NOT ADAPTED')
                sheet.cell(row = i + 1, column = self.num_condition_part*2 + 1 + 2).value = individual[-1][0]
                sheet.cell(row = i + 1, column = self.num_condition_part*2 + 2 + 2).value = individual[-1][1]
        wb.save(path)
        wb.close()
        print('saving changes')

    def compare_rules(self):
        fitness_no_rule = self.fitness_function(self.compare_rule)[0]
        if self.decision == DECISION_INTEGRATE:
            name = 'integrate'
            fitness_best = self.bestgroup[-1][-1][0]
            fitness_full_search = 0
        else:
            if self.decision == DECISION_SPEED:
                name = 'speed'
                fitness_best = self.bestgroup[-1][-1][0]
                fitness_full_search = self.full_search_method_speed()
            elif self.decision == DECISION_SELL:
                name = 'sell'
                fitness_best = 0
                for i in range(self.num):
                    if self.group[i][-2][0] != ACTION_STAY:
                        if self.check_rule_is_adapted(self.group[i]):
                            fitness_best = self.group[i][-1][0]
                            break
                fitness_full_search = self.full_search_method_sell()
            elif self.decision == DECISION_CHARTER:
                name = 'charter'
                fitness_best = 0
                for i in range(self.num):
                    if self.group[i][-2][0] != ACTION_STAY:
                        if self.check_rule_is_adapted(self.group[i]):
                            fitness_best = self.group[i][-1][0]
                            break
                fitness_full_search =  self.full_search_method_charter()
            else:
                print('selected decision item does not exist')
                sys.exit()
        #for sets of rules extracted by the algorithm
        #fitness_set_of_rule = self.fitness_function(None)
        #print('fitness sets of rule',fitness_set_of_rule)
        print('no rule         ',fitness_no_rule)
        print('best rule       ',fitness_best)
        print('full search rule',fitness_full_search)
        left = [1,2,3]
        height = [fitness_no_rule,fitness_best,fitness_full_search]
        label = ['no rule','best rule','full search']
        plt.title('Comparison among three decision rule')
        plt.ylabel('fitness')
        min_fit = min(fitness_no_rule,min(fitness_best,fitness_full_search))
        max_fit = max(fitness_no_rule,max(fitness_best,fitness_full_search))
        if max_fit < 0:
            plt.ylim(min_fit*1.1,max_fit*0.9)
        else:
            if min_fit < 0:
                plt.ylim(min_fit*1.1,max_fit*1.1)
            else:
                plt.ylim(min_fit*0.9,max_fit*1.1)
        colorlist = ['b','b','b']
        for i in range(len(height)):
            if height[i] < 0:
                colorlist[i] = 'r'
        plt.bar(left,height,color=colorlist,tick_label=label,align='center')
        save_dir = '../output'
        plt.savefig(os.path.join(save_dir, 'comparison_{}.png'.format(name)))
        plt.close()

    def full_search_method_speed(self):
        cash = 0
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            for year in range(VESSEL_LIFE_TIME):
                cash_year = 0
                for month in range(12):
                    list = []
                    ship = Ship(self.TEU_size,self.init_speed,self.route_distance)
                    current_oil_price = self.oil_price_data[pattern][year*12+month]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][year*12+month]['price']
                    current_freight_rate_return = self.freight_rate_return_data[pattern][year*12+month]['price']
                    total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    ship.calculate_idle_rate(current_freight_rate_outward)
                    for speed in VESSEL_SPEED_LIST:
                        search_ship = Ship(self.TEU_size,speed,self.route_distance)
                        cash_flow = search_ship.calculate_income_per_month(current_oil_price,total_freight)
                        list.append([cash_flow,speed])
                    list.sort(key=lambda x:x[0],reverse = True)
                    ship.change_speed(list[0][1])
                    cash_year += ship.calculate_income_per_month(current_oil_price,total_freight)
                DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
                cash_year *= self.exchange_rate[pattern][year*12+11]['price']
                cash += cash_year/DISCOUNT
            cash -= -INITIAL_COST_OF_SHIPBUIDING*INITIAL_NUMBER_OF_SHIPS*self.exchange_rate[pattern][0]['price']
        cash /= DEFAULT_PREDICT_PATTERN_NUMBER
        cash /= HUNDRED_MILLION
        cash /= INITIAL_NUMBER_OF_SHIPS
        return cash

    def full_search_method_sell(self):
        list = []
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            fitness_list = []
            for i in range(VESSEL_LIFE_TIME*12+1):
                ship = Ship(self.TEU_size,self.init_speed,self.route_distance)
                fitness_list.append([-INITIAL_COST_OF_SHIPBUIDING*INITIAL_NUMBER_OF_SHIPS*self.exchange_rate[pattern][0]['price'],0,i,ship])
            for time in range(VESSEL_LIFE_TIME*12):
                current_oil_price = self.oil_price_data[pattern][time]['price']
                current_freight_rate_outward = self.freight_rate_outward_data[pattern][time]['price']
                current_freight_rate_return = self.freight_rate_return_data[pattern][time]['price']
                total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                for index in range(VESSEL_LIFE_TIME*12+1):
                    fitness_list[index][-1].calculate_idle_rate(current_freight_rate_outward)
                    if index < time:
                        pass
                    elif index == time:
                        fitness_list[index][1] += fitness_list[index][-1].sell_ship(self.freight_rate_outward_data[pattern],time,100)
                    else:
                        fitness_list[index][1] += fitness_list[index][-1].calculate_income_per_month(current_oil_price,total_freight)
                if (time + 1) % 12 == 0:
                    for index in range(VESSEL_LIFE_TIME*12+1):
                        cash_year = fitness_list[index][1]
                        DISCOUNT = (1 + DISCOUNT_RATE) ** ((time+1)/12)
                        cash_year *= self.exchange_rate[pattern][time]['price']
                        fitness_list[index][0] += cash_year/DISCOUNT
                        fitness_list[index][1] = 0
            fitness_list.sort(key=lambda x:x[0],reverse = True)
            list.append(fitness_list[0][0]/(HUNDRED_MILLION*INITIAL_NUMBER_OF_SHIPS))
        best = 0
        for e in range(len(list)):
            best += list[e]
        return best/DEFAULT_PREDICT_PATTERN_NUMBER

    def full_search_method_charter(self):
        fitness = []
        for period in [0,1,2,3]:
            fitness.append([-INITIAL_COST_OF_SHIPBUIDING*INITIAL_NUMBER_OF_SHIPS*self.exchange_rate[0][0]['price']*DEFAULT_PREDICT_PATTERN_NUMBER,period])
            for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
                #charter_list = [] # check whether or not do charter in each time with this
                ship = Ship(self.TEU_size,self.init_speed,self.route_distance)
                store = []
                store.append([0,[],0])
                for time in range(1,CHARTER_PERIOD[period]):
                    oil_price = self.oil_price_data[pattern][-time]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][-time]['price']
                    current_freight_rate_return = self.freight_rate_return_data[pattern][-time]['price']
                    freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    ship.calculate_idle_rate(current_freight_rate_outward)
                    time_reverse_0 = 180 - time
                    year_cash_0 = int(time_reverse_0/12) + 1
                    DISCOUNT_cash_0 = (1 + DISCOUNT_RATE) ** year_cash_0
                    exchange_cash_0 = self.exchange_rate[pattern][year_cash_0*12-1]['price']
                    cash_0 = ship.calculate_income_per_month(oil_price,freight)*exchange_cash_0/DISCOUNT_cash_0
                    charter_0 = 0
                    for a in range(time_reverse_0,180):
                        year_charter_0 = int(a/12) + 1
                        DISCOUNT_charter_0 = (1 + DISCOUNT_RATE) ** year_charter_0
                        exchange_charter_0 = self.exchange_rate[pattern][year_charter_0*12-1]['price']
                        ship.idle_rate = 0
                        charter_0 += ship.calculate_income_per_month(oil_price,freight)*RISK_PREMIUM*exchange_charter_0/DISCOUNT_charter_0
                    if cash_0 + store[time-1][0] > charter_0:
                        store.append([cash_0 + store[time-1][0],[1],time])
                        #charter_list.append(['STAY',VESSEL_LIFE_TIME*12-time])
                    else:
                        store.append([charter_0,[0],time])
                        #charter_list.append(['CHARTER',VESSEL_LIFE_TIME*12-time])
                for x in range(CHARTER_PERIOD[period],VESSEL_LIFE_TIME*12+1):
                    oil_price_fx = self.oil_price_data[pattern][-x]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][-x]['price']
                    current_freight_rate_return = self.freight_rate_return_data[pattern][-x]['price']
                    freight_fx = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    ship.calculate_idle_rate(current_freight_rate_outward)
                    time_reverse_x = 180 - x
                    year_cash_x = int(time_reverse_x/12) + 1
                    DISCOUNT_cash_x = (1 + DISCOUNT_RATE) ** year_cash_x
                    exchange_cash_x = self.exchange_rate[pattern][year_cash_x*12-1]['price']
                    cash_x = ship.calculate_income_per_month(oil_price_fx,freight_fx)*exchange_cash_x/DISCOUNT_cash_x
                    charter_x = 0
                    for a in range(time_reverse_x,time_reverse_x+CHARTER_PERIOD[period]):
                        year_charter_x = int(a/12) + 1
                        DISCOUNT_charter_x = (1 + DISCOUNT_RATE) ** year_charter_x
                        exchange_charter_x = self.exchange_rate[pattern][year_charter_x*12-1]['price']
                        ship.idle_rate = 0
                        charter_x += ship.calculate_income_per_month(oil_price_fx,freight_fx)*RISK_PREMIUM/DISCOUNT_charter_x
                    if cash_x + store[-1][0] > charter_x + store[-CHARTER_PERIOD[period]][0]:
                        store.append([cash_x + store[-1][0],[1],x])
                        #charter_list.append(['STAY',VESSEL_LIFE_TIME*12-x])
                    else:
                        store.append([charter_x + store[-CHARTER_PERIOD[period]][0],[0],x])
                        #charter_list.append(['CHARTER',VESSEL_LIFE_TIME*12-x])
                '''
                charter_list.reverse()
                path = '../output/full_rule_charter.xlsx'
                w = openpyxl.load_workbook(path)
                sheet = w['Sheet{}'.format(period+1)]
                for i in range(VESSEL_LIFE_TIME*12):
                    sheet.cell(row = i + 1, column = pattern + 1).value = charter_list[i][0]
                w.save(path)
                w.close()
                '''
                '''
                store.reverse()
                a = 0
                for year in range(0,VESSEL_LIFE_TIME):
                    cash_of_year = store[year*12][0] - store[year*12 + 12][0]
                    DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
                    a += cash_of_year/DISCOUNT
                fitness[period][0] += a/HUNDRED_MILLION
                '''
                fitness[period][0] += store[-1][0]
            fitness[period][0] /= HUNDRED_MILLION
            fitness[period][0] /= INITIAL_NUMBER_OF_SHIPS
            fitness[period][0] /= DEFAULT_PREDICT_PATTERN_NUMBER
        fitness.sort(key=lambda x:x[0],reverse = True)
        return fitness[0][0]

    def check_rule_is_adapted(self,rule):
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            for year in range(VESSEL_LIFE_TIME):
                for month in range(12):
                    oil_price = self.oil_price_data[pattern][year*12+month]['price']
                    freight= self.freight_rate_outward_data[pattern][year*12+month]['price']
                    exchange = self.exchange_rate[pattern][year*12+month]['price']
                    if self.decision == DECISION_INTEGRATE:
                        a = OIL_PRICE_LIST[self.convert2to10_in_list(rule[0])]
                        b = OIL_PRICE_LIST[self.convert2to10_in_list(rule[1])]
                        if a == b or ( a <= oil_price and oil_price <= b):
                            c = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule[2])]
                            d = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule[3])]
                            if c == d or ( c <= freight and freight <= d):
                                e = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule[4])]
                                f = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule[5])]
                                if e == f or ( e <= exchange and exchange <= f):
                                    return True
                    else:
                        result = self.adapt_rule(oil_price,freight,exchange,rule)
                        if result[0]:
                            return True
        return False

    def check_convergence(self,target,criteria):
        flag = True
        for index in range(1,criteria+1):
            if target[-index][-1] != target[-(index+1)][-1]:
                flag = False
                break
        return flag

    def execute_GA(self,priority=PRIORITY_SELL_CHARTER,method=ROULETTE):
        first = time.time()

        #randomly generating individual group
        for i in range(self.num):
            self.group.append(self.generateIndividual())

        #genetic algorithm
        for gene in tqdm(range(self.generation)):
            time.sleep(1/self.generation)
            crossing_time = time.time()
            #crossing
            self.temp = copy.deepcopy(self.group)
            for i in range(0,self.num,2):
                if random.random() < self.crossing_rate:
                    if self.decision == DECISION_SPEED:
                        a,b = self.crossing(self.temp[i],self.temp[i+1],self.num_condition_part*2+1)
                    elif self.decision == DECISION_SELL:
                        a,b = self.crossing(self.temp[i],self.temp[i+1],self.num_condition_part*2+1)
                    elif self.decision == DECISION_CHARTER:
                        a,b = self.crossing(self.temp[i],self.temp[i+1],self.num_condition_part*2+2)
                    elif self.decision == DECISION_INTEGRATE:
                        a,b = self.crossing(self.temp[i],self.temp[i+1])
                    else:
                        print('selected decision item does not exist')
                        sys.exit()
                    self.temp.append(a)
                    self.temp.append(b)
            print('crossing',time.time()-crossing_time)

            #mutation
            mutation_time = time.time()
            for individual in self.temp:
                if random.random() < self.alpha:
                    individual = self.mutation(individual)
            print('mutation',time.time()-mutation_time)

            #rule check
            if self.decision == DECISION_INTEGRATE:
                for k in range(len(self.temp)):
                    for rule_index in range(len(self.temp[k])-1):
                        rule_for_X = self.temp[k][rule_index]
                        a = OIL_PRICE_LIST[self.convert2to10_in_list(rule_for_X[0])]
                        b = OIL_PRICE_LIST[self.convert2to10_in_list(rule_for_X[1])]
                        c = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule_for_X[2])]
                        d = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule_for_X[3])]
                        e = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule_for_X[4])]
                        f = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule_for_X[5])]
                        if a > b:
                            X = copy.deepcopy(self.temp[k])
                            for element in range(4):
                                rule_for_X[0][element] = X[rule_index][1][element]
                                rule_for_X[1][element] = X[rule_index][0][element]
                        if c > d:
                            Y = copy.deepcopy(self.temp[k])
                            for element in range(4):
                                rule_for_X[2][element] = Y[rule_index][3][element]
                                rule_for_X[3][element] = Y[rule_index][2][element]
                        if e > f:
                            Z = copy.deepcopy(self.temp[k])
                            for element in range(4):
                                rule_for_X[4][element] = Z[rule_index][5][element]
                                rule_for_X[5][element] = Z[rule_index][4][element]
            else:
                for k in range(len(self.temp)):
                    a = OIL_PRICE_LIST[self.convert2to10_in_list(self.temp[k][0])]
                    b = OIL_PRICE_LIST[self.convert2to10_in_list(self.temp[k][1])]
                    c = FREIGHT_RATE_LIST[self.convert2to10_in_list(self.temp[k][2])]
                    d = FREIGHT_RATE_LIST[self.convert2to10_in_list(self.temp[k][3])]
                    e = EXCHANGE_RATE_LIST[self.convert2to10_in_list(self.temp[k][4])]
                    f = EXCHANGE_RATE_LIST[self.convert2to10_in_list(self.temp[k][5])]
                    if a > b:
                        X = copy.deepcopy(self.temp[k])
                        for element in range(4):
                            self.temp[k][0][element] = X[1][element]
                            self.temp[k][1][element] = X[0][element]
                    if c > d:
                        Y = copy.deepcopy(self.temp[k])
                        for element in range(4):
                            self.temp[k][2][element] = Y[3][element]
                            self.temp[k][3][element] = Y[2][element]
                    if e > f:
                        Z = copy.deepcopy(self.temp[k])
                        for element in range(4):
                            self.temp[k][4][element] = Z[5][element]
                            self.temp[k][5][element] = Z[4][element]

            #computation of fitness
            multifitness_time = time.time()
            self.priority = priority
            '''
            with Pool() as pool:
                p = pool.imap(self.multiproces_fitness, range(len(self.temp)),10)
                #for i in range(len(self.temp)):
                #p.sort(key=lambda x:x[0])
                #for i in range(len(p)):
                #    self.temp[i][-1][0], self.temp[i][-1][1] = p[i][1]
            '''
            '''
            num_pool = multi.cpu_count()
            pool = Pool(num_pool)
            for i in range(len(self.temp)):
                res = pool.apply_async(self.multiproces_fitness, (i,))
            pool.close()
            pool.join(10)
            print('multifitness',time.time()-multifitness_time)
            '''
            '''
            result = Parallel(n_jobs=-1)([delayed(self.multiproces_fitness)(n) for n in range(len(self.temp))])
            result.sort(key=lambda x:x[0])
            for i in range(len(result)):
                self.temp[i][-1][0], self.temp[i][-1][1] = result[i][1]
            '''

            fitness_time = time.time()
            for one in range(len(self.temp)):
                rule = self.temp[one]
                rule[-1][0], rule[-1][1] = self.fitness_function(rule,priority)
            print('fitness',time.time()-fitness_time)

            #reduce the number of individual
            #num -= 10

            #selection
            #store last generation's best individual unchanged
            if gene > 0:
                self.group[0] = self.bestgroup[gene-1]
            else:#this does not have meaning, just number adjustment
                self.group[0] = self.temp[0]
                self.depict_average_variance(gene,self.temp)
            if method == ROULETTE:#roulette selection and elite storing
                #store the best 5% individual
                self.temp.sort(key=lambda x:x[-1][0],reverse = True)
                elite_number = int(self.num * 0.05)
                for i in range(1,elite_number+1):
                    self.group[i] = self.temp[i]
                random.shuffle(self.temp)
                ark = 0 # the number used to roulette in crossing
                probability = 0
                for i in range(len(self.temp)):
                    probability = probability + max(0,self.temp[i][-1][0]) + 0.1
                roulette = 0
                for i in range(elite_number+1,self.num):
                    roulette = random.randint(0,int(probability))
                    while roulette > 0:
                        roulette = roulette - (max(0,self.temp[ark][-1][0]) + 0.1)
                        ark = (ark + 1) % self.num
                    self.group[i] = self.temp[ark]
            elif method == TOURNAMENT:#tournament selection
                for select in range(self.num-1):
                    tournament = []
                    for _ in range(6):
                        tournament.append(self.temp[random.randint(0,2*self.num-1)])
                    tournament.sort(key=lambda x:x[-1][0],reverse = True)
                    self.group[select] = tournament[0]
            elif method == STEADY_STATE:#steady state ga
                for i in range(0,len(self.temp),2):
                    if i + 1 < self.num:
                        store = []
                        store.append(self.temp[i])
                        store.append(self.temp[i+1])
                        if self.num + i < len(self.temp):
                            store.append(self.temp[self.num + i])
                        if self.num + i + 1 < len(self.temp):
                            store.append(self.temp[self.num + i+1])
                        store.sort(key=lambda x:x[-1][0],reverse = True)
                        self.group[i] = store[0]
                        self.group[i+1] = store[1]
            else:
                print('Selected method does not exist')
                sys.exit()
            self.group.sort(key=lambda x:x[-1][0],reverse = True)
            self.bestgroup.append(self.group[0])
            random.shuffle(self.group)
            total = 0
            for e in range(self.num):
                total += self.group[e][-1][0]
            self.averagegroup.append(total/self.num)
            #if gene > 10 and self.check_convergence(self.bestgroup,10):
            #    break

        #print result
        self.group.sort(key=lambda x:x[-1][0],reverse = True)
        for i in range(0,self.num):
            if i == 0:
                print('best rule', self.group[i])
            thisone = self.group[i]
            if self.decision == DECISION_INTEGRATE:
                for rule_index in range(len(RULE_SET)):
                    rule_for_X = thisone[rule_index]
                    a = OIL_PRICE_LIST[self.convert2to10_in_list(rule_for_X[0])]
                    b = OIL_PRICE_LIST[self.convert2to10_in_list(rule_for_X[1])]
                    c = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule_for_X[2])]
                    d = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule_for_X[3])]
                    e = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule_for_X[4])]
                    f = EXCHANGE_RATE_LIST[self.convert2to10_in_list(rule_for_X[5])]
                    if RULE_SET[rule_index] == DECISION_SPEED:
                        g = (VESSEL_SPEED_LIST[self.convert2to10_in_list(rule_for_X[-1])]
                                if self.check_rule_is_adapted(rule_for_X)
                                else 'NOT ADAPTED')
                    elif RULE_SET[rule_index] == DECISION_SELL:
                        g = ('sell {} ships'.format(SELL_NUMBER[self.convert2to10_in_list(rule_for_X[-1])])
                                if self.check_rule_is_adapted(rule_for_X)
                                else 'NOT ADAPTED')
                    elif RULE_SET[rule_index] == DECISION_CHARTER:
                        g = ('{0}month charter, {1} ships'.format(CHARTER_PERIOD[self.convert2to10_in_list(rule_for_X[-2])],CHARTER_NUMBER[self.convert2to10_in_list(rule_for_X[-1])])
                                if self.check_rule_is_adapted(rule_for_X)
                                else 'NOT ADAPTED')
                    if i < NUM_DISPLAY:
                        print('{0} <= oil price <= {1} and {2} <= freight <= {3} and {4} <= exchange <= {5} -> {6}'.format(a,b,c,d,e,f,g))
                if i < NUM_DISPLAY:
                    print('Expectation = {}'.format(thisone[-1][0]))
                    print('Variance = {}'.format(thisone[-1][1]))
            else:
                a = OIL_PRICE_LIST[self.convert2to10_in_list(thisone[0])]
                b = OIL_PRICE_LIST[self.convert2to10_in_list(thisone[1])]
                c = FREIGHT_RATE_LIST[self.convert2to10_in_list(thisone[2])]
                d = FREIGHT_RATE_LIST[self.convert2to10_in_list(thisone[3])]
                e = EXCHANGE_RATE_LIST[self.convert2to10_in_list(thisone[4])]
                f = EXCHANGE_RATE_LIST[self.convert2to10_in_list(thisone[5])]
                if self.decision == DECISION_SPEED:
                    g = (VESSEL_SPEED_LIST[self.convert2to10_in_list(thisone[-2])]
                            if self.check_rule_is_adapted(thisone)
                            else 'NOT ADAPTED')
                elif self.decision == DECISION_SELL:
                    g = ('sell {} ships'.format(SELL_NUMBER[self.convert2to10_in_list(thisone[-2])])
                            if self.check_rule_is_adapted(thisone)
                            else 'NOT ADAPTED')
                elif self.decision == DECISION_CHARTER:
                    g = ('{0}month charter, {1} ships'.format(CHARTER_PERIOD[self.convert2to10_in_list(thisone[-3])],CHARTER_NUMBER[self.convert2to10_in_list(thisone[-2])])
                            if self.check_rule_is_adapted(thisone)
                            else 'NOT ADAPTED')
                if i < NUM_DISPLAY and self.check_rule_is_adapted(thisone):
                    print('{0} <= oil price <= {1} and {2} <= freight <= {3} and {4} <= exchange <= {5} -> {6}'.format(a,b,c,d,e,f,g))
                    print('Expectation = {}'.format(thisone[-1][0]))
                    print('Variance = {}'.format(thisone[-1][1]))
                if a > b or c > d or e > f:
                    print('rule error')
                    sys.exit()
        print('finish')
        exe = time.time() - first
        print('Spent time is {0}'.format(exe))
        self.depict_fitness()
        self.depict_average_variance()
        self.export_excel()
        self.compare_rules()

        #initialize attribute
        self.gruop = []
        self.bestgroup = []
        self.averagegroup = []

def main():
    generated_sinario = load_generated_sinario()
    oil_data = generated_sinario[0]
    freight_outward_data = generated_sinario[1]
    freight_return_data = generated_sinario[2]
    exchange_data = generated_sinario[3]
    args = sys.argv
    if args[1] == '1':
        depict_distribution(oil_data,freight_outward_data,exchange_data)
        ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
                    TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
                    DECISION_SPEED)
        ga.execute_GA()
    elif args[1] == '2':
        ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
                    TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
                    DECISION_SELL)
        ga.execute_GA()
    elif args[1] == '3':
        ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
                    TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
                    DECISION_CHARTER)
        ga.execute_GA()
    elif args[1] == '4':
        ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
                    TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
                    DECISION_INTEGRATE)
        ga.execute_GA()
    else:
        print('No one selected')
        print(args)

if __name__ == "__main__":
    main()
