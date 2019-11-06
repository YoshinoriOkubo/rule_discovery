import calendar as cal
import numpy as np
import datetime
import os
import csv
import matplotlib.pyplot as plt
from constants import *

def convert2to10_in_list(list):
    result = 0
    length = len(list)
    for i in range(len(list)):
        x = length - 1 - i
        result += list[i] * 2 ** (x)
    if len(list) == 4:
        return GRAY_CODE_4[result]
    elif len(list) == 1:
        return result
    else:
        return None

def export_scenario_csv(list,name):
    path = '../output/{}.csv'.format(name)
    with open(path, 'w') as f:
        pass
    with open(path, 'a') as f:
        writer = csv.writer(f)
        for time in range(VESSEL_LIFE_TIME*12):
            row = []
            for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
                row.append(list[pattern][time]['date'])
                row.append(list[pattern][time]['price'])
            print(row)
            writer.writerow(row)

def export_rules_csv(list):
    with open('../output/ship_rule.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','expectation','variance'])
    with open('../output/ship_rule.csv', 'a') as f:
        writer = csv.writer(f)
        for index in range(len(list)):
            row = []
            individual = list[index]
            for col_cond in range(DEFAULT_NUM_OF_CONDITION*2):
                if col_cond == 0 or col_cond == 1:
                    row.append(OIL_PRICE_LIST[convert2to10_in_list(individual[col_cond])])
                elif col_cond == 2 or col_cond == 3:
                    row.append(FREIGHT_RATE_LIST[convert2to10_in_list(individual[col_cond])])
                elif col_cond == 4 or col_cond == 5:
                    row.append(EXCHANGE_RATE_LIST[convert2to10_in_list(individual[col_cond])])
                else:
                    row.append(OWN_SHIP_LIST[convert2to10_in_list(individual[col_cond])])
            for col_act in range(DEFAULT_NUM_OF_ACTION):
                row.append(individual[DEFAULT_NUM_OF_CONDITION*2+col_act])
            row.append(individual[-1][0])
            row.append(individual[-1][1])
            writer.writerow(row)

def load_generated_sinario():
    all_data = []
    for i in range(4):
        if i == 0:
            history_data_path = '../output/oil_price.csv'
        elif i == 1:
            history_data_path = '../output/freight_outward.csv'
        elif i == 2:
            history_data_path = '../output/freight_return.csv'
        elif i == 3:
            history_data_path = '../output/exchange_rate.csv'


        # read data
        dt   = np.dtype({'names': ('date', 'price'),
                       'formats': ('S10' , np.float)})
        data = np.array([], dtype=dt)
        for j in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            data = np.append(data,np.genfromtxt(history_data_path,
                             delimiter=',',
                             dtype=dt,
                             usecols=[2*j,2*j+1],
                             skip_header=0,
                             encoding='utf-8_sig'))
        data = data.reshape(DEFAULT_PREDICT_PATTERN_NUMBER,VESSEL_LIFE_TIME*12)
        all_data.append(data)
    return all_data

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

def depict_scenario(oil,freight_outward,freight_return,exchange):
    list1 = [oil,freight_outward,freight_return,exchange]
    list2 = ['oil price','freight_outward','freight_return','exchange_rate']
    for (data, name) in zip(list1,list2):
        x = range(oil.predict_years*12)
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            y = []
            for time in range(data.predict_years*12):
                y.append(data.predicted_data[pattern][time]['price'])
            plt.plot(x, y)#,label='pattern {}'.format(pattern+1))
        plt.title('Transition of {}'.format(name), fontsize = 20)
        plt.xlabel('month', fontsize = 16)
        plt.ylabel(name, fontsize = 16)
        plt.grid(True)
        plt.ylim(0, 160)
        save_dir = '../output'
        plt.savefig(os.path.join(save_dir, '{}.png'.format(name)))
        plt.close()

def depict_whole_scenario(oil,freight_outward,exchange):
    list1 = [oil,freight_outward,exchange]
    list2 = ['oil price','freight_outward','exchange_rate']
    for (data, name) in zip(list1,list2):
        orignal_length = len(data.history_data)
        x = range(VESSEL_LIFE_TIME*12+orignal_length)
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            y = []
            for time in range(180+num):
                if time < orignal_length:
                    y.append(data.history_data[time][1])
                else:
                    y.append(data.predicted_data[pattern][time-num]['price'])
            plt.plot(x, y)#,label='pattern {0}'.format(pattern+1))
        plt.title('Transition of {}'.format(name), fontsize = 20)
        plt.xlabel('month', fontsize = 16)
        plt.ylabel(name, fontsize = 16)
        plt.grid(True)
        plt.xlim(0,600)
        plt.ylim(0, 160)
        save_dir = '../output'
        plt.savefig(os.path.join(save_dir, '{}_scenario_whole_time.png'.format(name)))
        plt.close()

def depict_distribution(oil,freight_outward,exchange):
    list1 = [oil,freight_outward,exchange]
    list2 = ['oil price','freight_outward','exchange_rate']
    list3 = [OIL_PRICE_LIST,FREIGHT_RATE_LIST,EXCHANGE_RATE_LIST]
    for (data, name, list) in zip(list1,list2,list3):
        distribution = [0]*16
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            for time in range(VESSEL_LIFE_TIME * 12):
                value = data[pattern][time]['price']
                for i in range(16):
                    if i == 15:
                        if list[i] < value:
                            distribution[i] += 1
                    else:
                        if list[i] < value and value < list[i+1]:
                            distribution[i] += 1
        for index in range(len(distribution)):
            distribution[index] = distribution[index]/(DEFAULT_PREDICT_PATTERN_NUMBER*180.0)
        left = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        label = list
        plt.title('{} distribution'.format(name))
        plt.xlabel(name)
        plt.ylabel('Propability')
        plt.bar(left,distribution,tick_label=label,align='center')
        save_dir = '../output'
        plt.savefig(os.path.join(save_dir, '{}_distribution.png'.format(name)))
        plt.close()
