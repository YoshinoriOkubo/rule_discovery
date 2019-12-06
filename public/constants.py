#for condition parts
def make_condition_options():
    import csv
    conditions = []
    path = '../output/train/scenario/statistics.csv'
    data = []
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == 'freight_outward' or row[0] == 'exchange_rate':
                data.append([])
                data[-1].append(float(row[1]))
                if row[0] == 'oil_price':
                    data[-1].append(float(row[3])/2.0)#stdev
                else:
                    data[-1].append(float(row[3]))#stdev
    for condition_num in range(2):
        mean, stdev = data[condition_num]
        conditions.append([DO_NOT_CARE,mean-2*stdev,mean-stdev,mean-0.5*stdev,mean,mean+0.5*stdev,mean+stdev,mean+2*stdev])
        for index in range(1,2**DEFAULT_NUM_OF_BIT):
            if conditions[-1][index] < 0:
                conditions[-1][index] = 0
    return conditions
    
"Ship parameter"
TEU_SIZE = 7000#9300TEU
INITIAL_SPEED = 19#knot
ROUTE_DISTANCE = 23179*1.60934#km
ORDER_TIME = 24#month
AVERAGE_SHIP_SIZE = 3.555#(1000TEU) refered to data in end of 2014
#age distribution
WITHIN_FIVE = 550#number of vessel under 5 years
WITHIN_TEN = 1043#number of vessel between 5 and 10 years
WITHIN_FIF = 570#number of vessel between 10 and 15 years 

"Profit calculation parameter"
VESSEL_LIFE_TIME         = 15#year
PAYBACK_PERIOD = 15
DEFAULT_PREDICT_YEARS    = VESSEL_LIFE_TIME+PAYBACK_PERIOD + ORDER_TIME
DISCOUNT_RATE = 0.06
CHARTER_TIME = 12
RISK_PREMIUM = 0.95
INDIRECT_COST = 0.05
FINAL_VALUE = 3.0 * 1000000#USD
NON_FUELED_COST  = 18.418 * 1000000#USD/year
INITIAL_NUMBER_OF_SHIPS = 100
ORDER_CAPACITY=55#shipbuilding company's capacity to build ship per month
DEMAND_PER_SHIP_NUMBER = 0.02326057#demand per one vessel
SHIP_NUMBER_PER_DEMAND = 1.0/DEMAND_PER_SHIP_NUMBER
LOADING_DAYS = 12#days necessary for loading and unloading
OPTIMISM = 1.31#measure of investor's optimistic expectation for future
# load factor 60 % of ONE's real data in 2018 
LOAD_FACTOR_ASIA_TO_EUROPE = 0.528
LOAD_FACTOR_EUROPE_TO_ASIA = 0.33
TIME_STEP = 3#every time step, make decision

"GA parameter"
GENETIC_ALGORITHM_PARAMETER = {'scenario_pattern': 100, 'generation':1, 'population_size':100}
DEFAULT_PREDICT_PATTERN_NUMBER = GENETIC_ALGORITHM_PARAMETER['scenario_pattern']
DEFAULT_GENERATION = GENETIC_ALGORITHM_PARAMETER['generation']
DEFAULT_POPULATION_SIZE = GENETIC_ALGORITHM_PARAMETER['population_size']
DEFAULT_CROSSOVER_RATE = 0.80#crossover happens with this probability
DEFAULT_MUTATION_RATE = 0.05#mutation happend with this probability
TRAIN_DATA_SET = 'train'#the sign of train data with generated scenario
TEST_DATA_SET = 'test'#the sign of test data with generated scenario

"Chromosome paramater"
DEFAULT_NUM_OF_BIT = 3#number of bits in one block
DEFAULT_NUM_OF_CONDITION = 5#number rule condition types 
DEFAULT_NUM_OF_ACTION_INTEGRATE = 6#number rule condition types in integrated version
DEFAULT_NUM_OF_ACTION = 5#number of rule action types in independent version
DO_NOT_CARE = -1#if this appear in the condition, then it is always met
OIL_PRICE_LIST = [DO_NOT_CARE,20,40,60,80,100,120,140]
FREIGHT_RATE_LIST,EXCHANGE_RATE_LIST = make_condition_options()
OWN_SHIP_LIST = [DO_NOT_CARE,20,40,60,80,100,120,140]
CONVERT_LIST = [OIL_PRICE_LIST,FREIGHT_RATE_LIST,EXCHANGE_RATE_LIST,OWN_SHIP_LIST,FREIGHT_RATE_LIST]#the list for condition part
FREIGHT_PREV = [2000,1640,1210,1390,1580,1540,1570,1540,1280,1070,1140,1250]#for calculating average freight of past ten months
#for vessel speed optimaization
VESSEL_SPEED_LIST = [13,14,15,16,17,18,19,20,21,22,23,24,25,26]
#for action part
PURCHASE_NUMBER = [0,1,3,5]
SELL_NUMBER = [0,1,3,5]
CHARTER_IN_NUMBER = [0,1,3,5]
CHARTER_OUT_NUMBER = [0,1,3,5]
#for gray code
GRAY_CODE_2 = [0,1,3,2]
GRAY_CODE_3 = [0,1,3,2,6,7,5,4]
GRAY_CODE_4 = [0,1,3,2,6,7,5,4,12,13,15,14,10,11,9,8]


"Market Scenario parameter"
#regeression for generating scenario
#freight outward market
F_OUTWARD_INCLINATION_OIL = 5.744615088
F_OUTWARD_INCLINATION_DEMAND = 206070.8041/AVERAGE_SHIP_SIZE
F_OUTWARD_INTERCEPT = -525.578907
#freight homeward market
F_HOMEWARD_INCLINATION_OIL = 2.907961456
F_HOMEWARD_INCLINATION_DEMAND = 39921.43727/AVERAGE_SHIP_SIZE
F_HOMEWARD_INTERCEPT = 314.4678861
#newbuilding market
NEW_BUILDING_INCLINATION = 7733.416819/AVERAGE_SHIP_SIZE
NEW_BUILDING_INTERCEPT = 18.00650226
#secondhand market
SECONDHAND_INCLINATION = 20934.59554/AVERAGE_SHIP_SIZE
SECONDHAND_INTERCEPT = -87.74252608
#used when using binomial lattice model
DELTA_T_MONTH = 12
DELTA_T_DAY = 30
MAX_OIL_PRICE = 160#upper limit of oil price
MAX_EXCHANGE = 200#upper limit of exchange rate


"Others"
HUNDRED_MILLION = 1.0 * 10**8
SCALING = 10000
NUM_DISPLAY = 3
MONTH = 0
YEAR = 1
FIVE_YEARS_OLD = 60
DECISION_CHARTER_OUT = 0
DECISION_CHARTER_IN = 1
OUTWARD = 0
HOMEWARD = 1
CCFI = 2
OIL_TYPE = 100
FREIGHT_TYPE = 200
EXCHANGE_TYPE = 300
DEMAND_TYPE = 400
SUPPLY_TYPE = 500
NEWSHIPMARKET_TYPE =600
SECONDHAND_TYPE = 700