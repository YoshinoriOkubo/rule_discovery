import random
import copy
import time
import sys
import matplotlib.pyplot as plt
import os
from multiprocessing import Pool
import multiprocessing as multi
from ship import Ship
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

    def __init__(self,oil_price_data,freight_rate_outward,freight_rate_return,exchange_rate,demand,supply,actionlist,generation=None,population_size=None,alpha=None,crossover_rate=None):
        self.oil_price_data = oil_price_data #oil price predicted data
        self.freight_rate_outward_data = freight_rate_outward #feright rate outward predicted data
        self.freight_rate_return_data = freight_rate_return # freight rate return predicted data
        self.exchange_rate_data = exchange_rate # exchange_rate predicted data
        self.demand_data = demand#ship demand predicted data
        self.supply_data = supply#ship supply predicted data
        self.actionlist = actionlist # decision of action parts.
        self.generation = generation if generation else DEFAULT_GENERATION # the number of generation
        self.population_size = population_size if population_size else DEFAULT_POPULATION_SIZE  # the number of individual
        self.alpha = alpha if alpha else DEFAULT_ALPHA # the rate of mutation
        self.crossover_rate = crossover_rate if crossover_rate else DEFAULT_CROSSOVER_RATE
        self.population = [] # population that has individual
        self.temp = [] #temporary group that has individuals
        self.bestpopulation = [] # group that has the best individuals in each generation
        self.averagepopulation = [] # the average value of fitness in each generation

    def adapt_rule(self,oil_price,freight,exchange,own_ship,rule):
        a = OIL_PRICE_LIST[convert2to10_in_list(rule[0])]
        b = OIL_PRICE_LIST[convert2to10_in_list(rule[1])]
        if a <= oil_price and oil_price <= b:
            c = FREIGHT_RATE_LIST[convert2to10_in_list(rule[2])]
            d = FREIGHT_RATE_LIST[convert2to10_in_list(rule[3])]
            if c <= freight and freight <= d:
                e = EXCHANGE_RATE_LIST[convert2to10_in_list(rule[4])]
                f = EXCHANGE_RATE_LIST[convert2to10_in_list(rule[5])]
                if e <= exchange and exchange <= f:
                    g = OWN_SHIP_LIST[convert2to10_in_list(rule[6])]
                    h = OWN_SHIP_LIST[convert2to10_in_list(rule[7])]
                    if g <= own_ship and own_ship <= h:
                        result = [True]
                        result.append([])
                        result[1].append(VESSEL_SPEED_LIST[self.actionlist[0]])
                        result[1].append(PURCHASE_NUMBER[self.actionlist[1]])
                        result[1].append(PURCHASE_NUMBER[self.actionlist[2]])
                        result[1].append(SELL_NUMBER[self.actionlist[3]])
                        result[1].append(CHARTER_IN_NUMBER[self.actionlist[4]])
                        result[1].append(CHARTER_OUT_NUMBER[self.actionlist[5]])
                        return result
        return [False]

    def check_rule_is_adapted(self,rule):
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            for year in range(VESSEL_LIFE_TIME):
                for month in range(12):
                    oil_price = self.oil_price_data[pattern][year*12+month]['price']
                    freight= self.freight_rate_outward_data[pattern][year*12+month]['price']
                    exchange = self.exchange_rate_data[pattern][year*12+month]['price']
                    result = self.adapt_rule(oil_price,freight,exchange,INITIAL_NUMBER_OF_SHIPS,rule)
                    if result[0]:
                        return True
        return False

    def generateIndividual(self):
        temp = []
        for condition in range(DEFAULT_NUM_OF_CONDITION*2):
            temp.append([])
            for a in range(4):
                temp[condition].append(random.randint(0,1))
        for action in range(DEFAULT_NUM_OF_ACTION):
            temp.append(self.actionlist[action])
        temp.append([0,0])
        temp[-1][0],temp[-1][1] = self.fitness_function(temp)
        return temp

    def crossover(self,a,b):
        temp1 = []
        temp2 = []
        crossover_block = random.randint(0,DEFAULT_NUM_OF_CONDITION*2-1)
        for condition in range(DEFAULT_NUM_OF_CONDITION*2):
            if condition == crossover_block:
                temp1.append([])
                temp2.append([])
                length = len(a[condition]) - 1
                crossover_point = random.randint(1,length-2)
                for former in range(0,crossover_point):
                    temp1[condition].append(a[condition][former])
                    temp2[condition].append(b[condition][former])
                for latter in range(crossover_point,len(a[condition])):
                    temp1[condition].append(b[condition][latter])
                    temp2[condition].append(a[condition][latter])
            else:
                temp1.append(a[condition])
                temp2.append(b[condition])
        for action in range(DEFAULT_NUM_OF_CONDITION*2,len(a)-1):
            temp1.append(a[action])
            temp2.append(b[action])
        temp1.append([0,0])
        temp2.append([0,0])
        return [temp1,temp2]

    def mutation(self,individual):
        mutation_block = random.randint(0,DEFAULT_NUM_OF_CONDITION*2-1)
        length = len(individual[mutation_block]) - 1
        point = random.randint(0,length)
        individual[mutation_block][point] = (individual[mutation_block][point] + 1) % 2
        return individual

    def fitness_function(self,rule):
        Record = []
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            fitness = 0
            ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
            for year in range(VESSEL_LIFE_TIME):
                cash_flow = 0
                for month in range(12):
                    current_oil_price = self.oil_price_data[pattern][year*12+month]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][year*12+month]['price']
                    current_freight_rate_return = self.freight_rate_return_data[pattern][year*12+month]['price']
                    total_freight = 0.5 * ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    current_exchange = self.exchange_rate_data[pattern][year*12+month]['price']
                    current_demand = self.demand_data[pattern][year*12+month]['price']
                    current_supply = self.supply_data[pattern][year*12+month]['price']
                    result = self.adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,rule)
                    if result[0]:
                        ship.change_speed(result[1][0])
                        cash_flow += ship.buy_new_ship(self.freight_rate_outward_data[pattern],year*12+month,result[1][1])
                        cash_flow += ship.buy_secondhand_ship(self.freight_rate_outward_data[pattern],year*12+month,result[1][2])
                        cash_flow += ship.sell_ship(self.freight_rate_outward_data[pattern],year*12+month,result[1][3])
                        ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][4],DECISION_CHARTER_IN)
                        ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][5],DECISION_CHARTER_OUT)
                        if ship.charter_flag == True:
                            cash_flow += ship.charter()
                            ship.end_charter()
                    cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                    cash_flow += ship.add_age()
                    ship.change_speed(INITIAL_SPEED)
                DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
                cash_flow *= self.exchange_rate_data[pattern][year*12+11]['price']
                fitness += cash_flow / DISCOUNT
            ship.sell_ship(self.freight_rate_outward_data[pattern],VESSEL_LIFE_TIME*12-1,ship.exist_number)
            fitness /= HUNDRED_MILLION
            fitness /= INITIAL_NUMBER_OF_SHIPS
            Record.append(fitness)
        e, sigma = calc_statistics(Record)
        return [e,sigma]

    def selection(self):
        #store last generation's best individual unchanged
        self.population.sort(key=lambda x:x[-1][0],reverse = True)
        #roulette selection and elite storing
        #store the best 5% individual
        self.temp.sort(key=lambda x:x[-1][0],reverse = True)
        elite_number = int(self.population_size * 0.05)
        for i in range(1,elite_number+1):
            self.population[i] = self.temp[i]
        min_fit = self.temp[-1][-1][0]
        random.shuffle(self.temp)
        ark = 0 # the number used to roulette in crossing
        probability = 0
        for i in range(len(self.temp)):
            probability = probability + self.temp[i][-1][0] + (0.1 - min_fit)
        roulette = 0
        for i in range(elite_number+1,self.population_size):
            roulette = random.randint(0,int(probability))
            while roulette > 0:
                roulette = roulette - (self.temp[ark][-1][0] + 0.1 - min_fit)
                ark = (ark + 1) % len(self.temp)
            self.population[i] = self.temp[ark]

    def exchange_rule(self):
        for k in range(len(self.temp)):
            if OIL_PRICE_LIST[convert2to10_in_list(self.temp[k][0])] > OIL_PRICE_LIST[convert2to10_in_list(self.temp[k][1])]:
                self.temp[k][0],self.temp[k][1] = self.temp[k][1],self.temp[k][0]
            if FREIGHT_RATE_LIST[convert2to10_in_list(self.temp[k][2])] > FREIGHT_RATE_LIST[convert2to10_in_list(self.temp[k][3])]:
                self.temp[k][2],self.temp[k][3] = self.temp[k][3],self.temp[k][2]
            if EXCHANGE_RATE_LIST[convert2to10_in_list(self.temp[k][4])] > EXCHANGE_RATE_LIST[convert2to10_in_list(self.temp[k][5])]:
                self.temp[k][4],self.temp[k][5] = self.temp[k][5],self.temp[k][4]
            if OWN_SHIP_LIST[convert2to10_in_list(self.temp[k][6])] > OWN_SHIP_LIST[convert2to10_in_list(self.temp[k][7])]:
                self.temp[k][6],self.temp[k][7] = self.temp[k][7],self.temp[k][6]

    def store_best_and_average(self):
        self.population.sort(key=lambda x:x[-1][0],reverse = True)
        self.bestpopulation.append(self.population[0])
        random.shuffle(self.population)
        total = 0
        for e in range(self.population_size):
            total += self.population[e][-1][0]
        self.averagepopulation.append(total/self.population_size)

    def depict_fitness(self):
        x = range(0,len(self.bestpopulation))
        y = []
        z = []
        for i in range(len(self.bestpopulation)):
            y.append(self.bestpopulation[i][-1][0])
            z.append(self.averagepopulation[i])
        plt.plot(x, y, marker='o',label='best')
        plt.plot(x, z, marker='x',label='average')
        plt.title('Transition of fitness', fontsize = 20)
        plt.xlabel('generation', fontsize = 16)
        plt.ylabel('fitness value', fontsize = 16)
        plt.ylim(-2,2)
        plt.tick_params(labelsize=14)
        plt.grid(True)
        plt.legend(loc = 'lower right')
        save_dir = '../output/image'
        plt.savefig(os.path.join(save_dir, 'fitness.png'))
        plt.close()

    def depict_average_variance(self,gene=None,list=None):
        x = []
        y = []
        for i in range(self.population_size):
            if gene == 0:
                x.append(list[i][-1][0])
                y.append(list[i][-1][1])
            else:
                x.append(self.population[i][-1][0])
                y.append(self.population[i][-1][1])
        plt.scatter(x,y)
        x_min = min(x)
        x_min = x_min*0.9 if x_min>0 else x_min*1.1
        plt.xlim(-1,1)
        plt.ylim(0,2)
        plt.title("Rule Performance")
        plt.xlabel("Expectation")
        plt.ylabel("Variance")
        plt.grid(True)
        save_dir = '../output'
        if gene == 0:
            plt.savefig(os.path.join(save_dir, 'Evaluation_{}_initial.png'.format(name)))
        else:
            plt.savefig(os.path.join(save_dir, 'Evaluation_{}.png'.format(name)))
        plt.close()

    def check_convergence(self,target,criteria):
        flag = True
        for index in range(1,criteria+1):
            if target[-index][-1] != target[-(index+1)][-1]:
                flag = False
                break
        return flag

    def print_result(self):
        self.population.sort(key=lambda x:x[-1][0],reverse = True)
        for i in range(0,NUM_DISPLAY):
            if i == 0:
                print('best rule', self.population[i])
            thisone = self.population[i]
            a = OIL_PRICE_LIST[convert2to10_in_list(thisone[0])]
            b = OIL_PRICE_LIST[convert2to10_in_list(thisone[1])]
            c = FREIGHT_RATE_LIST[convert2to10_in_list(thisone[2])]
            d = FREIGHT_RATE_LIST[convert2to10_in_list(thisone[3])]
            e = EXCHANGE_RATE_LIST[convert2to10_in_list(thisone[4])]
            f = EXCHANGE_RATE_LIST[convert2to10_in_list(thisone[5])]
            speed = VESSEL_SPEED_LIST[self.actionlist[0]]
            purchase_new = PURCHASE_NUMBER[self.actionlist[1]]
            purchase_secondhand = PURCHASE_NUMBER[self.actionlist[2]]
            sell = SELL_NUMBER[self.actionlist[3]]
            charter_in = CHARTER_IN_NUMBER[self.actionlist[4]]
            charter_out = CHARTER_OUT_NUMBER[self.actionlist[5]]
            print('{0} <= oil price <= {1} and {2} <= freight <= {3} and {4} <= exchange <= {5}'.format(a,b,c,d,e,f))
            print('speed {}'.format(speed))
            print('purchase {} new ships'.format(purchase_new))
            print('purchase {} secondhand ships'.format(purchase_secondhand))
            print('sell {} ships'.format(sell))
            print('charter_in {}'.format(charter_in))
            print('charter_out {}'.format(charter_out))
            print('Expectation = {}'.format(thisone[-1][0]))
            print('Variance = {}'.format(thisone[-1][1]))
            if self.check_rule_is_adapted(thisone):
                print('ADPTED')
            if a > b or c > d or e > f:
                print('rule error')
                sys.exit()

    def execute_GA(self):
        first = time.time()

        #randomly generating individual group
        for i in range(self.population_size):
            self.population.append(self.generateIndividual())
        #self.depict_average_variance(0,self.population,self.actionlist)

        #genetic algorithm
        for gene in range(self.generation):
            #crossover
            self.temp = copy.deepcopy(self.population)
            random.shuffle(self.temp)
            for selected in range(0,self.population_size,2):
                if random.random() < self.crossover_rate:
                    a,b = self.crossover(self.temp[selected],self.temp[selected+1])
                else:
                    a,b = copy.deepcopy(self.temp[selected]),copy.deepcopy(self.temp[selected+1])
                self.temp.append(a)
                self.temp.append(b)

            #mutation
            for individual in self.temp:
                if random.random() < self.alpha:
                    individual = self.mutation(individual)

            #rule check
            self.exchange_rule()

            #computation of fitness
            for one in range(len(self.temp)):
                rule = self.temp[one]
                rule[-1][0], rule[-1][1] = self.fitness_function(rule)

            #selection
            self.selection()
            self.store_best_and_average()
            #if gene > 10 and self.check_convergence(self.bestpopulation,10):
            #    break

        #print('finish')
        #print('Spent time is {0}'.format(time.time() - first))
        self.depict_fitness()
        #self.depict_average_variance()
        #self.print_result()
        self.population.sort(key=lambda x:x[-1][0],reverse = True)
        return self.population[0]
