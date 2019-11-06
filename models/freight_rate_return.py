import numpy as np
import sys
import math
import datetime
import matplotlib.pyplot as plt
import os
#import openpyxl

# import own modules #
sys.path.append('../public')
from my_modules import *
from constants  import *

class FreightReturn:
    def __init__(self, history_data=None, neu=None, sigma=None, u=None, d=None, p=None):
        if history_data is None:
            self.history_data = load_monthly_freight_rate_data(RETURN)
            self.flag = True
        else:
            self.history_data = history_data
            self.flag = False

        # initialize parameters
        if self.flag:
            if (neu is None or sigma is None or u is None or d is None or p is None):
                self.calc_params_from_history()
            else:
                self.neu, self.sigma, self.u, self.d, self.p = neu, sigma, u, d, p

    # calc neu and sigma from history data
    def calc_params_from_history(self):
        index   = 0
        delta_t = 1.0 / 12
        values  = np.array([])
        for date, freight_rate in self.history_data:
            if index == 0:
                # initialize the price
                s_0 = freight_rate
            else:
                s_t      = freight_rate
                base_val = math.log(s_t / s_0)
                values   = np.append(values, base_val)
                # update the price
                s_0      = freight_rate
            index += 1

        # substitute inf to nan in values
        values = inf_to_nan_in_array(values)
        self.neu    = np.nanmean(values)
        self.sigma  = np.nanstd(values)
        self.u      = np.exp(self.sigma * np.sqrt(delta_t))
        self.d      = np.exp(self.sigma * (-1) * np.sqrt(delta_t))
        self.p      = 0.5 + 0.5 * (self.neu / self.sigma) * np.sqrt(delta_t)
        return

    def calc_freight_rate(self, current_freight_rate):
        return self.u * current_freight_rate if prob(self.p) else self.d * current_freight_rate

    # generate predicted sinario
    def generate_sinario(self,predict_years=DEFAULT_PREDICT_YEARS,predict_pattern_number=DEFAULT_PREDICT_PATTERN_NUMBER):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years
        if self.flag:
            # predicted data type
            dt   = np.dtype({'names': ('date', 'price'),
                             'formats': ('S10' , np.float)})
            self.predicted_data = np.array([], dtype=dt)

            predict_months_num = int(self.predict_years * 12)

            # latest date from history_data
            latest_history_date_str, latest_freight_rate = self.history_data[-1]

            latest_history_date                      = datetime.datetime.strptime(latest_history_date_str.decode('UTF-8'), '%Y/%m/%d')

            for pattern in range(predict_pattern_number):
                current_date  = latest_history_date
                current_freight_rate = latest_freight_rate
                for predict_month_num in range(predict_months_num):
                    current_date        = add_month(current_date)
                    current_date_str    = datetime.datetime.strftime(current_date, '%Y/%m/%d')
                    current_freight_rate    = self.calc_freight_rate(current_freight_rate)

                    #make a threshold
                    if current_freight_rate > 2500:
                        current_freight_rate = current_freight_rate * self.d /self.u
                    if current_freight_rate < 500:
                        current_freight_rate = current_freight_rate * self.u /self.d

                    self.predicted_data = np.append(self.predicted_data, np.array([(current_date_str, current_freight_rate)], dtype=dt))
            self.predicted_data = self.predicted_data.reshape(DEFAULT_PREDICT_PATTERN_NUMBER,VESSEL_LIFE_TIME*12)
        else:
            self.predicted_data = np.copy(self.history_data)
            for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
                for time in range(len(self.history_data[pattern])):
                    self.predicted_data[pattern][time]['price'] = 625.7839568 + 0.128162493 * self.history_data[pattern][time]['price']
        self.export_excel()
        return

    def depict(self):
        x = range(self.predict_years*12)
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            y = []
            for i in range(self.predict_years*12):
                y.append(self.predicted_data[pattern][i]['price'])
            plt.plot(x, y)#,label='pattern {0}'.format(pattern+1))
        plt.title('Transition of freight rate return', fontsize = 20)
        plt.xlabel('month', fontsize = 16)
        plt.ylabel('freight rate return', fontsize = 16)
        #plt.tick_params(labelsize=14)
        #plt.legend(loc = 'lower right')
        plt.grid(True)
        save_dir = '../output'
        plt.savefig(os.path.join(save_dir, 'freight_rate_return.png'))
        plt.close()
        #plt.savefig(os.path.join(save_dir, 'freight_rate_return.png'))
        #plt.show()
    '''
    def export_excel(self):
        path = '../output/freight_return.xlsx'
        wb = openpyxl.load_workbook(path)
        sheet = wb['Sheet1']
        for i in range(self.predict_years*12):
            for j in range(DEFAULT_PREDICT_PATTERN_NUMBER):
                sheet.cell(row = i + 1, column = 2*j + 1).value = self.predicted_data[j][i]['date']
                sheet.cell(row = i + 1, column = 2*j + 2).value = self.predicted_data[j][i]['price']
        wb.save(path)
        wb.close()
    '''
