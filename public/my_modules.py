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

def export_dictionary(dic):
    path = '../output/rule-discovered/dictionary.csv'
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['key','profit','variance'])
    with open(path, 'a') as f:
        writer = csv.writer(f)
        for k, v in dic.items():
            row = []
            row.append('a'+str(k))
            row.append(v[0])
            row.append(v[1])
            writer.writerow(row)


def export_rules_integrate_csv(list,number=None):
    if number is None:
        path = '../output/rule-discovered/rule.csv'
    else:
        path = '../output/rule-discovered/rule_at_{}.csv'.format(number)
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['a','b','c','d','e','f','g','h','i','j'])
    with open(path, 'a') as f:
        writer = csv.writer(f)
        for index in range(len(list)):
            individual = list[index]
            for block in range(DEFAULT_NUM_OF_ACTION_INTEGRATE+1):
                row = []
                if block == DEFAULT_NUM_OF_ACTION_INTEGRATE:
                    row.append(individual[block][0])
                    row.append(individual[block][1])
                else:
                    rule = individual[block]
                    for col_cond in range(DEFAULT_NUM_OF_CONDITION):
                        condition_type = CONVERT_LIST[col_cond]
                        lower = condition_type[convert2to10_in_list(rule[col_cond*2])]
                        upper = condition_type[convert2to10_in_list(rule[col_cond*2+1])]
                        row.append(lower)
                        row.append(upper)
                writer.writerow(row)

def export_rules_csv(list,one=None):
    if one is None:
        path = '../output/rule-discovered/ship_rule.csv'
    else:
        path = '../output/rule-discovered/ship_one_rule.csv'
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','expectation','variance'])
    with open(path, 'a') as f:
        writer = csv.writer(f)
        for index in range(len(list)):
            row = []
            individual = list[index]
            for col_cond in range(DEFAULT_NUM_OF_CONDITION*2):
                if col_cond == 0 or col_cond == 1:
                    row.append(OIL_PRICE_LIST[convert2to10_in_list(individual[col_cond])])
                elif col_cond == 2 or col_cond == 3 or col_cond == 8 or col_cond ==9:
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

def load_generated_sinario(sign=TRAIN_DATA_SET):
    all_data = []
    for name in ['oil_price','freight_outward','freight_homeward','exchange_rate','demand','supply','new_ship','secondhand_ship']:
        history_data_path = '../output/{0}/scenario/{1}.csv'.format(sign,name)
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
        elif direction == HOMEWARD:
            history_data_path = '../data/freight_rate_homeward_{}.csv'.format(name)
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

def export_binomial_parameter(sign,oil,exchange,demand):
    path = '../output/{}/scenario/paramater.csv'.format(sign)
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

def export_statistical_feature(sign,oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship):
    #export mean, variance, stdev,median, minimum, maximum, mean with barrier
    list1 = [oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship]
    list2 = ['oil_price','freight_outward','freight_homeward','exchange_rate','ship_demand','ship_supply','new_ship','secondhand_ship']
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
    path = '../output/{}/scenario/statistics.csv'.format(sign)
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

def export_scenario_csv(sign,oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship):
    list1 = [oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship]
    list2 = ['oil_price','freight_outward','freight_homeward','exchange_rate','demand','supply','new_ship','secondhand_ship']
    for (data, name) in zip(list1,list2):
        path = '../output/{0}/scenario/{1}.csv'.format(sign,name)
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

def depict_scenario(sign,oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship):
    list1 = [oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship]
    list2 = ['oil price','freight outward','freight homeward','exchange rate','ship demand','ship supply','new ship','secondhand ship']
    down = [0,0,0,0,0,0,0,0]
    unit1 = ['($/barrel)','($/TEU)','($/TEU)','(JPY/$)','','(ships)','($)','($)']
    up = [200,2500,1500,250,250,10000,150*10**6,150*10**6]
    for (data, name,d,u,unit) in zip(list1,list2,down,up,unit1):
        x = range(data.predict_years*12)
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            y = []
            for time in range(data.predict_years*12):
                y.append(data.predicted_data[pattern][time]['price'])
            plt.plot(x, y)#,label='pattern {}'.format(pattern+1))
        #plt.title('Transition of {}'.format(name), fontsize = 20)
        plt.xlabel('month', fontsize = 10)
        plt.ylabel('{0} {1}'.format(name,unit), fontsize = 10)
        plt.ylim(d,u)
        #plt.grid(True)
        save_dir = '../output/{}/image'.format(sign)
        plt.savefig(os.path.join(save_dir, '{}.png'.format(name)))
        plt.close()

def depict_whole_scenario(sign,oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship):
    list1 = [oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship]
    list2 = ['oil price','freight outward','freight homeward','exchange rate','ship demand','ship supply','new ship','secondhand ship']
    down = [0,0,0,0,0,0,0,0]
    unit1 = ['($/barrel)','($/TEU)','($/TEU)','(JPY/$)','','(ships)','($)','($)']
    up = [200,2500,1500,250,250,10000,150*10**6,150*10**6]
    for (data, name, d, u,unit) in zip(list1,list2,down,up,unit1):
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
        #plt.title('Transition of {}'.format(name), fontsize = 20)
        plt.xlabel('month', fontsize = 10)
        plt.ylabel('{0} {1}'.format(name,unit), fontsize = 10)
        plt.ylim(d,u)
        #plt.grid(True)
        save_dir = '../output/{}/image'.format(sign)
        plt.savefig(os.path.join(save_dir, '{}_scenario_whole_time.png'.format(name)))
        plt.close()

def depict_distribution(sign,oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship):
    list1 = [oil,freight_outward,freight_homeward,exchange,demand,supply,new_ship,secondhand_ship]
    list2 = ['oil price','freight outward','freight homeward','exchange rate','ship demand','ship supply','new ship price','secondhand ship price']
    unit1 = ['($/barrel)','($/TEU)','($/TEU)','(JPY/$)','','(ships)','($)','($)']
    list3 = [0,0,0,0,0,0,0,0]
    list4 = [150,2500,1500,250,200,10000,150*10**6,150*10**6]
    for type,name,down,up, unit in zip(list1,list2,list3,list4,unit1):
        data = []
        for pattern in range(DEFAULT_PREDICT_PATTERN_NUMBER):
            for time in range(DEFAULT_PREDICT_YEARS * 12):
                data.append(type.predicted_data[pattern][time]['price'])
        plt.hist(data,bins=20,range=(down, up))
        plt.xlabel('{0} {1}'.format(name,unit), fontsize = 10)
        plt.ylabel('Frequency', fontsize = 10)
        #plt.title('{} value in generated scenario'.format(name))
        save_dir = '../output/{}/image'.format(sign)
        plt.savefig(os.path.join(save_dir, '{}_distribution.png'.format(name)))
        plt.close()
