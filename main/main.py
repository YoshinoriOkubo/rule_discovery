import time
import sys
from multiprocessing import Pool
import multiprocessing as multi
import matplotlib
import slackweb
matplotlib.use('Agg')
# import own modules #
sys.path.append('../public')
from my_modules import *
sys.path.append('../models')
from ga import GA

def make_actionlist():
    all_actionlist = []
    for speed in range(4):
        for purchase_new in range(4):
            for purchase_secondhand in range(4):
                for sell in range(4):
                    for charter_in in range(4):
                        for charter_out in range(4):
                            all_actionlist.append([speed,purchase_new,purchase_secondhand,sell,charter_in,charter_out])
    return all_actionlist

def process(oil_data,freight_outward_data,freight_return_data,exchange_data,actionlist):
    ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
                    TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
                    actionlist)
    return ga.execute_GA()

def wrapper_process(args):
    return process(*args)

def single_processing():
    all_actionlist = make_actionlist()
    oil_data,freight_outward_data,freight_return_data,exchange_data = load_generated_sinario()
    rule = []
    for action_number in range(len(all_actionlist)):
        rule.append(process(oil_data,freight_outward_data,freight_return_data,exchange_data,all_actionlist[action_number]))
    export_rules_csv(rule)

def multi_processing():
    all_actionlist = make_actionlist()
    oil_data,freight_outward_data,freight_return_data,exchange_data = load_generated_sinario()
    num_pool = multi.cpu_count()
    tutumimono = [[oil_data,freight_outward_data,freight_return_data,exchange_data,all_actionlist[i]] for i in range(4)]
    with Pool(num_pool) as pool:
        p = pool.map(wrapper_process, tutumimono)
        export_rules_csv(p)

def one_rule_example(actionlist):
    oil_data,freight_outward_data,freight_return_data,exchange_data = load_generated_sinario()
    ga = GA(oil_data,freight_outward_data,freight_return_data,exchange_data,
                    TEU_SIZE,INITIAL_SPEED,ROUTE_DISTANCE,
                    actionlist)
    p = []
    p.append(ga.execute_GA())
    print(p)

def send_messege():
    slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
    slack.notify(text="program end!!!!!!!!!")

def main():
    start = time.time()
    #single_processing()
    #multi_processing()
    one_rule_example([0,0,1,3,1,2])
    print(time.time()-start)

if __name__ == "__main__":
    main()
