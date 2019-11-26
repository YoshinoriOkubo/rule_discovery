"Ship parameter"
TEU_SIZE = 7000#9300#TEU
INITIAL_SPEED = 19#knot
ROUTE_DISTANCE = 23179*1.60934#km
#INITIAL_COST_OF_SHIPBUIDING = 99.9 * 1000000#$ refer = https://link.springer.com/content/pdf/10.1007%2Fs00773-014-0262-5.pdf
FINAL_VALUE = 3.0 * 1000000
NON_FUELED_COST  = 18.418 * 1000000 # $/year
ORDER_TIME = 24
WITHIN_FIVE = 550
WITHIN_TEN = 1043
WITHIN_FIF = 570

"Profit calculation parameter"
VESSEL_LIFE_TIME         = 15#year
PAYBACK_PERIOD = 15
DEFAULT_PREDICT_YEARS    = VESSEL_LIFE_TIME+PAYBACK_PERIOD + ORDER_TIME
DISCOUNT_RATE = 0.06
CHARTER_TIME = 12
RISK_PREMIUM = 0.95
INDIRECT_COST = 0.05
LOAD_FACTOR_ASIA_TO_EUROPE = 0.44
LOAD_FACTOR_EUROPE_TO_ASIA = 0.31
INITIAL_NUMBER_OF_SHIPS = 100
ORDER_CAPACITY=55
SHIP_NUMBER_PER_DEMAND = 1.0/0.002396766#1/0.002016513
LOADING_DAYS = 12
FIVE_YEARS_OLD = 60

"GA parameter"
GENETIC_ALGORITHM_PARAMETER = {'scenario_pattern': 1, 'generation':1, 'population_size':100}
DEFAULT_PREDICT_PATTERN_NUMBER = GENETIC_ALGORITHM_PARAMETER['scenario_pattern']
DEFAULT_GENERATION = GENETIC_ALGORITHM_PARAMETER['generation']
DEFAULT_POPULATION_SIZE = GENETIC_ALGORITHM_PARAMETER['population_size']
DEFAULT_CROSSOVER_RATE = 0.80
DEFAULT_ALPHA = 0.05


"Chromosome paramater"
DEFAULT_NUM_OF_BIT = 3
DEFAULT_NUM_OF_CONDITION = 4
DEFAULT_NUM_OF_ACTION = 5
DEFAULT_NUM_OF_ACTION_INTEGRATE = 3
#for condition parts
def make_condition_options():
    import csv
    conditions = []
    path = '../output/scenario/statistics.csv'
    data = []
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == 'freight_outward' or row[0] == 'exchange_rate':
                data.append([])
                data[-1].append(float(row[1]))
                if row[0] == 'oil_price':
                    data[-1].append(float(row[3]))#/2.0)#stdev
                else:
                    data[-1].append(float(row[3]))#stdev
    for condition_num in range(2):
        mean, stdev = data[condition_num]
        conditions.append([0,mean-3*stdev,mean-2*stdev,mean-stdev,mean,mean+stdev,mean+2*stdev,mean+3*stdev])
        for index in range(8):
            if conditions[-1][index] < 0:
                conditions[-1][index] = 0
    return conditions
OIL_PRICE_LIST = [0,20,40,60,80,100,120,160]
FREIGHT_RATE_LIST,EXCHANGE_RATE_LIST = make_condition_options()
OWN_SHIP_LIST = [0,40,60,80,100,120,140,160]
'''
OIL_PRICE_LIST = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150]
FREIGHT_RATE_LIST = [0,300,500,700,800,900,1000,1100,1200,1300,1400,1600,1800,2000,3000,4000]
EXCHANGE_RATE_LIST = [0,50,60,70,80,90,95,100,105,110,120,130,140,150,160,200]
OWN_SHIP_LIST = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150]
'''
#for distribution
SHIP_DEMAND_LIST = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
SHIP_SUPPLY_LIST = [0,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000]
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


"Sinario parameter"
OUTWARD = 0
RETURN = 1
CCFI = 2
OIL_TYPE = 100
FREIGHT_TYPE = 200
EXCHANGE_TYPE = 300
DEMAND_TYPE = 400
SUPPLY_TYPE = 500
NEWSHIPMARKET_TYPE =600
SECONDHAND_TYPE = 700
DELTA_T_MONTH = 12
DELTA_T_DAY = 30

"Rule parameter"
DECISION_CHARTER_OUT = 0
DECISION_CHARTER_IN = 1

"Others"
AVERAGE_SHIP_SIZE = 3.894
HUNDRED_MILLION = 1.0 * 10**8
SCALING = 10000
NUM_DISPLAY = 3
F_INCLINATION = 0.128162493
F_INTERCEPT = 625.7839568
NEW_BUILDING_INCLINATION = 107418.2591/AVERAGE_SHIP_SIZE
NEW_BUILDING_INTERCEPT = 2.07166179
SECONDHAND_INCLINATION = 293185.6353/AVERAGE_SHIP_SIZE
SECONDHAND_INTERCEPT = -133.3114819
#without oil
FREIGHT_OUTWARD_INCLINATION = 5573028.886/AVERAGE_SHIP_SIZE
FREIGHT_OUTWARD_INTERCEPT = -2182.71276
FREIGHT_OUTWARD_DELAY = 0
FREIGHT_RETURN_INCLINATION = 1889523.524/AVERAGE_SHIP_SIZE
FREIGHT_RETURN_INTERCEPT = -363.8396324
#with oil
F_OUTWARD_INCLINATION_OIL = 5.564948355
F_OUTWARD_INCLINATION_DEMAND = 2588604.082/AVERAGE_SHIP_SIZE
F_OUTWARD_INTERCEPT = -783.5510068
F_RETURN_INCLINATION_OIL = 3.355275021
F_RETURN_INCLINATION_DEMAND = 90123.89569/AVERAGE_SHIP_SIZE
F_RETURN_INTERCEPT = 479.7571415
FREIGHT_RETURN_DELAY = 0
FREIGHT_MAX_DELAY = 0
FREIGHT_0 = 1250
FREIGHT_1 = 1140
FREIGHT_2 = 1070
FREIGHT_3 = 1280
FREIGHT_PREV = [FREIGHT_3,FREIGHT_2,FREIGHT_1]
MONTH = 0
YEAR = 1
MAX_OIL_PRICE = 160
MAX_EXCHANGE = 200
