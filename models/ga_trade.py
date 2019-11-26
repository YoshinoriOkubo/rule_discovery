import random
import copy
import time
import sys
import matplotlib.pyplot as plt
import os
from multiprocessing import Pool
import multiprocessing as multi
from ship import Ship
# import own modules #
sys.path.append('../public')
sys.path.append('../output')
from constants  import *
from my_modules import *

class GA_Trade:

    def __init__(self,oil_price_data,freight_rate_outward,freight_rate_return,exchange_rate,demand,supply,actionlist=None,generation=None,population_size=None,alpha=None,crossover_rate=None):
        self.oil_price_data = oil_price_data #oil price predicted data
        self.freight_rate_outward_data = freight_rate_outward #feright rate outward predicted data
        self.freight_rate_return_data = freight_rate_return # freight rate return predicted data
        self.exchange_rate_data = exchange_rate # exchange_rate predicted data
        self.demand_data = demand#ship demand predicted data
        self.supply_data = supply#ship supply predicted data
        self.actionlist = None if actionlist else None # decision of action parts.
        self.generation = generation if generation else DEFAULT_GENERATION # the number of generation
        self.population_size = population_size if population_size else DEFAULT_POPULATION_SIZE  # the number of individual
        self.alpha = alpha if alpha else DEFAULT_ALPHA # the rate of mutation
        self.crossover_rate = crossover_rate if crossover_rate else DEFAULT_CROSSOVER_RATE
        self.population = [] # population that has individual
        self.temp = [] #temporary group that has individuals
        self.bestpopulation = [] # group that has the best individuals in each generation
        self.averagepopulation = [] # the average value of fitness in each generation

    def adapt_rule(self,oil_price,freight,exchange,own_ship,rule_two):
        result = [[False,0],[False,0]]
        for which_action in range(2):
            rule = rule_two[which_action]
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
                            result[which_action][0] = True
                            result[which_action][1] = 1
                            #result[1].append(PURCHASE_NUMBER[self.actionlist[0]])
                            #result[1].append(PURCHASE_NUMBER[self.actionlist[1]])
                            #result[1].append(SELL_NUMBER[self.actionlist[2]])
                            #result[1].append(CHARTER_IN_NUMBER[self.actionlist[3]])
                            #result[1].append(CHARTER_OUT_NUMBER[self.actionlist[4]])
        return result

    def check_rule_is_adapted(self,rule):
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            for year in range(DEFAULT_PREDICT_YEARS):
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
        actionlist =[[1,0],[0,1]]
        for trade in range(2):
            temp.append([])
            for condition in range(DEFAULT_NUM_OF_CONDITION*2):
                temp[trade].append([])
                for a in range(DEFAULT_NUM_OF_BIT):
                    temp[trade][condition].append(random.randint(0,1))
            for action in range(2):
                temp[trade].append(actionlist[trade][action])
        temp.append([0,0])
        return temp

    def crossover(self,a,b):
        temp1 = []
        temp2 = []
        which_action = random.randint(0,1)
        crossover_block = random.randint(0,DEFAULT_NUM_OF_CONDITION*2-1)
        for index in range(2):
            if index == which_action:
                temp1.append([])
                temp2.append([])
                for condition in range(DEFAULT_NUM_OF_CONDITION*2):
                    if condition == crossover_block:
                        temp1[index].append([])
                        temp2[index].append([])
                        length = len(a[index][condition]) - 1
                        crossover_point = random.randint(1,length-1)
                        for former in range(0,crossover_point):
                            temp1[index][condition].append(a[index][condition][former])
                            temp2[index][condition].append(b[index][condition][former])
                        for latter in range(crossover_point,len(a[index][condition])):
                            temp1[index][condition].append(b[index][condition][latter])
                            temp2[index][condition].append(a[index][condition][latter])
                    else:
                        temp1[index].append(a[index][condition])
                        temp2[index].append(b[index][condition])
                for action in range(2):
                    temp1[index].append(a[index][action+DEFAULT_NUM_OF_CONDITION*2])
                    temp2[index].append(b[index][action+DEFAULT_NUM_OF_CONDITION*2])
            else:
                temp1.append(a[index])
                temp2.append(b[index])
        temp1.append([0,0])
        temp2.append([0,0])
        return [temp1,temp2]

    def mutation(self,individual):
        which_action = random.randint(0,1)
        mutation_block = random.randint(0,DEFAULT_NUM_OF_CONDITION*2-1)
        length = len(individual[which_action][mutation_block]) - 1
        point = random.randint(0,length)
        individual[which_action][mutation_block][point] = (individual[which_action][mutation_block][point] + 1) % 2
        return individual

    def fitness_function(self,rule):
        Record = []
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            fitness = 0
            ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
            '''
            for i in range(len(ship.agelist)):
                if ship.agelist[i] == 0:
                    fitness -= INITIAL_COST_OF_SHIPBUIDING*0.5*(1+ship.freight_impact(self.freight_rate_outward_data,0))*(1 + INDIRECT_COST)
                else:
                    fitness -= INITIAL_COST_OF_SHIPBUIDING*ship.age_impact(ship.agelist[i])*ship.freight_impact(self.freight_rate_outward_data,0)*(1 + INDIRECT_COST)
            fitness *= self.exchange_rate_data[pattern][11]['price']
            '''
            for year in range(DEFAULT_PREDICT_YEARS):
                cash_flow = 0
                for month in range(12):
                    current_oil_price = self.oil_price_data[pattern][year*12+month]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][year*12+month]['price']
                    current_freight_rate_return = self.freight_rate_return_data[pattern][year*12+month]['price']
                    total_freight = ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_return * LOAD_FACTOR_EUROPE_TO_ASIA)
                    current_exchange = self.exchange_rate_data[pattern][year*12+month]['price']
                    current_demand = self.demand_data[pattern][year*12+month]['price']
                    current_supply = self.supply_data[pattern][year*12+month]['price']
                    result = self.adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,rule)
                    if result[0]:
                        cash_flow += ship.buy_secondhand_ship_from_demand_and_supply(current_demand,current_supply,result[0][1])
                    if result[1]:
                        cash_flow += ship.sell_ship_from_demand_and_supply(current_demand,current_supply,result[1][1])
                    #if result[0] and year < PAYBACK_PERIOD:
                        #cash_flow += ship.buy_new_ship(self.freight_rate_outward_data[pattern],year*12+month,result[1][0])
                        #cash_flow += ship.buy_secondhand_ship(self.freight_rate_outward_data[pattern],year*12+month,result[1][1])
                        #cash_flow += ship.sell_ship(self.freight_rate_outward_data[pattern],year*12+month,result[1][2])
                        #ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][3],DECISION_CHARTER_IN)
                        #ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[1][4],DECISION_CHARTER_OUT)
                    #if ship.charter_flag == True:
                        #cash_flow += ship.charter()
                        #ship.end_charter()
                    cash_flow += ship.calculate_income_per_month(current_oil_price,total_freight,current_demand,current_supply)
                    cash_flow += ship.add_age()
                DISCOUNT = (1 + DISCOUNT_RATE) ** (year + 1)
                cash_flow *= self.exchange_rate_data[pattern][year*12+11]['price']
                fitness += cash_flow / DISCOUNT
            fitness /= HUNDRED_MILLION
            fitness /= SCALING
            Record.append(fitness)
        e, sigma = calc_statistics(Record)
        return [e,sigma]

    def selection(self,generation):
        #store last generation's best individual unchanged
        self.population.sort(key=lambda x:x[-1][0],reverse = True)
        #roulette selection and elite storing
        #store the best 5% individual
        self.temp.sort(key=lambda x:x[-1][0],reverse = True)
        elite_number = int(self.population_size * 0.05)
        start = 1 if generation != 0 else 0
        for ith_individual in range(start,elite_number+1):
            self.population[ith_individual] = self.temp[ith_individual]
        min_fit = self.temp[-1][-1][0]
        random.shuffle(self.temp)
        ark = 0 # the number used to roulette in crossing
        probability = 0
        for jth_individual in range(len(self.temp)):
            probability = probability + self.temp[jth_individual][-1][0] + (0.1 - min_fit)#Translation
        roulette = 0
        for kth_individual in range(elite_number+1,self.population_size):
            roulette = random.randint(0,int(probability))
            while roulette > 0:
                roulette = roulette - (self.temp[ark][-1][0] + 0.1 - min_fit)
                ark = (ark + 1) % len(self.temp)
            self.population[kth_individual] = self.temp[ark]

    def exchange_rule(self):
        for individual_index in range(len(self.temp)):
            for condition_block in range(2):
                condition = self.temp[individual_index][condition_block]
                if OIL_PRICE_LIST[convert2to10_in_list(condition[0])] > OIL_PRICE_LIST[convert2to10_in_list(condition[1])]:
                    condition[0],condition[1] = condition[1],condition[0]
                if FREIGHT_RATE_LIST[convert2to10_in_list(condition[2])] > FREIGHT_RATE_LIST[convert2to10_in_list(condition[3])]:
                    condition[2],condition[3] = condition[3],condition[2]
                if EXCHANGE_RATE_LIST[convert2to10_in_list(condition[4])] > EXCHANGE_RATE_LIST[convert2to10_in_list(condition[5])]:
                    condition[4],condition[5] = condition[5],condition[4]
                if OWN_SHIP_LIST[convert2to10_in_list(condition[6])] > OWN_SHIP_LIST[convert2to10_in_list(condition[7])]:
                    condition[6],condition[7] = condition[7],condition[6]

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
        #plt.ylim(-2,2)
        plt.tick_params(labelsize=14)
        plt.grid(True)
        plt.legend(loc = 'lower right')
        save_dir = '../output/image'
        plt.savefig(os.path.join(save_dir, 'integrate_fitness.png'))
        plt.close()

    def depict_average_variance(self,actionlist,gene=None,list=None):
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
        plt.xlim(-1,5)
        plt.ylim(0,2)
        plt.title("Rule Performance")
        plt.xlabel("Expectation")
        plt.ylabel("Variance")
        plt.grid(True)
        save_dir = '../output/image'
        name = str(actionlist[0]*16+actionlist[1]*8+actionlist[2]*4+actionlist[3]*2+actionlist[4])
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
            purchase_new = PURCHASE_NUMBER[self.actionlist[0]]
            purchase_secondhand = PURCHASE_NUMBER[self.actionlist[1]]
            sell = SELL_NUMBER[self.actionlist[2]]
            charter_in = CHARTER_IN_NUMBER[self.actionlist[3]]
            charter_out = CHARTER_OUT_NUMBER[self.actionlist[4]]
            print('{0} <= oil price <= {1} and {2} <= freight <= {3} and {4} <= exchange <= {5}'.format(a,b,c,d,e,f))
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

    def process(self,rule):
        return self.fitness_function(rule)


    def wrapper_process(self,args):
        return self.process(*args)

    def execute_GA(self):
        first = time.time()

        #randomly generating individual group
        for p_size in range(self.population_size):
            self.population.append(self.generateIndividual())
        #self.depict_average_variance(self.actionlist,0,self.population)

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
            for individual_mutaion in self.temp:
                if random.random() < self.alpha:
                    individual_mutaion = self.mutation(individual_mutaion)

            #rule check
            self.exchange_rule()

            num_pool = multi.cpu_count()
            num_pool = int(num_pool*0.9)
            with Pool(num_pool) as pool:
                p = pool.map(self.process, self.temp)
                for index in range(len(self.temp)):
                    rule = self.temp[index]
                    rule[-1][0], rule[-1][1] = p[index]

            '''
            #computation of fitness
            for rule_index in range(len(self.temp)):
                rule_selected = self.temp[rule_index]
                rule_selected[-1][0], rule_selected[-1][1] = self.fitness_function(rule_selected)
            '''

            #selection
            self.selection(gene)
            for rule in self.population:
                for i in range(2):
                    thisone = rule[i]
                    a = OIL_PRICE_LIST[convert2to10_in_list(thisone[0])]
                    b = OIL_PRICE_LIST[convert2to10_in_list(thisone[1])]
                    c = FREIGHT_RATE_LIST[convert2to10_in_list(thisone[2])]
                    d = FREIGHT_RATE_LIST[convert2to10_in_list(thisone[3])]
                    e = EXCHANGE_RATE_LIST[convert2to10_in_list(thisone[4])]
                    f = EXCHANGE_RATE_LIST[convert2to10_in_list(thisone[5])]
                    g = OWN_SHIP_LIST[convert2to10_in_list(thisone[6])]
                    h = OWN_SHIP_LIST[convert2to10_in_list(thisone[7])]
                    if a > b or c > d or e > f or g > h:
                        print('rule error')
                        sys.exit()
            self.store_best_and_average()
            #if gene > 10 and self.check_convergence(self.bestpopulation,10):
            #    break

        #print('finish')
        #print('Spent time is {0}'.format(time.time() - first))
        self.depict_fitness()
        #self.depict_average_variance(self.actionlist)
        #self.print_result()
        self.population.sort(key=lambda x:x[-1][0],reverse = True)
        return self.population


def main():
    oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data = load_generated_sinario()
    rule = []
    ga = GA_Trade(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,)
    p = ga.execute_GA()
    export_rules_integrate_csv(p)

if __name__ == "__main__":
    start = time.time()
    main()
    print(time.time()-start)
