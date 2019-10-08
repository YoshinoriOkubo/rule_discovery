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

    def __init__(self,oil_price_data,freight_rate_outward,freight_rate_return,TEU_size,init_speed,route_distance,generation=None,num=None,alpha=None,crossing_rate=None):
        self.oil_price_data = oil_price_data #oil_price_history_data
        self.freight_rate_outward_data = freight_rate_outward #feright rate outward history data
        self.freight_rate_return_data = freight_rate_return # freight rate return history data
        self.TEU_size = TEU_size #size of ship(TEU)
        self.init_speed = init_speed # initial speed of ship (km/h)
        self.route_distance = route_distance # distance of fixed route (km)
        self.generation = generation if generation else DEFAULT_GENERATION # the number of generation
        self.num = num if num else DEFAULT_NUM_OF_INDIVIDUAL  # the number of individual
        self.alpha = alpha if alpha else DEFAULT_ALPHA # the rate of mutation
        self.crossing_rate = crossing_rate if crossing_rate else DEFAULT_CROSSING_RATE
        self.group = [] # group that has individual
        self.bestgroup = [] # group that has the best individuals in each generation
        self.averagegroup = [] # the average value of fitness in each generation
        #self.average_fitness = 0 # the average value of fitness

    def convert2to10_in_list(self,list):
        result = 0
        length = len(list)
        for i in range(len(list)):
            x = length - 1 - i
            #print(list[i],x)
            result += list[i] * 2 ** (x)
        return GRAY_CODE[result]

    def convert2to10(self,x1,x2,x3,x4,x5):
        return x1*16 + x2*8 + x3*4 + x4*2 + x5

    def convert2to10(self,x1,x2,x3,x4,x5,x6,x7):
        return x1*64 + x2*32 + x3*16 + x4*8 + x5*4 + x6*2 + x7

    def adapt_rule(self,oil_price,speed,freight,rule):
        a = OIL_PRICE_LIST[self.convert2to10_in_list(rule[0])]
        b = OIL_PRICE_LIST[self.convert2to10_in_list(rule[1])]
        if a == b or ( a < oil_price and oil_price < b):
            c = VESSEL_SPEED_LIST[self.convert2to10_in_list(rule[2])]
            d = VESSEL_SPEED_LIST[self.convert2to10_in_list(rule[3])]
            if c == d or (c < speed and speed < d):
                e = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule[4])]
                f = FREIGHT_RATE_LIST[self.convert2to10_in_list(rule[5])]
                if e == f or ( e < freight and freight < f):
                    return [True,VESSEL_SPEED_LIST[self.convert2to10_in_list(rule[-2])]]
        return [False]

    def exchange(self,rule,p1,p2):
        newRule = []
        for i in range(len(rule)-2):
            if i == p1:
                newRule.append(copy.deepcopy(rule[p2]))
            else:
                if i == p2:
                    newRule.append(copy.deepcopy(rule[p1]))
                else:
                    newRule.append(copy.deepcopy(rule[i]))
        newRule.append(rule[-2])
        newRule.append(rule[-1])
        return newRule

    def crossing(self,a,b,num_block):
        #for exapmle, a = [ [1,0,0,0], [0,1,0,1],[1,1,1,0],[0,0,0,0],[1,1,0,0],[1,0,0,1],[1,0,0,1],0]
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

    '''
    def mutation(self,individual):
        x = random.randint(0,5)
        if x == 4:
            individual[x] = random.randint(0,2) - 1
        else:
            if x == 5:
                individual[x] = random.randint(0,3)
            else:
                length = len(individual[x]) - 1
                point = random.randint(0,length)
                individual[x][point] = (individual[x][point] + 1) % 2
        return individual
    '''

    def mutation(self,individual):
        for x in range(len(individual)-1):
            length = len(individual[x]) - 1
            point = random.randint(0,length)
            individual[x][point] = (individual[x][point] + 1) % 2
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
    def fitness_function(self,rule):
        #converge = 0
        ship = Ship(self.TEU_size,self.init_speed,self.route_distance)
        average_fitness = 0
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            fitness = -1 * INITIAL_COST_OF_SHIPBUIDING
            for year in range(VESSEL_LIFE_TIME):
                cash_flow = 0
                for month in range(12):
                    current_oil_price = self.oil_price_data[pattern][month]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][month]['price']
                    current_freight_rate_return = self.freight_rate_return_data[pattern][month]['price']
                    total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    result = self.adapt_rule(current_oil_price,ship.speed,total_freight,rule)
                    if result[0]:
                        #converge += 1
                        ship.change_speed(result[1])
                    cash_flow += ship.calculate_income_per_month(current_oil_price,current_freight_rate_outward,current_freight_rate_return)
                DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
                average_fitness += cash_flow / DISCOUNT
            ship.chagne_speed_to_initial()
        average_fitness /= DEFAULT_PREDICT_PATTERN_NUMBER
        average_fitness /= 100000000
        return max(0,average_fitness)# + converge/(DEFAULT_PREDICT_PATTERN_NUMBER*VESSEL_LIFE_TIME*12))

    def generateIndividual(self):#graycode
        temp = []
        for i in range(2):
            temp.append([])
            for j in range(4):
                temp[i].append(random.randint(0,1))
        for a in range(2):
            temp.append([])
            for b in range(4):
                temp[a+2].append(random.randint(0,1))
        for c in range(2):
            temp.append([])
            for d in range(4):
                temp[c+4].append(random.randint(0,1))
        temp.append([])
        for e in range(4):
            temp[6].append(random.randint(0,1))
        temp.append(0)
        return temp

    def depict(self):
        x = range(0,len(self.bestgroup))
        y = []
        z = []
        for i in range(len(self.bestgroup)):
            y.append(self.bestgroup[i][-1])
            z.append(self.averagegroup[i])
        plt.plot(x, y, marker='o',label='best')
        plt.plot(x, z, marker='x',label='average')
        plt.title('Transition of fitness', fontsize = 20)
        plt.xlabel('generation', fontsize = 16)
        plt.ylabel('fitness value', fontsize = 16)
        plt.tick_params(labelsize=14)
        plt.grid(True)
        plt.legend(loc = 'lower right')
        save_dir = '../image'
        plt.savefig(os.path.join(save_dir, 'fitness.png'))
        #plt.show()

    def export_excel(self):
        wb = openpyxl.load_workbook('../output/ship_rule.xlsx')
        sheet = wb['Sheet1']
        for i in range(0,self.num):
            individual = self.group[i]
            sheet.cell(row = i + 1, column = 1).value = 'rule{}'.format(i+1)
            for j in range(len(individual)):
                if j < len(individual) - 1:
                    if j == 2 or j == 3 or j == 6:
                        sheet.cell(row = i + 1, column = j + 2).value = VESSEL_SPEED_LIST[self.convert2to10_in_list(individual[j])]
                    elif j == 0 or j == 1:
                        sheet.cell(row = i + 1, column = j + 2).value = OIL_PRICE_LIST[self.convert2to10_in_list(individual[j])]
                    else:
                        sheet.cell(row = i + 1, column = j + 2).value = FREIGHT_RATE_LIST[self.convert2to10_in_list(individual[j])]
                else:
                    sheet.cell(row = i + 1, column = j + 2).value = individual[j]
        wb.save('../output/ship_rule.xlsx')
        print('saving changes')

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
                    a,b = self.crossing(temp[i],temp[i+1],6)
                    temp.append(a)
                    temp.append(b)

            #mutation
            for individual in temp:
                if random.random() < self.alpha:
                    individual = self.mutation(individual)

            #rule check
            for k in range(len(temp)):
                rule = temp[k]
                lower = self.convert2to10_in_list(rule[0])
                upper = self.convert2to10_in_list(rule[1])
                if lower > upper:
                    temp[k] = self.exchange(rule,0,1)
                lower = self.convert2to10_in_list(rule[2])
                upper = self.convert2to10_in_list(rule[3])
                if lower > upper:
                    temp[k] = self.exchange(rule,2,3)
                lower = self.convert2to10_in_list(rule[4])
                upper = self.convert2to10_in_list(rule[5])
                if lower > upper:
                    temp[k] = self.exchange(rule,4,5)

            #computation of fitness
            for one in range(len(temp)):
                rule = temp[one]
                rule[-1] = self.fitness_function(rule)

            #reduce the number of individual
            #num -= 10

            #selection

            #steady state ga
            #'''
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
            self.bestgroup.append(self.group[0])
            total = 0
            for e in range(self.num):
                total += self.group[e][-1]
            self.averagegroup.append(total/self.num)
            #'''
            '''
            #tournament selection
            for select in range(self.num):
                tournament = []
                for _ in range(6):
                    tournament.append(temp[random.randint(0,2*self.num-1)])
                tournament.sort(key=lambda x:x[-1],reverse = True)
                self.group[select] = tournament[0]
            self.group.sort(key=lambda x:x[-1],reverse = True)
            self.bestgroup.append(self.group[0])
            total = 0
            for e in range(self.num):
                total += self.group[e][-1]
            self.averagegroup.append(total/self.num)
            '''

            '''
            #roulette selection
            #store the best individual
            temp.sort(key=lambda x:x[-1],reverse = True)
            self.group[0] = temp[0]
            ark = 0 # the number used to roulette in crossing
            probability = 0
            for i in range(len(temp)):
                probability += temp[i][-1]
            roulette = 0
            for i in range(1,self.num):
                roulette = random.randint(0,int(probability))
                while roulette > 0:
                    roulette -= temp[ark][-1]
                    ark = (ark + 1) % self.num
                self.group[i] = temp[ark]
            #self.group.sort(key=lambda x:x[-1],reverse = True)
            self.bestgroup.append(self.group[0])
            total = 0
            for e in range(self.num):
                total += self.group[e][-1]
            self.averagegroup.append(total/self.num)
            #if gene > 10 and self.bestgroup[-1] == self.bestgroup[-4]:
            #    break
            '''
        #print result
        self.group.sort(key=lambda x:x[-1],reverse = True)
        for i in range(0,self.num):
            if i == 0:
                print(self.group[i])
            thisone = self.group[i]
            a = OIL_PRICE_LIST[self.convert2to10_in_list(thisone[0])]
            b = OIL_PRICE_LIST[self.convert2to10_in_list(thisone[1])]
            c = VESSEL_SPEED_LIST[self.convert2to10_in_list(thisone[2])]
            d = VESSEL_SPEED_LIST[self.convert2to10_in_list(thisone[3])]
            e = FREIGHT_RATE_LIST[self.convert2to10_in_list(thisone[4])]
            f = FREIGHT_RATE_LIST[self.convert2to10_in_list(thisone[5])]
            h = VESSEL_SPEED_LIST[self.convert2to10_in_list(thisone[-2])]
            #if thisone[9] > 400:
            print('{0} < oil price < {1} and {2} < speed < {3} and {4} < freight < {5} -> {6}  fitness value = {7}'.format(a,b,c,d,e,f,h,thisone[-1]))
        print('finish')
        exe = time.time() - first
        print('Spent time is {0}'.format(exe))
        self.export_excel()
