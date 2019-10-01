import numpy as np
import sys
import math
import datetime

# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

class Sinario:
    def __init__(self, history_data=None, neu=None, sigma=None, u=None, d=None, p=None):
        if history_data is None:
            self.history_data = load_monthly_history_data()
        else:
            self.history_data = history_data
        # initialize parameters
        if (neu is None or sigma is None or u is None or d is None or p is None):
            self.calc_params_from_history()
        else:
            self.neu, self.sigma, self.u, self.d, self.p = neu, sigma, u, d, p

    # calc neu and sigma from history data
    def calc_params_from_history(self):
        index   = 0
        delta_t = 1.0 / 12
        values  = np.array([])
        for date, oil_price in self.history_data:
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
        return self.u * current_oilprice if prob(self.p) else self.d * current_oilprice

    # generate predicted sinario
    def generate_sinario(self, sinario_mode, predict_years=DEFAULT_PREDICT_YEARS):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years

        # predicted data type
        dt   = np.dtype({'names': ('date', 'price'),
                         'formats': ('S10' , np.float)})
        self.predicted_data = np.array([], dtype=dt)

        predict_months_num = int(self.predict_years * 12)

        # latest date from history_data
        latest_history_date_str, latest_oilprice = self.history_data[-1]
        #日付型に変換
        latest_history_date                      = datetime.datetime.strptime(latest_history_date_str.decode('UTF-8'), '%Y/%m/%d')

        current_date  = latest_history_date
        current_oilprice = latest_oilprice
        for predict_month_num in range(predict_months_num):
            current_date        = add_month(current_date)
            current_date_str    = datetime.datetime.strftime(current_date, '%Y/%m/%d')

            # change oil_price by mode
            if sinario_mode == DERIVE_SINARIO_MODE['high']:
                current_oilprice = HIGH_OIL_PRICE
            elif sinario_mode == DERIVE_SINARIO_MODE['low']:
                current_oilprice = LOW_OIL_PRICE
            elif sinario_mode == DERIVE_SINARIO_MODE['maintain']:
                current_oilprice = current_oilprice
            else:#mean binomial
                current_oilprice    = self.calc_oilprice(current_oilprice)
            # change oil_price by mode

            self.predicted_data = np.append(self.predicted_data, np.array([(current_date_str, current_oilprice)], dtype=dt))

        return
