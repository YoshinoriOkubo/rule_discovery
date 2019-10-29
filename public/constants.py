"Ship parameter"
TEU_SIZE = 9300#TEU
INITIAL_SPEED = 19#knot
ROUTE_DISTANCE = 24000#km
INITIAL_COST_OF_SHIPBUIDING = 99.9 * 1000000#$ refer = https://link.springer.com/content/pdf/10.1007%2Fs00773-014-0262-5.pdf
NON_FUELED_COST  = 18.418 * 1000000 # $/year


"Profit calculation parameter"
VESSEL_LIFE_TIME         = 15#year
OPERATION_DURATION_YEARS = VESSEL_LIFE_TIME
DEFAULT_PREDICT_YEARS    = OPERATION_DURATION_YEARS
DISCOUNT_RATE = 0.06
RISK_PREMIUM = 0.8
LOAD_FACTOR_ASIA_TO_EUROPE = 0.75
LOAD_FACTOR_EUROPE_TO_ASIA = 0.34
INITIAL_NUMBER_OF_SHIPS = 100

"GA parameter"
GENETIC_ALGORITHM_PARAMETER = {'scenario_pattern':10, 'generation':20, 'population_size':100}
DEFAULT_PREDICT_PATTERN_NUMBER = GENETIC_ALGORITHM_PARAMETER['scenario_pattern']
DEFAULT_GENERATION = GENETIC_ALGORITHM_PARAMETER['generation']
DEFAULT_POPULATION_SIZE = GENETIC_ALGORITHM_PARAMETER['population_size']
DEFAULT_CROSSOVER_RATE = 0.70
DEFAULT_ALPHA = 0.01
ROULETTE = 100
TOURNAMENT = 200
STEADY_STATE = 300


"Chromosome paramater"
DEFAULT_NUM_OF_CONDITION = 3
OIL_PRICE_LIST = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150]
VESSEL_SPEED_LIST = [11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
FREIGHT_RATE_LIST = [0,300,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1800,2000,3000]
EXCHANGE_RATE_LIST = [0,50,60,70,80,90,95,100,105,110,120,130,140,150,160,200]
#SELL_NUMBER = []
#CHARTER_NUMBER = []
#for i in range(16):
#    SELL_NUMBER.append(100)
#    CHARTER_NUMBER.append(100)
SELL_NUMBER = [0,5,10,15,20,25,30,40,50,60,70,80,90,100,100,100]
CHARTER_NUMBER = [0,5,10,15,20,25,30,40,50,60,70,80,90,100,100,100]
CHARTER_PERIOD = [3,6,12,36]
GRAY_CODE_2 = [0,1,3,2]
GRAY_CODE_4 = [0,1,3,2,7,6,4,5,15,14,12,13,8,9,11,10]


"Sinario parameter"
OUTWARD = 0
RETURN = 1
CCFI = 2

"Rule parameter"
DECISION_SPEED = 0
DECISION_SELL = 1
DECISION_CHARTER = 2
DECISION_INTEGRATE = 3
RULE_SET = [DECISION_SPEED,DECISION_SELL, DECISION_CHARTER]
ACTION_STAY = [0,0,0,0]
PRIORITY_SELL_CHARTER = [1,2]
PRIORITY_CHARTER_SELL = [2,1]

"Others"
HUNDRED_MILLION = 1.0 * 10**10
NUM_DISPLAY = 3
