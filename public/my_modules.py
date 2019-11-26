import calendar as cal
import numpy as np
import datetime
import os
import csv
import matplotlib.pyplot as plt
import statistics
from constants import *

def convert2to10_in_list(list):
    result = 0
    length = len(list)
    for i in range(len(list)):
        x = length - 1 - i
        result += list[i] * 2 ** (x)
    if len(list) == 1:
        return result
    elif len(list) == 2:
        return GRAY_CODE_2[result]
    elif len(list) == 3:
        return GRAY_CODE_3[result]
    elif len(list) == 4:
        return GRAY_CODE_4[result]
    else:
        return None

def export_rules_integrate_csv(list):
    path = '../output/rule-discovered/rule.csv'
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['a','b','c','d','e','f','g','h'])
    with open(path, 'a') as f:
        writer = csv.writer(f)
        for index in range(len(list)):
            individual = list[index]
            for block in range(3):
                row = []
                if block == 2:
                    row.append(individual[block][0])
                    row.append(individual[block][1])
                else:
                    for col_cond in range(DEFAULT_NUM_OF_CONDITION*2):
                        if col_cond == 0 or col_cond == 1:
                            row.append(OIL_PRICE_LIST[convert2to10_in_list(individual[block][col_cond])])
                        elif col_cond == 2 or col_cond == 3:
                            row.append(FREIGHT_RATE_LIST[convert2to10_in_list(individual[block][col_cond])])
                        elif col_cond == 4 or col_cond == 5:
                            row.append(EXCHANGE_RATE_LIST[convert2to10_in_list(individual[block][col_cond])])
                        else:
                            row.append(OWN_SHIP_LIST[convert2to10_in_list(individual[block][col_cond])])
                writer.writerow(row)

def export_rules_csv(list,one=None):
    if one is None:
        path = '../output/rule-discovered/ship_rule.csv'
    else:
        path = '../output/rule-discovered/ship_one_rule.csv'
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['a','b','c','d','e','f','g','h','i','j','k','l','m','expectation','variance'])
    with open(path, 'a') as f:
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
    for name in ['oil_price','freight_outward','freight_return','exchange_rate','demand','supply']:
        history_data_path = '../output/scenario/{}.csv'.format(name)
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
        data = data.reshape(DEFAULT_PREDICT_PATTERN_NUMBER,DEFAULT_PREDICT_YEARS*12)
        all_data.append(data)
    return all_data

def load_history_data(unit,type,direction=None,from_date=None, to_date=None):
    if unit == MONTH:
        name = 'monthly'
    elif unit == YEAR:
        name = 'yearly'

    if type == OIL_TYPE:
        history_data_path = '../data/crude_oil_{}.csv'.format(name)
    elif type == FREIGHT_TYPE:
        if direction == OUTWARD:
            history_data_path = '../data/freight_rate_outward_{}.csv'.format(name)
        elif direction == RETURN:
            history_data_path = '../data/freight_rate_return_{}.csv'.format(name)
        elif direction == CCFI:
            history_data_path = '../data/ccfi_{}.csv'.format(name)
        else:
            raise Exception('freight type error!')
    elif type == EXCHANGE_TYPE:
        history_data_path = '../data/exchange_rate_{}.csv'.format(name)
    elif type == DEMAND_TYPE:
        history_data_path = '../data/ship_demand_{}.csv'.format(name)
    elif type == SUPPLY_TYPE:
        history_data_path = '../data/ship_supply_{}.csv'.format(name)
    elif type == NEWSHIPMARKET_TYPE:
        history_data_path = '../data/new_ship_price_{}.csv'.format(name)
    elif type == SECONDHAND_TYPE:
        history_data_path = '../data/secondhand_ship_price_{}.csv'.format(name)
    else:
        raise Exception('type error')

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

def export_binomial_parameter(oil,exchange,demand):
    path = '../output/scenario/paramater.csv'
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['type', 'mu', 'sigma', 'u', 'd', 'p'])
    with open(path, 'a') as f:
        writer = csv.writer(f)
        list1 = [oil,exchange,demand]
        list2 = ['oil price', 'exchange rate', 'ship demand']
        for data, name in zip(list1,list2) :
            row = []
            row.append(name)
            row.append(data.neu)
            row.append(data.sigma)
            row.append(data.u)
            row.append(data.d)
            row.append(data.p)
            writer.writerow(row)

def export_statistical_feature(oil,freight_outward,freight_return,exchange,demand,supply,new_ship,secondhand_ship):
    #export mean, variance, stdev,median, minimum, maximum, mean with barrier
    list1 = [oil,freight_outward,freight_return,exchange,demand,supply,new_ship,secondhand_ship]
    list2 = ['oil_price','freight_outward','freight_return','exchange_rate','ship_demand','ship_supply','new_ship','secondhand_ship']
    list3 = [0,0,0,0,0,0,0,0]
    list4 = [150,2000,2000,250,20,10000,150*10**6,150*10**6]
    statistical_feature = []
    number = 0
    for type,name,down,up in zip(list1,list2,list3,list4):
        statistical_feature.append({})
        data = []
        data_modifyed = []
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            for time in range(DEFAULT_PREDICT_YEARS * 12):
                data.append(type.predicted_data[pattern][time]['price'])
                if type.predicted_data[pattern][time]['price'] < up:
                    data_modifyed.append(type.predicted_data[pattern][time]['price'])
        dictionary_data = statistical_feature[number]
        dictionary_data['mean'] = statistics.mean(data)
        dictionary_data['variance'] = statistics.variance(data)
        dictionary_data['stdev'] = statistics.stdev(data)
        dictionary_data['median'] = statistics.median(data)
        dictionary_data['min'] = min(data)
        dictionary_data['max'] = max(data)
        number += 1
    path = '../output/scenario/statistics.csv'
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'mean', 'variance', 'stdev', 'median', 'min', 'max'])
    with open(path, 'a') as f:
        writer = csv.writer(f)
        for index in range(len(statistical_feature)):
            statistics_data = statistical_feature[index]
            name = list2[index]
            row = []
            row.append(name)
            row.append(statistics_data['mean'])
            row.append(statistics_data['variance'])
            row.append(statistics_data['stdev'])
            row.append(statistics_data['median'])
            row.append(statistics_data['min'])
            row.append(statistics_data['max'])
            writer.writerow(row)

def export_scenario_csv(oil,freight_outward,freight_return,exchange,demand,supply,new_ship,secondhand_ship):
    list1 = [oil,freight_outward,freight_return,exchange,demand,supply,new_ship,secondhand_ship]
    list2 = ['oil_price','freight_outward','freight_return','exchange_rate','demand','supply','new_ship','secondhand_ship']
    for (data, name) in zip(list1,list2):
        path = '../output/scenario/{}.csv'.format(name)
        with open(path, 'w') as f:
            pass
        with open(path, 'a') as f:
            writer = csv.writer(f)
            for time in range(DEFAULT_PREDICT_YEARS*12):
                row = []
                for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
                    row.append(data.predicted_data[pattern][time]['date'])
                    row.append(data.predicted_data[pattern][time]['price'])
                writer.writerow(row)

def depict_scenario(oil,freight_outward,freight_return,exchange,demand,supply,new_ship,secondhand_ship):
    list1 = [oil,freight_outward,freight_return,exchange,demand,supply,new_ship,secondhand_ship]
    list2 = ['oil_price','freight_outward','freight_return','exchange_rate','ship_demand','ship_supply','new_ship','secondhand_ship']
    down = [0,0,0,0,0,0,0,0]
    up = [200,4000,4000,250,30,10000,150*10**6,150*10**6]
    for (data, name,d,u) in zip(list1,list2,down,up):
        x = range(data.predict_years*12)
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            y = []
            for time in range(data.predict_years*12):
                y.append(data.predicted_data[pattern][time]['price'])
            plt.plot(x, y)#,label='pattern {}'.format(pattern+1))
        plt.title('Transition of {}'.format(name), fontsize = 20)
        plt.xlabel('month', fontsize = 16)
        plt.ylabel(name, fontsize = 16)
        plt.ylim(d,u)
        plt.grid(True)
        save_dir = '../output/image'
        plt.savefig(os.path.join(save_dir, '{}.png'.format(name)))
        plt.close()

def depict_whole_scenario(oil,freight_outward,freight_return,exchange,demand,supply,new_ship,secondhand_ship):
    list1 = [oil,freight_outward,freight_return,exchange,demand,supply,new_ship,secondhand_ship]
    list2 = ['oil_price','freight_outward','freight_return','exchange_rate','ship_demand','ship_supply','new_ship','secondhand_ship']
    down = [0,0,0,0,0,0,0,0]
    up = [200,6834.62314,2000,250,20,10000,150*10**6,150*10**6]
    for (data, name, d, u) in zip(list1,list2,down,up):
        orignal_length = len(data.monthly_history_data)
        length_sum = DEFAULT_PREDICT_YEARS*12+orignal_length
        x = range(length_sum)
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            y = []
            for time in range(length_sum):
                if time < orignal_length:
                    y.append(data.monthly_history_data[time]['price'])
                else:
                    y.append(data.predicted_data[pattern][time-orignal_length]['price'])
            plt.plot(x, y)
        plt.title('Transition of {}'.format(name), fontsize = 20)
        plt.xlabel('month', fontsize = 16)
        plt.ylabel(name, fontsize = 16)
        plt.ylim(d,u)
        plt.grid(True)
        save_dir = '../output/image'
        plt.savefig(os.path.join(save_dir, '{}_scenario_whole_time.png'.format(name)))
        plt.close()

def depict_distribution(oil,freight_outward,freight_return,exchange,demand,supply,new_ship,secondhand_ship):
    list1 = [oil,freight_outward,freight_return,exchange,demand,supply,new_ship,secondhand_ship]
    list2 = ['oil_price','freight_outward','freight_return','exchange_rate','ship_demand','ship_supply','new_ship','secondhand_ship']
    list3 = [0,0,0,0,0,0,0,0]
    list4 = [150,4000,2000,250,20,10000,150*10**6,150*10**6]
    for type,name,down,up in zip(list1,list2,list3,list4):
        data = []
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            for time in range(DEFAULT_PREDICT_YEARS * 12):
                data.append(type.predicted_data[pattern][time]['price'])
        plt.hist(data,bins=20,range=(down, up))
        plt.xlabel('{} value'.format(name))
        plt.ylabel('Frequency')
        plt.title('{} value in generated scenario'.format(name))
        save_dir = '../output/image'
        plt.savefig(os.path.join(save_dir, '{}_distribution.png'.format(name)))
        plt.close()
