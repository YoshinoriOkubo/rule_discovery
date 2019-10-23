import calendar as cal
import numpy as np
import datetime
import os
import matplotlib.pyplot as plt
from constants import *

#load history data of crude oil
def load_monthly_history_data(from_date=None, to_date=None):
    history_data_path = '../data/crude_oil_monthly_history.csv'
    # read data
    dt   = np.dtype({'names': ('date', 'price'),
                   'formats': ('S10' , np.float)})
    data = np.genfromtxt(history_data_path,
                         delimiter=',',
                         dtype=dt,
                         usecols=[0,1],
                         skip_header=1)

    # from_date
    if not from_date is None:
        from_datetime = datetime.datetime.strptime(from_date, "%Y/%m/%d")
        for index in range(len(data)):
            datetime_key = datetime.datetime.strptime(data['date'][index], "%Y/%m/%d")
            if from_datetime <= datetime_key:
                break
        data = data[index:]

    # to_date
    if not to_date is None:
        to_datetime = datetime.datetime.strptime(to_date, "%Y/%m/%d")
        for index in range(len(data)):
            datetime_key = datetime.datetime.strptime(data['date'][index], "%Y/%m/%d")
            if to_datetime <= datetime_key:
                break
        data = data[:index]

    return data

#load history data of freight rate
def load_monthly_freight_rate_data(direction,from_date=None, to_date=None):
    if direction == OUTWARD:
        history_data_path = '../data/freight_rate_history_outward.csv'
    else:
        if direction == RETURN:
            history_data_path = '../data/freight_rate_history_return.csv'
        else:
            if direction == CCFI:
                history_data_path = '../data/ccfi_history.csv'
            else:
                raise Exception('Error!')
    # read data
    dt   = np.dtype({'names': ('date', 'price'),
                   'formats': ('S10' , np.float)})
    data = np.genfromtxt(history_data_path,
                         delimiter=',',
                         dtype=dt,
                         usecols=[0,1],
                         skip_header=1)

    # from_date
    if not from_date is None:
        from_datetime = datetime.datetime.strptime(from_date, "%Y/%m/%d")
        for index in range(len(data)):
            datetime_key = datetime.datetime.strptime(data['date'][index], "%Y/%m/%d")
            if from_datetime <= datetime_key:
                break
        data = data[index:]

    # to_date
    if not to_date is None:
        to_datetime = datetime.datetime.strptime(to_date, "%Y/%m/%d")
        for index in range(len(data)):
            datetime_key = datetime.datetime.strptime(data['date'][index], "%Y/%m/%d")
            if to_datetime <= datetime_key:
                break
        data = data[:index]

    return data

#load history data of freight rate
def load_monthly_exchange_rate_data(from_date=None, to_date=None):
    history_data_path = '../data/exchange_rate_after_praza_agreement.csv'

    # read data
    dt   = np.dtype({'names': ('date', 'price'),
                   'formats': ('S10' , np.float)})
    data = np.genfromtxt(history_data_path,
                         delimiter=',',
                         dtype=dt,
                         usecols=[0,1],
                         skip_header=1)

    # from_date
    if not from_date is None:
        from_datetime = datetime.datetime.strptime(from_date, "%Y/%m/%d")
        for index in range(len(data)):
            datetime_key = datetime.datetime.strptime(data['date'][index], "%Y/%m/%d")
            if from_datetime <= datetime_key:
                break
        data = data[index:]

    # to_date
    if not to_date is None:
        to_datetime = datetime.datetime.strptime(to_date, "%Y/%m/%d")
        for index in range(len(data)):
            datetime_key = datetime.datetime.strptime(data['date'][index], "%Y/%m/%d")
            if to_datetime <= datetime_key:
                break
        data = data[:index]

    return data

# substitute inf to nan in values
def inf_to_nan_in_array(values):
    inf_induces = np.where(values==float('-inf'))[0]

    for i in range(len(inf_induces)):
        values[inf_induces[i]] = float('nan')

    return values

def add_month(current_date, num=1):
    for _n in range(num):
        _d, days      = cal.monthrange(current_date.year, current_date.month)
        current_date += datetime.timedelta(days=days)
    return current_date

def add_year(start_date, year_num=1):
    current_date = start_date
    if year_num < 1:
        current_date = add_month(current_date, int(year_num * 12))
        return current_date

    for year_index in range(year_num):
        current_date = add_month(current_date, 12)
    return current_date

def prob(prob_value):
    N = 10000
    nonzero_num = np.count_nonzero(np.random.binomial(1, prob_value, N))
    threshold   = N * prob_value
    return (nonzero_num > threshold)

def calc_statistics(list):
    n = len(list)
    e = 0
    sigma = 0
    for i in range(n):
        e += list[i]
    e /= n
    for i in range(n):
        sigma += (list[i] - e)**2
    sigma /= n
    return [e,sigma]

def depict_real_freight(freight_outward,freight_return):
    distribution = [0,0,0,0,0,0,0,0]
    range_0 = [200,300,400,500,600,700,800,900,1000]
    total_freight = []
    for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
        total_freight.append([])
        for x in range(VESSEL_LIFE_TIME * 12):
            f = 0.5*(freight_outward.predicted_data[pattern][x]['price'] * LOAD_FACTOR_ASIA_TO_EUROPE + freight_return.predicted_data[pattern][x]['price'] * LOAD_FACTOR_EUROPE_TO_ASIA)
            total_freight[pattern].append(f)
            for i in range(8):
                if range_0[i] < f and f < range_0[i+1]:
                    distribution[i] += 1
        _x = range(0,VESSEL_LIFE_TIME*12)
        plt.plot(_x, total_freight[pattern])
        plt.title('Transition of total freight', fontsize = 20)
        plt.xlabel('month', fontsize = 16)
        plt.ylabel('total freight rate value', fontsize = 16)
        plt.grid(True)
    save_dir = '../output'
    plt.savefig(os.path.join(save_dir, 'real_freight.png'))
    plt.close()
    #s'''

    for index in range(len(distribution)):
        distribution[index] = distribution[index]/(DEFAULT_PREDICT_PATTERN_NUMBER*180.0)
    #left = [200,300,400,500,600,700,800,900]
    left = [0,1,2,3,4,5,6,7]
    label = ['200','300','400','500','600','700','800','900']
    plt.title('Freight distribution')
    plt.xlabel('real freight')
    plt.ylabel('Propability')
    plt.bar(left,distribution,tick_label=label,align='center')
    save_dir = '../output'
    plt.savefig(os.path.join(save_dir, 'freight_distribution.png'))
    plt.close()
