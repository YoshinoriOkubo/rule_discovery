TEU_SIZE = 9300#TEU
INITIAL_SPEED = 19#knot
ROUTE_DISTANCE = 24000#km

INITIAL_COST_OF_SHIPBUIDING = 99.9 * 1000000#$ refer = https://link.springer.com/content/pdf/10.1007%2Fs00773-014-0262-5.pdf
DPRECIATION_TIME = 10#year
DISCOUNT_RATE = 0.1
MINIMUM_SHIP_SPEED = 10#knot
NON_FUELED_COST  = 18.418 * 1000000 # $/year

LOAD_FACTOR_ASIA_TO_EUROPE = 0.75
LOAD_FACTOR_EUROPE_TO_ASIA = 0.34
FREIGHT_RATE_ASIA_TO_EUROPE = 1490
FREIGHT_RATE_EUROPE_TO_ASIA = 860
OUTWARD = 0
RETURN = 1
FULL_SEARCH = 3
DECISION_SPEED = 0
DECISION_SELL = 1

ACTION_SELL = 0
ACTION_STAY = 1

VESSEL_LIFE_TIME         = 15#year
OPERATION_DURATION_YEARS = VESSEL_LIFE_TIME
DEFAULT_PREDICT_YEARS    = OPERATION_DURATION_YEARS

GENETIC_ALGORITHM_PARAMETER = {'pattern':10, 'generation':5, 'individual':100}
DEFAULT_PREDICT_PATTERN_NUMBER = GENETIC_ALGORITHM_PARAMETER['pattern']
DEFAULT_GENERATION = GENETIC_ALGORITHM_PARAMETER['generation']
DEFAULT_NUM_OF_INDIVIDUAL = GENETIC_ALGORITHM_PARAMETER['individual']
DEFAULT_CROSSING_RATE = 0.70

DEFAULT_ALPHA = 0.25
OIL_PRICE_LIST = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150]
VESSEL_SPEED_LIST = [10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
FREIGHT_RATE_LIST = [0,200,300,400,500,550,600,650,700,750,800,900,1000,1100,1300,1500]

GRAY_CODE = [0,1,3,2,7,6,4,5,15,14,12,13,8,9,11,10]
DEFAULT_NUM_OF_CONDITION = 2
