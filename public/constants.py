"Ship parameter"
TEU_SIZE = 9300#TEU
INITIAL_SPEED = 19#knot
ROUTE_DISTANCE = 23179*1.60934#km
INITIAL_COST_OF_SHIPBUIDING = 99.9 * 1000000#$ refer = https://link.springer.com/content/pdf/10.1007%2Fs00773-014-0262-5.pdf
FINAL_VALUE = 3.0 * 1000000
NON_FUELED_COST  = 18.418 * 1000000 # $/year
ORDER_TIME = 18
WITHIN_FIVE = 550
WITHIN_TEN = 1043
WITHIN_FIF = 570

"Profit calculation parameter"
VESSEL_LIFE_TIME         = 15#year
OPERATION_DURATION_YEARS = VESSEL_LIFE_TIME
DEFAULT_PREDICT_YEARS    = OPERATION_DURATION_YEARS
DISCOUNT_RATE = 0.06
CHARTER_TIME = 12
RISK_PREMIUM = [0.99,0.98,0.95,0.9]
INDIRECT_COST = 0.05
LOAD_FACTOR_ASIA_TO_EUROPE = 0.75
LOAD_FACTOR_EUROPE_TO_ASIA = 0.34
INITIAL_NUMBER_OF_SHIPS = 100
ORDER_CAPACITY=40
SHIP_NUMBER_PER_DEMAND = 1/0.002016513
LOADING_DAYS = 2
FIVE_YEARS_OLD = 60

"GA parameter"
GENETIC_ALGORITHM_PARAMETER = {'scenario_pattern': 1000, 'generation':1, 'population_size':100}
DEFAULT_PREDICT_PATTERN_NUMBER = GENETIC_ALGORITHM_PARAMETER['scenario_pattern']
DEFAULT_GENERATION = GENETIC_ALGORITHM_PARAMETER['generation']
DEFAULT_POPULATION_SIZE = GENETIC_ALGORITHM_PARAMETER['population_size']
DEFAULT_CROSSOVER_RATE = 0.70
DEFAULT_ALPHA = 0.01


"Chromosome paramater"
DEFAULT_NUM_OF_CONDITION = 4
DEFAULT_NUM_OF_ACTION = 6
OIL_PRICE_LIST = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150]
FREIGHT_RATE_LIST = [0,300,500,700,900,1000,1100,1200,1300,1500,1800,2000,2200,2500,3000,4000]
EXCHANGE_RATE_LIST = [0,50,60,70,80,90,95,100,105,110,120,130,140,150,160,200]
OWN_SHIP_LIST = [0,50,80,90,95,97,98,99,100,101,102,103,105,110,120,120]
SHIP_DEMAND_LIST = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
SHIP_SUPPLY_LIST = [0,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000]
VESSEL_SPEED_LIST = [18,19,20,21]
PURCHASE_NUMBER = [0,1,3,5]
SELL_NUMBER = [0,1,3,5]
CHARTER_IN_NUMBER = [0,1,3,5]
CHARTER_OUT_NUMBER = [0,1,3,5]
CHARTER_PERIOD = [3,6,12,36]
GRAY_CODE_4 = [0,1,3,2,7,6,4,5,15,14,12,13,8,9,11,10]


"Sinario parameter"
OUTWARD = 0
RETURN = 1
CCFI = 2
OIL_TYPE = 100
FREIGHT_TYPE = 200
EXCHANGE_TYPE = 300
DEMAND_TYPE = 400
SUPPLY_TYPE = 500
DELTA_T = 12

"Rule parameter"
DECISION_CHARTER_OUT = 0
DECISION_CHARTER_IN = 1

"Others"
HUNDRED_MILLION = 1.0 * 10**10
NUM_DISPLAY = 3
F_INCLINATION = 0.128162493
F_INTERCEPT = 625.7839568
FREIGHT_OUTWARD_INCLINATION = -2661522.996
FREIGHT_OUTWARD_INTERCEPT = 6834.623141
FREIGHT_OUTWARD_DELAY = -9
FREIGHT_RETURN_INCLINATION = -829816.2646
FREIGHT_RETURN_INTERCEPT = 2515.370692
FREIGHT_RETURN_DELAY = -3
FREIGHT_MAX_DELAY = 9
FREIGHT_0 = 1270
FREIGHT_1 = 1170
FREIGHT_2 = 1080
FREIGHT_3 = 1160
FREIGHT_PREV = [FREIGHT_3,FREIGHT_2,FREIGHT_1]
MONTH = 0
YEAR = 1
