import random
import copy
import time
import sys
import matplotlib.pyplot as plt
import os
from multiprocessing import Pool
import multiprocessing as multi
from ship import Ship
from tqdm import tqdm
import slackweb
# import own modules #
sys.path.append('../public')
sys.path.append('../output')
from constants  import *
from my_modules import *

class GA_Trade:

    def __init__(self,oil_price_data,freight_rate_outward,freight_rate_homeward,exchange_rate,demand,supply,newbuilding,secondhand,actionlist=None,generation=None,population_size=None,crossover_rate=None,mutation_rate=None):
        self.oil_price_data = oil_price_data #oil price predicted data
        self.freight_rate_outward_data = freight_rate_outward #feright rate outward predicted data
        self.freight_rate_homeward_data = freight_rate_homeward # freight rate return predicted data
        self.exchange_rate_data = exchange_rate # exchange_rate predicted data
        self.demand_data = demand#ship demand predicted data
        self.supply_data = supply#ship supply predicted data
        self.newbuilding = newbuilding#new building ship price data
        self.secondhand = secondhand#secondhand ship price data
        self.actionlist = None if actionlist else None # decision of action parts.
        self.generation = generation if generation else DEFAULT_GENERATION # the number of generation
        self.population_size = population_size if population_size else DEFAULT_POPULATION_SIZE  # the number of individual
        self.mutation_rate = mutation_rate if mutation_rate else DEFAULT_MUTATION_RATE # the rate of mutation
        self.crossover_rate = crossover_rate if crossover_rate else DEFAULT_CROSSOVER_RATE
        self.population = [] # population that has individual
        self.temp = [] #temporary group that has individuals
        self.bestpopulation = [] # group that has the best individuals in each generation
        self.averagepopulation = [] # the average value of fitness in each generation
        self.number_of_train_data = DEFAULT_PREDICT_PATTERN_NUMBER

    def adapt_rule(self,oil_price,freight,exchange,own_ship,freight_data,time,rule_integrate):
        result = [[False,0],[False,0],[False,0],[False,0],[False,0]]
        average_freight = 0
        for data_index in range(10):
            if time - data_index < 0:
                average_freight += FREIGHT_PREV[time - data_index]
            else:
                average_freight += freight_data[time - data_index]['price']
        average_freight /= 10
        compare_list = [oil_price,freight,exchange,own_ship,average_freight]
        for which_action in range(DEFAULT_NUM_OF_ACTION_INTEGRATE):
            rule = rule_integrate[which_action]
            flag = True
            for cond in range(DEFAULT_NUM_OF_CONDITION):
                condition_type = CONVERT_LIST[cond]
                lower = condition_type[convert2to10_in_list(rule[cond*2])]
                upper = condition_type[convert2to10_in_list(rule[cond*2+1])]
                if (lower < compare_list[cond] or lower == DO_NOT_CARE) and (compare_list[cond] < upper or upper == DO_NOT_CARE):
                    pass
                else:
                    flag = False
            if flag == True:
                if DEFAULT_NUM_OF_ACTION_INTEGRATE == 6:
                    result[int(which_action/2)][0] = True
                    result[int(which_action/2)][1] += (which_action % 2) + 1
                elif DEFAULT_NUM_OF_ACTION_INTEGRATE == 3:
                    result[which_action][0] = True
                    result[which_action][1] = + 1
        return result
    
    def generateIndividual_with_wise(self):
        population = []
        always = [[0,0,0],[0,0,0]]
        if_low = [[0,0,0],[0,1,1]]
        if_high = [[1,0,0],[0,0,0]]
        no = [[1,1,1],[1,1,1]]
        candidate = [always,if_low,if_high,no]
        for new in candidate:
            for second in candidate:
                for sell in candidate:
                    rule = []
                    strategylist = []
                    if DEFAULT_NUM_OF_ACTION_INTEGRATE == 6:
                        strategylist = [new,new,second,second,sell,sell]
                    elif DEFAULT_NUM_OF_ACTION_INTEGRATE == 3:
                        strategylist = [new,second,sell]
                    for strategy in strategylist:
                        rule.append([])
                        for number_of_condition in range(DEFAULT_NUM_OF_CONDITION):
                            if number_of_condition == 1:
                                rule[-1].append(copy.deepcopy(strategy[0]))
                                rule[-1].append(copy.deepcopy(strategy[1]))
                            else:
                                rule[-1].append(copy.deepcopy(always[0]))
                                rule[-1].append(copy.deepcopy(always[1]))
                    rule.append([0,0])
                    rule[-1][0],rule[-1][1] = self.fitness_function(rule)
                    population.append(rule)
        for num in range(self.population_size-len(candidate)**3):
            rule_random = []
            for trade in range(DEFAULT_NUM_OF_ACTION_INTEGRATE):
                rule_random.append([])
                for condition in range(DEFAULT_NUM_OF_CONDITION*2):
                    rule_random[trade].append([])
                    for bit in range(DEFAULT_NUM_OF_BIT):
                        rule_random[trade][condition].append(random.randint(0,1))
            rule_random.append([0,0])
            rule_random[-1][0],rule_random[-1][1] = self.fitness_function(rule_random)
            population.append(rule_random)
        return population

    def crossover(self,a,b):
        temp1 = []
        temp2 = []
        which_action = random.randint(0,DEFAULT_NUM_OF_ACTION_INTEGRATE-1)
        proportion = [1,3,1,1,3]
        rand = random.randint(0,sum(proportion)-1)
        crossover_block = 0
        for tryal in range(4):
            if rand < proportion[crossover_block]:
                pass
            else:
                rand -= proportion[crossover_block]
                crossover_block += 1
        crossover_block = crossover_block*2 + random.randint(0,1)
        #crossover_block = random.randint(0,DEFAULT_NUM_OF_CONDITION*2-1)
        for index in range(DEFAULT_NUM_OF_ACTION_INTEGRATE):
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
            else:
                temp1.append(a[index])
                temp2.append(b[index])
        temp1.append([0,0])
        temp2.append([0,0])
        return [temp1,temp2]

    def mutation(self,individual):
        which_action = random.randint(0,DEFAULT_NUM_OF_ACTION_INTEGRATE-1)
        proportion = [1,3,1,1,3]
        rand = random.randint(0,sum(proportion)-1)
        mutation_block = 0
        for tryal in range(4):
            if rand < proportion[mutation_block]:
                pass
            else:
                rand -= proportion[mutation_block]
                mutation_block += 1
        mutation_block = mutation_block*2 + random.randint(0,1)
        #mutation_block = random.randint(0,DEFAULT_NUM_OF_CONDITION*2-1)
        length = len(individual[which_action][mutation_block]) - 1
        point = random.randint(0,length)
        if individual[which_action][mutation_block][point] == 0:
            individual[which_action][mutation_block][point] = 1
        else:
            individual[which_action][mutation_block][point] = 0
        return individual

    def fitness_function(self,rule):
        Record = []
        for pattern in range(self.number_of_train_data):
            fitness = 0
            ship = Ship(TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE)
            for year in range(DEFAULT_PREDICT_YEARS):
                cash_flow = 0
                if year >= PAYBACK_PERIOD and ship.exist_number <= 0:
                    break
                for month in range(0,12,TIME_STEP):
                    current_oil_price = self.oil_price_data[pattern][year*12+month]['price']
                    current_freight_rate_outward = self.freight_rate_outward_data[pattern][year*12+month]['price']
                    current_freight_rate_homeward = self.freight_rate_homeward_data[pattern][year*12+month]['price']
                    total_freight = ( current_freight_rate_outward * LOAD_FACTOR_ASIA_TO_EUROPE + current_freight_rate_homeward * LOAD_FACTOR_EUROPE_TO_ASIA)
                    current_exchange = self.exchange_rate_data[pattern][year*12+month]['price']
                    current_demand = self.demand_data[pattern][year*12+month]['price']
                    current_supply = self.supply_data[pattern][year*12+month]['price']
                    if year < PAYBACK_PERIOD:
                        current_newbuilding = self.newbuilding[pattern][year*12+month]['price']
                        current_secondhand = self.secondhand[pattern][year*12+month]['price']
                        result = self.adapt_rule(current_oil_price,current_freight_rate_outward,current_exchange,ship.total_number+ship.order_number,self.freight_rate_outward_data[pattern],year*12+month,rule)
                        if result[0][0]:
                            cash_flow += ship.buy_new_ship(current_newbuilding,result[0][1])
                        if result[1][0]:
                            cash_flow += ship.buy_secondhand_ship(current_secondhand,result[1][1])
                        if result[2][0]:
                            cash_flow += ship.sell_ship(current_secondhand,result[2][1])
                        if result[3][0]:
                            ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[3][1],DECISION_CHARTER_IN)
                        if result[4][0]:
                            ship.charter_ship(current_oil_price,total_freight,current_demand,current_supply,result[4][1],DECISION_CHARTER_OUT)
                    if ship.charter_flag == True:
                        cash_flow += ship.charter()
                        ship.end_charter()
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

    def process(self,rule):
        return self.fitness_function(rule)

    def wrapper_process(self,args):
        return self.process(*args)

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
            for condition_block in range(DEFAULT_NUM_OF_ACTION_INTEGRATE):
                condition = self.temp[individual_index][condition_block]
                if OIL_PRICE_LIST[convert2to10_in_list(condition[0])] > OIL_PRICE_LIST[convert2to10_in_list(condition[1])]:
                    condition[0],condition[1] = condition[1],condition[0]
                if FREIGHT_RATE_LIST[convert2to10_in_list(condition[2])] > FREIGHT_RATE_LIST[convert2to10_in_list(condition[3])]:
                    condition[2],condition[3] = condition[3],condition[2]
                if EXCHANGE_RATE_LIST[convert2to10_in_list(condition[4])] > EXCHANGE_RATE_LIST[convert2to10_in_list(condition[5])]:
                    condition[4],condition[5] = condition[5],condition[4]
                if OWN_SHIP_LIST[convert2to10_in_list(condition[6])] > OWN_SHIP_LIST[convert2to10_in_list(condition[7])]:
                    condition[6],condition[7] = condition[7],condition[6]
                if FREIGHT_RATE_LIST[convert2to10_in_list(condition[8])] > FREIGHT_RATE_LIST[convert2to10_in_list(condition[9])]:
                    condition[8],condition[9] = condition[9],condition[8]

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
        save_dir = '../output/train/image'
        plt.savefig(os.path.join(save_dir, 'integrate_fitness.png'))
        plt.close()

    def depict_average_variance(self,gene=None):
        x = []
        y = []
        for i in range(self.population_size):          
            x.append(self.population[i][-1][0])
            y.append(self.population[i][-1][1])
        plt.scatter(x,y)
        x_min = min(x)
        x_min = x_min*0.9 if x_min>0 else x_min*1.1
        plt.xlim(-1,2)
        plt.ylim(0,1)
        plt.title("Rule Performance")
        plt.xlabel("Expectation")
        plt.ylabel("Variance")
        plt.grid(True)
        save_dir = '../output/train/image'
        if gene is not None:
            plt.savefig(os.path.join(save_dir, 'Evaluation_initial.png'))
        else:
            plt.savefig(os.path.join(save_dir, 'Evaluation.png'))
        plt.close()

    def check_convergence(self,target,criteria):
        flag = True
        for index in range(1,criteria+1):
            if target[-index][-1] != target[-(index+1)][-1]:
                flag = False
                break
        return flag

    def execute_GA(self):

        #randomly generating individual group
        #for p_size in range(self.population_size):
        #    self.population.append(self.generateIndividual())
        self.population = self.generateIndividual_with_wise()
        self.depict_average_variance(0)

        #genetic algorithm
        for gene in tqdm(range(self.generation)):
            time.sleep(1/self.generation)
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
            for individual_mutaion in self.temp[self.population_size:]:
                if random.random() < self.mutation_rate:
                    individual_mutaion = self.mutation(individual_mutaion)
            
            #rule check
            self.exchange_rule()

            num_pool = multi.cpu_count()
            num_pool = 1#int(num_pool*0.9)
            with Pool(num_pool) as pool:
                p = pool.map(self.process, self.temp[self.population_size:])
                for index in range(self.population_size):
                    rule = self.temp[index+self.population_size]
                    rule[-1][0], rule[-1][1] = p[index]

            #selection
            self.selection(gene)

            self.store_best_and_average()
            #if gene > 1000 and self.check_convergence(self.bestpopulation,200):
            #    break

        self.depict_fitness()
        self.depict_average_variance()
        self.population.sort(key=lambda x:x[-1][0],reverse = True)
        return self.population


def main():
    oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data = load_generated_sinario()
    ga = GA_Trade(oil_data,freight_outward_data,freight_return_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data)
    start = time.time()
    p = ga.execute_GA()
    print(time.time()-start)
    export_rules_integrate_csv(p)

if __name__ == "__main__":
    main()
    slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
    #slack.notify(text="program end!!!!!!!!!")
