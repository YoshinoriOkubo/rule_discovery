import calendar as cal
import numpy as np
import datetime
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


# load history data of world scale
## monthly
def load_world_scale_history_data(from_date=None, to_date=None):
    history_data_path = '../data/world_scale.csv'
    # read data
    dt   = np.dtype({'names': ('date', 'ws'),
                   'formats': ('S10' , np.float)})
    data = np.genfromtxt(history_data_path,
                         delimiter=',',
                         dtype=dt,
                         usecols=[0,1],
                         skiprows=1)
    index = 0
    if not from_date is None:
        from_datetime = datetime.datetime.strptime(from_date, "%Y/%m/%d")
        for index in range(len(data)):
            datetime_key = datetime.datetime.strptime(data['date'][index], "%Y/%m/%d")
            if from_datetime <= datetime_key:
                break
    return data[index:]

# load history data of flat rate
## monthly
def load_flat_rate_history_data(from_date=None, to_date=None):
    history_data_path = '../data/flat_rate.csv'
    # read data
    dt   = np.dtype({'names': ('date', 'fr'),
                   'formats': ('S10' , np.float)})
    data = np.genfromtxt(history_data_path,
                         delimiter=',',
                         dtype=dt,
                         usecols=[0,1],
                         skiprows=1)
    index = 0
    if not from_date is None:
        from_datetime = datetime.datetime.strptime(from_date, "%Y/%m/%d")
        for index in range(len(data)):
            datetime_key = datetime.datetime.strptime(data['date'][index], "%Y/%m/%d")
            if from_datetime <= datetime_key:
                break
    return data[index:]

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
