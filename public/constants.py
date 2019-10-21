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
DEPRECIATION_TIME = 10#year
DISCOUNT_RATE = 0.06
RISK_PREMIUM = 0.8
LOAD_FACTOR_ASIA_TO_EUROPE = 0.75
LOAD_FACTOR_EUROPE_TO_ASIA = 0.34
EXCHANGE_RATE = 100

"GA parameter"
GENETIC_ALGORITHM_PARAMETER = {'pattern':30, 'generation':20, 'individual':100}
DEFAULT_PREDICT_PATTERN_NUMBER = GENETIC_ALGORITHM_PARAMETER['pattern']
DEFAULT_GENERATION = GENETIC_ALGORITHM_PARAMETER['generation']
DEFAULT_NUM_OF_INDIVIDUAL = GENETIC_ALGORITHM_PARAMETER['individual']
DEFAULT_CROSSING_RATE = 0.90
DEFAULT_ALPHA = 0.05
ROULETTE = 100
TOURNAMENT = 200
STEADY_STATE = 300


"Chromosome paramater"
DEFAULT_NUM_OF_CONDITION = 2
OIL_PRICE_LIST = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150]
VESSEL_SPEED_LIST = [10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
FREIGHT_RATE_LIST = [0,200,300,400,500,550,600,650,700,750,800,900,1000,1100,1300,1500]
SELL_PERCENTAGE = [0,0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,1,1,1]
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
ACTION_SELL = 0
ACTION_STAY = [0,0,0,0]
ACTION_CHARTER = 0
ACTION_NOTHING = 1
PRIORITY_SELL_CHARTER = [1,2]
PRIORITY_CHARTER_SELL = [2,1]

"Others"
HUNDRED_MILLION = 100000000
NUM_DISPLAY = 3
