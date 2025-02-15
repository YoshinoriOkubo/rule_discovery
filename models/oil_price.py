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

class Oil:
    def __init__(self, history_data=None, neu=None, sigma=None, u=None, d=None, p=None):
        if history_data is None:
            self.monthly_history_data = load_history_data(MONTH,OIL_TYPE)
        else:
            self.monthly_history_data = history_data
        # initialize parameters
        if (neu is None or sigma is None or u is None or d is None or p is None):
            self.calc_params_from_history()
        else:
            self.neu, self.sigma, self.u, self.d, self.p = neu, sigma, u, d, p

    # calc neu and sigma from history data
    def calc_params_from_history(self):
        index   = 0
        delta_t = 1.0 / DELTA_T_DAY
        values  = np.array([])
        for date, oil_price in self.monthly_history_data:
            if index == 0:
                # initialize the price
                s_0 = oil_price
            else:
                s_t      = oil_price
                base_val = math.log(s_t / s_0)
                values   = np.append(values, base_val)
                # update the price
                s_0      = oil_price
            index += 1
        # substitute inf to nan in values
        values = inf_to_nan_in_array(values)
        self.neu    = np.nanmean(values)
        self.sigma  = np.nanstd(values)
        self.u      = np.exp(self.sigma * np.sqrt(delta_t))
        self.d      = np.exp(self.sigma * (-1) * np.sqrt(delta_t))
        self.p      = 0.5 + 0.5 * (self.neu / self.sigma) * np.sqrt(delta_t)
        return

    def calc_oilprice(self, current_oilprice):
        return self.u * current_oilprice if random.randint(0,1) < self.p else self.d * current_oilprice

    # generate predicted scenario
    def generate_scenario(self,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years

        # predicted data type
        self.predicted_data = []
        for p_num in range(predict_pattern_number):
            self.predicted_data.append([])

        predict_months_num = int(self.predict_years * 12)

        # latest date from history_data
        latest_history_date_str, latest_oilprice = self.monthly_history_data[-1]
        latest_history_date                      = datetime.datetime.strptime(latest_history_date_str.decode('UTF-8'), '%Y/%m/%d')
        for pattern in range(predict_pattern_number):
            current_date  = latest_history_date
            current_oilprice = latest_oilprice
            for predict_month_num in range(predict_months_num):
                current_date        = add_month(current_date)
                current_date_str    = datetime.datetime.strftime(current_date, '%Y/%m/%d')
                for time in range(DELTA_T_DAY):
                    current_oilprice    = self.calc_oilprice(current_oilprice)
                    if current_oilprice > MAX_OIL_PRICE:
                        current_oilprice = current_oilprice/self.u
                self.predicted_data[pattern].append({'date':current_date_str,'price':current_oilprice})
        return
