import random
import copy
import time
import sys
import numpy
from oil_price import Sinario
from ship import Ship
# import own modules #
sys.path.append('../public')
from constants  import *

class GA:

    def __init__(self,history_data,generation=None,num=None,alpha=None):
        self.history_data = history_data#oil_price_history_data
        self.generation = generation if generation else 50 # the number of generation
        self.num = num if num else 100  # the number of individual
        self.alpha = alpha if alpha else 0.05 # the rate of mutation
        self.group = [] # group that has individual

    def convert2to10_in_list(self,list):
        result = 0
        length = len(list)
        for i in range(len(list)):
            x = length - 1 - i
            #print(list[i],x)
            result += list[i] * 2 ** (x)
        return result

    def convert2to10(self,x1,x2,x3,x4,x5):
        return x1*16 + x2*8 + x3*4 + x4*2 + x5

    def convert2to10(self,x1,x2,x3,x4,x5,x6,x7):
        return x1*64 + x2*32 + x3*16 + x4*8 + x5*4 + x6*2 + x7

    def adapt_rule(self,oil_price,speed,rule):
        if self.convert2to10_in_list(rule[0]) < oil_price and oil_price < self.convert2to10_in_list(rule[1]):
            if self.convert2to10_in_list(rule[2]) < speed and speed < self.convert2to10_in_list(rule[3]):
                return [True,rule[4]*rule[5]]
            else:
                return [False]
        else:
            return [False]

    def exchange(self,rule,p1,p2):
        newRule = []
        for i in range(len(rule)-3):
            if i == p1:
                newRule.append(copy.deepcopy(rule[p2]))
            else:
                if i == p2:
                    newRule.append(copy.deepcopy(rule[p1]))
                else:
                    newRule.append(copy.deepcopy(rule[i]))
        newRule.append(rule[4])
        newRule.append(rule[5])
        newRule.append(rule[6])
        return newRule

    def crossing(self,a,b,num_block):
        #for exapmle, a = [ [0,0,1,1,0,0,1], [0,1,0,1,0,1,0,1],[0,0,0,0,0],[0,0,0,0,1],-1,3,0]
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

    def fitness_function(self,history_data,rule):
        ship = Ship(12000,25,9000)
        fitness = 0
        for month in range(VESSEL_LIFE_TIME * 12):
            result = self.adapt_rule(history_data[month][1],ship.speed,rule)
            if result[0]:
                ship.change_speed(ship.speed + result[1])
            fitness += ship.calculate_income_per_month(history_data[month][1])
        return round(fitness / 10000000)

    def generateIndividual(self):
        temp = []
        for i in range(2):
            temp.append([])
            for j in range(7):
                temp[i].append(random.randint(0,1))
        for a in range(2):
            temp.append([])
            for b in range(5):
                temp[a+2].append(random.randint(0,1))
        sign = random.randint(0,2)-1
        temp.append(sign)
        temp.append(random.randint(0,3))
        temp.append(0)
        return temp

    def execute_GA(self):
        first = time.time()

        #randomly generating individual group
        for i in range(self.num):
            self.group.append(self.generateIndividual())

        #genetic algorithm
        for gene in range(self.generation):
            print('{}%完了'.format(gene*100.0/self.generation))
            #crossing
            temp = copy.deepcopy(self.group)
            for i in range(0,self.num,2):
                a,b = self.crossing(temp[i],temp[i+1],4)
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

            #computation of fitness
            for one in range(len(temp)):
                rule = temp[one]
                rule[-1] = self.fitness_function(self.history_data,rule)

            #reduce the number of individual
            #num -= 10

            #selection
            ark = 0 # the number used to roulette in crossing
            probability = 0
            for i in range(len(temp)):
                probability += temp[i][-1]
            roulette = 0
            for i in range(self.num):
                roulette = random.randint(0,int(probability))
                while roulette > 0:
                    roulette -= temp[ark][-1]
                    ark = (ark + 1) % self.num
                self.group[i] = temp[ark]

        #print result
        self.group.sort(key=lambda x:x[-1],reverse = True)
        for i in range(0,self.num):
            thisone = self.group[i]
            a = self.convert2to10_in_list(thisone[0])
            b = self.convert2to10_in_list(thisone[1])
            c = self.convert2to10_in_list(thisone[2])
            d = self.convert2to10_in_list(thisone[3])
            #if thisone[9] > 400:
            print('{0} < oil price < {1} and {2} < speed < {3} -> {4}  fitness value = {5}'.format(a,b,c,d,thisone[4]*thisone[5],thisone[-1]))
        print('finish')
        exe = time.time() - first
        print('Spent time is {0}'.format(exe))
