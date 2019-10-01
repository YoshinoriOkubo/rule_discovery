import numpy as np

class FlatRate:
    def __init__(self, history_data=None, neu=None, sigma=None, u=None, d=None, p=None):

        if history_data is None:
            self.history_data = load_flat_rate_history_data()
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
        for date, flat_rate in self.history_data:
            if index == 0:
                # initialize the rate
                s_0 = flat_rate
            else:
                s_t      = flat_rate
                base_val = math.log(s_t / s_0)
                values   = np.append(values, base_val)
                # update the price
                s_0      = flat_rate
            index += 1

        # substitute inf to nan in values
        values     = inf_to_nan_in_array(values)
        self.neu   = np.nanmean(values)
        self.sigma = np.nanstd(values)
        self.u     = np.exp(self.sigma * np.sqrt(delta_t))
        self.d     = np.exp(self.sigma * (-1) * np.sqrt(delta_t))
        self.p     = 0.5 + 0.5 * (self.neu / self.sigma) * np.sqrt(delta_t)
        return

    # generate predicted sinario
    def generate_flat_rate(self, sinario_mode, predict_years=DEFAULT_PREDICT_YEARS):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years

        # predicted data type
        dt   = np.dtype({'names': ('date', 'fr'),
                         'formats': ('S10' , np.float)})
        self.predicted_data = np.array([], dtype=dt)

        # latest date from history_data
        latest_history_date_str, latest_flatrate = self.history_data[-1]
        latest_history_date                      = datetime.datetime.strptime(latest_history_date_str, '%Y/%m/%d')

        end_date         = add_year(latest_history_date, predict_years)
        current_date     = latest_history_date
        current_flatrate = latest_flatrate
        while end_date > current_date:
            current_date    += datetime.timedelta(days=1)
            current_date_str = datetime.datetime.strftime(current_date, '%Y/%m/%d')

            # change by mode
            if sinario_mode == DERIVE_SINARIO_MODE['high']:
                current_flatrate = None
            elif sinario_mode == DERIVE_SINARIO_MODE['low']:
                current_flatrate = None
            elif sinario_mode == DERIVE_SINARIO_MODE['maintain']:
                current_flatrate = current_flatrate
            else:
                current_flatrate = self.calc_flatrate(current_flatrate)
            self.predicted_data = np.append(self.predicted_data, np.array([(current_date_str, current_flatrate)], dtype=dt))

        return


    def calc_flatrate(self, current_flatrate):
        return self.u * current_flatrate if prob(self.p) else self.d * current_flatrate


    '''
    # generate predicted sinario
    def generate_significant_flat_rate(self, sinario_mode, significant_flat_rate=None, predict_years=DEFAULT_PREDICT_YEARS):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years

        # predicted data type
        dt   = np.dtype({'names': ('date', 'fr'),
                         'formats': ('S10' , np.float)})
        self.predicted_data = np.array([], dtype=dt)

        predict_days_num = self.predict_years * 365
        # latest date from history_data
        latest_history_date_str, latest_flatrate = self.history_data[-1]
        latest_history_date                      = datetime.datetime.strptime(latest_history_date_str, '%Y/%m/%d')

        end_date         = add_year(latest_history_date, predict_years)
        current_date     = latest_history_date
        current_flatrate = latest_flatrate
        if isinstance(significant_flat_rate, list):
            xlist = np.array([0, predict_days_num])
            tlist = np.array(significant_flat_rate)
            wlist = estimate(xlist, tlist, 1)
            significant_flat_rate_array = {index: calc_y(index, wlist, 1) for index in range(predict_days_num)}

        day_index = 0
        while end_date > current_date:
            current_date    += datetime.timedelta(days=1)
            current_date_str = datetime.datetime.strftime(current_date, '%Y/%m/%d')
            # change by mode
            if sinario_mode == 'medium':
                current_flatrate = current_flatrate
            elif sinario_mode == 'oilprice_dec' or sinario_mode == 'oilprice_inc':
                if significant_flat_rate[0] == significant_flat_rate[1]:
                    current_flatrate = significant_flat_rate[1]
                else:
                    current_flatrate = round(significant_flat_rate_array[day_index], 3)
            else:
                current_flatrate = significant_flat_rate
            self.predicted_data = np.append(self.predicted_data, np.array([(current_date_str, current_flatrate)], dtype=dt))
            day_index += 1
        return

    '''
