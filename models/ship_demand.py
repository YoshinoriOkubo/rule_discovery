import numpy as np
import sys
import math
import datetime
import os
import random
# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

class ShipDemand:
    def __init__(self, history_data=None, neu=None, sigma=None, u=None, d=None, p=None):
        if history_data is None:
            self.yearly_history_data = load_history_data(YEAR,DEMAND_TYPE)
            self.monthly_history_data = load_history_data(MONTH,DEMAND_TYPE)
        else:
            self.yearly_history_data = history_data
        # initialize parameters
        if (neu is None or sigma is None or u is None or d is None or p is None):
            self.calc_params_from_history()
        else:
            self.neu, self.sigma, self.u, self.d, self.p = neu, sigma, u, d, p

    # calc neu and sigma from history data
    def calc_params_from_history(self):
        index   = 0
        delta_t = 1.0 / DELTA_T
        values  = np.array([])
        for date, ship_demand in self.yearly_history_data:
            if index == 0:
                # initialize the price
                s_0 = ship_demand
            else:
                s_t      = ship_demand
                base_val = math.log(s_t / s_0)
                values   = np.append(values, base_val)
                # update the price
                s_0      = ship_demand
            index += 1

        # substitute inf to nan in values
        values = inf_to_nan_in_array(values)
        self.neu    = np.nanmean(values)
        self.sigma  = np.nanstd(values)
        self.u      = np.exp(self.sigma * np.sqrt(delta_t))
        self.d      = np.exp(self.sigma * (-1) * np.sqrt(delta_t))
        self.p      = 0.5 + 0.5 * (self.neu / self.sigma) * np.sqrt(delta_t)
        return

    def calc_ship_demand(self, current_ship_demand):
        return self.u * current_ship_demand if random.randint(0,1) < self.p else self.d * current_ship_demand

    # generate predicted sinario
    def generate_sinario(self,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years

        # predicted data type
        dt   = np.dtype({'names': ('date', 'price'),
                         'formats': ('S10' , np.float)})
        self.predicted_data = np.array([], dtype=dt)

        predict_months_num = int(self.predict_years * 12)

        # latest date from history_data
        latest_history_date_str, latest_ship_demand = self.yearly_history_data[-1]
        latest_history_date                      = datetime.datetime.strptime(latest_history_date_str.decode('UTF-8'), '%Y/%m/%d')
        for pattern in range(predict_pattern_number):
            current_date  = latest_history_date
            current_ship_demand = latest_ship_demand
            for predict_month_num in range(predict_months_num+FREIGHT_MAX_DELAY):
                current_date        = add_month(current_date)
                current_date_str    = datetime.datetime.strftime(current_date, '%Y/%m/%d')
                current_ship_demand    = self.calc_ship_demand(current_ship_demand)
                self.predicted_data = np.append(self.predicted_data, np.array([(current_date_str, current_ship_demand)], dtype=dt))
        self.predicted_data = self.predicted_data.reshape(DEFAULT_PREDICT_PATTERN_NUMBER,predict_years*12+FREIGHT_MAX_DELAY)
        return
