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

def make_minimum_actionlist():
    all_actionlist = []
    all_actionlist.append([1,0,0,0,0])
    all_actionlist.append([0,1,0,0,0])
    all_actionlist.append([0,0,1,0,0])
    all_actionlist.append([0,0,0,1,0])
    all_actionlist.append([0,0,0,0,1])
    return [all_actionlist,5]

def make_small_actionlist():
    all_actionlist = []
    for purchase_new in range(2):
        for purchase_secondhand in range(2):
            for sell in range(2):
                for charter_in in range(2):
                    for charter_out in range(2):
                        all_actionlist.append([purchase_new,purchase_secondhand,sell,charter_in,charter_out])
    return [all_actionlist,2**5]

def make_actionlist():
    all_actionlist = []
    for purchase_new in range(4):
        for purchase_secondhand in range(4):
            for sell in range(4):
                for charter_in in range(4):
                    for charter_out in range(4):
                        all_actionlist.append([purchase_new,purchase_secondhand,sell,charter_in,charter_out])
    return [all_actionlist,4**5]

def process(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,actionlist):
    ga = GA(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,
                    actionlist)
    return ga.execute_GA()

def wrapper_process(args):
    return process(*args)

def single_processing():
    all_actionlist = make_actionlist()
    oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data = load_generated_sinario()
    rule = []
    for action_number in range(len(all_actionlist)):
        rule.append(process(oil_data,freight_outward_data,freight_homeward_data,exchange_data,all_actionlist[action_number]))
    export_rules_csv(rule)

def multi_processing():
    all_actionlist,number = make_minimum_actionlist()
    #all_actionlist,number = make_small_actionlist()
    #all_actionlist,number = make_actionlist()
    oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data = load_generated_sinario()
    num_pool = multi.cpu_count()
    num_pool = int(num_pool*0.9)
    tutumimono = [[oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,all_actionlist[i]] for i in range(number)]
    with Pool(num_pool) as pool:
        p = pool.map(wrapper_process, tutumimono)
        export_rules_csv(p)
    send_messege()

def one_rule_example(actionlist):
    oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data = load_generated_sinario()
    ga = GA(oil_data,freight_outward_data,freight_homeward_data,exchange_data,demand_data,supply_data,newbuilding_data,secondhand_data,
                    actionlist)
    p = []
    p.append(ga.execute_GA())
    print(p)
    export_rules_csv(p,1)

def send_messege():
    slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
    slack.notify(text="program end!!!!!!!!!")

def main():
    start = time.time()
    #single_processing()
    multi_processing()
    #one_rule_example([1,0,0,0,0])
    print(time.time()-start)

if __name__ == "__main__":
    main()
