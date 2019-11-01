import subprocess
import time
import sys
from multiprocessing import Pool
import multiprocessing as multi
# import own modules #
sys.path.append('../public')
from my_modules import *
sys.path.append('../models')
from ga import GA

'''
start = time.time()
number = 0
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
'''
'''
def process(oil_data,freight_outward_data,freight_return_data,exchange_data,actionlist,action_number):
    ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
                    TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
                    actionlist,action_number)
    return ga.execute_GA()

def wrapper_process(args):
    return process(*args)

def main():
    start = time.time()
    all_actionlist = []
    for speed in range(4):
        for purchase in range(4):
            for sell in range(4):
                for charter_in in range(4):
                    for charter_out in range(4):
                        all_actionlist.append([speed,purchase,sell,charter_in,charter_out])
    generated_sinario = load_generated_sinario()
    oil_data = generated_sinario[0]
    freight_outward_data = generated_sinario[1]
    freight_return_data = generated_sinario[2]
    exchange_data = generated_sinario[3]
    num_pool = multi.cpu_count()
    tutumimono = [[oil_data,freight_outward_data,freight_return_data,exchange_data,all_actionlist[i],i+1] for i in range(100)]
    with Pool(num_pool) as pool:
        p = pool.map(wrapper_process, tutumimono)
        export_population(p)
    print(time.time()-start)
if __name__ == "__main__":
    main()
'''
generated_sinario = load_generated_sinario()
oil_data = generated_sinario[0]
freight_outward_data = generated_sinario[1]
freight_return_data = generated_sinario[2]
exchange_data = generated_sinario[3]
ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
                TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
                [2,2,1,1,1],0)
print(ga.execute_GA())
