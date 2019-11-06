import subprocess
import time
import sys
from multiprocessing import Pool
import multiprocessing as multi
import matplotlib
matplotlib.use('Agg')
# import own modules #
sys.path.append('../public')
from my_modules import *
sys.path.append('../models')
from ga import GA

def single_processing():#single processing
    start = time.time()
    number = 0
    population_list = []
    for speed in range(4):
        for purchase in range(4):
            for sell in range(4):
                for charter_in in range(4):
                    for charter_out in range(4):
                        number += 1
                        print('pattern {} integrate will start'.format(number))
                        cmd = "python3 ga.py {0} {1} {2} {3} {4} {5}".format(speed,purchase,sell,charter_in,charter_out,number)
                        subprocess.call(cmd.split(),cwd = "../models")
    print(time.time()-start)

def multi_processing():
    start = time.time()
    all_actionlist = []
    for speed in range(4):
        for purchase_new in range(4):
            for purchase_secondhand in range(4):
                for sell in range(4):
                    for charter_in in range(4):
                        for charter_out in range(4):
                            all_actionlist.append([speed,purchase_new,purchase_secondhand,sell,charter_in,charter_out])
    generated_sinario = load_generated_sinario()
    oil_data = generated_sinario[0]
    freight_outward_data = generated_sinario[1]
    freight_return_data = generated_sinario[2]
    exchange_data = generated_sinario[3]
    num_pool = multi.cpu_count()
    tutumimono = [[oil_data,freight_outward_data,freight_return_data,exchange_data,all_actionlist[i],i+1] for i in range(4)]
    with Pool(num_pool) as pool:
        p = pool.map(wrapper_process, tutumimono)
        export_rules_csv(p)
    print(time.time()-start)

def process(oil_data,freight_outward_data,freight_return_data,exchange_data,actionlist,action_number):
    ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
                    TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
                    actionlist,action_number)
    return ga.execute_GA()

def wrapper_process(args):
    return process(*args)

def one_rule_example():
    print(multi.cpu_count())
    start = time.time()
    generated_sinario = load_generated_sinario()
    oil_data = generated_sinario[0]
    freight_outward_data = generated_sinario[1]
    freight_return_data = generated_sinario[2]
    exchange_data = generated_sinario[3]
    ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
                    TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
                    [2,2,1,1,1,1],0)
    p = []
    p.append(ga.execute_GA())
    export_rules_csv(p)
    print(p)
    print(time.time()-start)

def main():
    multi_processing()
    #one_rule_example()

if __name__ == "__main__":
    main()#multiprocessing
