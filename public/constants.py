# dir path from models
RESULT_DIR_PATH         = '../results'
GRAPH_DIR_PATH          = "%s/graphs" % (RESULT_DIR_PATH)
DATA_PATH               = '../data/'
COMPONENT_PATH          = '../data/components_lists'
VALIDATION_LOG_DIR_PATH = "%s/varidation"   % (RESULT_DIR_PATH)
AGNET_LOG_DIR_PATH      = "%s/agent_log"    % (RESULT_DIR_PATH)
COMBINATIONS_DIR_PATH   = "%s/combinations" % (RESULT_DIR_PATH)
WAVE_DIR_PATH           = "%s/wave"         % (RESULT_DIR_PATH)
CORRELATION_DIR_PATH    = "%s/correlation"  % (RESULT_DIR_PATH)
BEAUFORT_RESULT_PATH    = "%s/beauforts"  % (RESULT_DIR_PATH)
INITIAL_DESIGN_RESULT   = "%s/initial_design"  % (RESULT_DIR_PATH)
NARROW_DOWN_RESULT_PATH = "%s/narrow_down_result"  % (INITIAL_DESIGN_RESULT)
NARROWED_RESULT_PATH    = "%s/narrowed_result"  % (INITIAL_DESIGN_RESULT)
SENSITIVITY_DIR_PATH    = "%s/sensitivity" % (RESULT_DIR_PATH)
THESIS_DIR_PATH         = "%s/thesis"    % (RESULT_DIR_PATH)

# seed num
COMMON_SEED_NUM         = 19901129

# dir path from scripts
NOHUP_LOG_DIR_PATH    = '../nohup'

# for multiprocessing
import getpass
current_user = getpass.getuser()
PROC_NUM = 15 if current_user == 'tsaito' else 3
# for multiprocessing

VESSEL_LIFE_TIME         = 15
OPERATION_DURATION_YEARS = VESSEL_LIFE_TIME

DEFAULT_PREDICT_YEARS    = OPERATION_DURATION_YEARS

# navigation infomation [mile]
NAVIGATION_DISTANCE_A = 6590
NAVIGATION_DISTANCE_B = 10000

DERIVE_SINARIO_MODE   = {'high': 0,
                         'low': 1,
                         'binomial': 2,
                         'maintain': 3}

RETROFIT_MODE = {'none': 0,
                 'propeller': 1,
                 'propeller_and_engine': 2,
                 'whole': 3,
                 'significant': 4,
                 'significant_rule': 5,
                 'route_change': 6,
                 'route_change_merged': 7}

RETROFIT_COST = {'propeller': 200000,
                 'engine': 1000000}

# Beaufort mode
BF_MODE = {'rough': 0,
           'calm': 1}

# Retrofit mode
RETROFIT_SCENARIO_MODE = {'significant': 0,
                          'binomiial': 1}

# default simulate count for searching initial design
DEFAULT_SIMULATE_COUNT                        = 50
SIMMULATION_DURATION_YEARS_FOR_INITIAL_DESIGN = 15
# narrowed down design ratio for initial design
NARROWED_DOWN_DESIGN_RATIO                    = 0.1
NARROWED_DOWN_DURATION_YEARS                  = 2
NARROWED_DOWN_DURATION_SIMULATE_COUNT         = 10
MINIMUM_NARROWED_DOWN_DESIGN_NUM              = 100

# simmulation duration for retrofits
SIMMULATION_TIMES_FOR_RETROFITS          = 15
SIMMULATION_RANK_THRESHOLD_FOR_RETROFITS = 10

# days taken to load
LOAD_DAYS = 2

# dock-in
## dock-in period [years]
DOCK_IN_PERIOD   = 2
## dock-in duration [month]
DOCK_IN_DURATION = 1

# 200 [dollars/barrel]
HIGH_OIL_PRICE = 200
# 100 [dollars/barrel]
LOW_OIL_PRICE = 80


# load condition [ballast, full]
LOAD_CONDITION = {0: 'ballast',
                  1: 'full'   }
# initial load condition 'ballast'
INITIAL_LOAD_CONDITION = 0

# default velocity range [knot] #
VELOCITY_RANGE_STRIDE  = 0.10
DEFAULT_VELOCITY_RANGE = {'from'  : 5.0,
                          'to'    : 25.0,
                          'stride': VELOCITY_RANGE_STRIDE}
# default rps range #
RPM_RANGE_STRIDE  = 0.5
DEFAULT_RPM_RANGE = {'from'  : 25.0,
                     'to'    : 80.0,
                     'stride': RPM_RANGE_STRIDE}

# minimum array require rate
MINIMUM_ARRAY_REQUIRE_RATE = 3.0

# thrust coefficient(1-t)
THRUST_COEFFICIENT = 0.8

# wake coefficient(1-w)
WAKE_COEFFICIENT = 0.97

# eta
ETA_S = 0.97

# icr
DEFAULT_ICR_RATE = 0.05

## fix value ##
# dry dock maintenance [USD/year] #
DRY_DOCK_MAINTENANCE = 800000
# maintenance [USD/year] #
MAINTENANCE          = 240000
# crew labor cost [USD/year] #
CREW_LABOR_COST      = 2400000
# Insurance [USD/year] #
INSURANCE            = 240000
## fix value ##

# Port [USD]
PORT_CHARGES    = 100000
PORT_DWELL_DAYS = 2

# Log columns
LOG_COLUMNS = ['ballast', 'full']

# discount rate
DISCOUNT_RATE = 0.01

# model variables
## agent
AGENT_VARIABLES = ['dockin_flag',
                   'velocity_combination',
                   'origin_date',
                   'loading_days',
                   'load_condition',
                   'operation_date_array',
                   'cash_flow',
                   'ballast_trip_days',
                   'round_trip_distance',
                   'retrofit_mode',
                   'retire_date',
                   'log',
                   'total_NPV',
                   'sinario',
                   'loading_flag',
                   'current_date',
                   'hull',
                   'icr',
                   'previous_oilprice',
                   'engine',
                   'latest_dockin_date',
                   'voyage_date',
                   'world_scale',
                   'current_distance',
                   'rpm_array',
                   'total_cash_flow',
                   'total_distance',
                   'propeller',
                   'return_trip_days',
                   'total_elapsed_days',
                   'left_distance_to_port',
                   'current_fare',
                   'oilprice_full',
                   'elapsed_days',
                   'sinario_mode',
                   'oilprice_ballast',
                   'NPV',
                   'velocity_array']

# cull threshold [knot]
CULL_THRESHOLD = 6

# Rank weight
APPR_RANK_WEIGHT = 2
NPV_RANK_WEIGHT  = 1

# engine rpm curve approx degree
ENGINE_CURVE_APPROX_DEGREE = 3
RELATIVE_ENGINE_EFFICIENCY = {1.0: 1.0,
                              0.85: 0.7,
                              0.65: 0.35,
                              0.45: 0.2,
                              0:0}

# velocity deterioration func
V_DETERIO_FUNC_COEFFS = {'cons': -0.0621757689405,
                         'lin': -0.13738023067,
                         "squ": -0.167749562986}
V_DETERIO_M = 2

# Gravitational Acceleration
G_ACCEL = 9.80665

FUILD_DENSITY_SEA = 1.025

# MARKET FACTORS
MARKET_FACTOR_KEYS = ['oilprice', 'world_scale', 'flat_rate']

# SIGNIFICANT SENARIOS
SIGNIFICANT_SENARIO_MODES = {'rise': 0,
                             'maintain': 1,
                             'decline': 2}

# SIGNIFICANT SCENARIO
## RISE RATIO
RISE_RATIO = 1.5
## DECLINE RATIO
DECLINE_RATIO = 0.5
## multiply index
MULTIPLY_INDEX = 2.0
DEVIDE_INDEX = 0.8

# ENGINE SFOC BASE
BASE_PEAK     = 60
SFOC_BASE_DEC = 9

# RETROFIT DESIGNS

RETROFIT_DESIGNS = { 'calm' : {'low': 'H2E1P514' ,'high': 'H1E2P1285', 'dec': 'H1E3P257', 'inc': 'H2E1P514'},
                     'rough': {'low': 'H1E2P514','high': 'H1E3P514', 'middle': 'H1E3P1285'}}
RETROFIT_DESIGNS_FOR_ROUTE_CHANGE = {'rough': {'low': 'H2E2P514','high': 'H2E3P1285', 'middle': 'H2E3P514'}}

TARGET_DESIGNS = {'calm': ['low', 'high', 'dec'],
                  'rough': ['middle']}
'''
RETROFIT_DESIGNS = { 'calm' : {'low': 'H2E1P514' ,'high': 'H2E4P257', 'dec': 'H2E1P514', 'inc': 'H1E4P514'},
                     'rough': {'low': 'H2E2P1285','high': 'H2E4P257', 'dec': 'H2E2P1285', 'inc': 'H2E1P514'}}
'''

# RETROFIT RULES
'''
HIGH_TREND          = 1.0
HIGH_MULTIPLE_INDEX = 2.0
LOW_TREND           = -1.0
LOW_MULTIPLE_INDEX  = 0.5
'''
BASE_TREND = {'origin': 0.0, 'end': 2.0}
BASE_DELTA = {'origin': 0.0, 'end': 0.5}

# NORMALIZE COMPONENTS
PROPELLERS = {'0': 0, '257': 1, '514': 2, '771': 3, '1028': 4, '1285': 5}

# FOR REALOPTION ANALYSIS
UPFRONT_COST   = 300000

# practice prices
PRACTICE_PRICES = {'hull': 30000, 'engine': 20000, 'propeller': 10000}

# for WHOLE RETROFIT
UPFRONT_COST   = 500000

# FOR REALOPTION ANALYSIS (sea)
UPFRONT_COST_ROUTE   = 400000

# derive sinario modes
SIGNIFICANT_SENARIO_MODES_WITH_MONTE = ['high', 'low', 'stage']

# simulate count
SIMULATE_COUNT = 10000

# for actual
CHANGE_ROUTE_PERIODS_RAW = range(0, VESSEL_LIFE_TIME, DOCK_IN_PERIOD)
CHANGE_ROUTE_PERIODS     = CHANGE_ROUTE_PERIODS_RAW[1:]

# change route prob
CHANGE_ROUTE_PROB = {d:100.0/len(CHANGE_ROUTE_PERIODS_RAW) for d in CHANGE_ROUTE_PERIODS_RAW}

# change route rate
CHANGE_ROUTE_MARKET_RATE = 1.1
