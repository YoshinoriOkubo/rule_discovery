import numpy as np

class WorldScale:
    def __init__(self, history_data=None, neu=None, sigma=None, u=None, d=None, p=None, alpha=None, beta=None):
        self.history_data   = load_world_scale_history_data() if history_data is None else history_data
        # initialize parameters
        if (neu is None or sigma is None or u is None or d is None or p is None or alpha is None or beta is None):
            self.calc_params_from_history()
        else:
            self.neu, self.sigma, self.u, self.d, self.p, self.alpha, self.beta = neu, sigma, u, d, p, alpha, beta

    # calc neu and sigma from history data
    def calc_params_from_history(self):
        index   = 0
        delta_t = 1.0 / 12
        values  = np.array([])
        for date, world_scale in self.history_data:
            if index == 0:
                # initialize the price
                s_0 = world_scale
            else:
                s_t      = world_scale
                base_val = math.log(s_t / s_0)
                values   = np.append(values, base_val)
                # update the price
                s_0      = world_scale
            index += 1

        # substitute inf to nan in values
        values = inf_to_nan_in_array(values)

        #[WIP] calc alpha and beta
        alpha = 0.1932
        beta  = 6.713

        self.neu    = np.nanmean(values)
        self.sigma  = np.nanstd(values)
        self.u      = np.exp(self.sigma * np.sqrt(delta_t))
        self.d      = np.exp(self.sigma * (-1) * np.sqrt(delta_t))
        self.p      = 0.5 + 0.5 * (self.neu / self.sigma) * np.sqrt(delta_t)
        self.alpha, self.beta = alpha, beta
        return
        
    # generate predicted sinario
    def generate_sinario(self, sinario_mode, predict_years=DEFAULT_PREDICT_YEARS):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years

        # predicted data type
        dt   = np.dtype({'names': ('date', 'ws'),
                         'formats': ('S10' , np.float)})
        self.predicted_data = np.array([], dtype=dt)

        predict_months_num = self.predict_years * 12

        # latest date from history_data
        latest_history_date_str, latest_ws = self.history_data[-1]
        latest_history_date                = datetime.datetime.strptime(latest_history_date_str, '%Y/%m/%d')

        current_date = latest_history_date
        current_ws   = latest_ws
        for predict_month_num in range(predict_months_num):
            current_date     = add_month(current_date)
            current_date_str = datetime.datetime.strftime(current_date, '%Y/%m/%d')

            # change ws by mode
            if sinario_mode == DERIVE_SINARIO_MODE['high']:
                current_ws = None
            elif sinario_mode == DERIVE_SINARIO_MODE['low']:
                current_ws = None
            elif sinario_mode == DERIVE_SINARIO_MODE['maintain']:
                current_ws = current_ws
            else:
                current_ws = self.calc_ws(current_ws)

            # change ws by mode
            self.predicted_data = np.append(self.predicted_data, np.array([(current_date_str, round(current_ws, 4))], dtype=dt))

        return
    '''
    # generate predicted sinario
    def generate_significant_sinario(self, sinario_mode, significant_world_scale=None, predict_years=DEFAULT_PREDICT_YEARS):
        # default predict_years is 15 years [180 months]
        self.predict_years  = predict_years

        # predicted data type
        dt   = np.dtype({'names': ('date', 'ws'),
                         'formats': ('S10' , np.float)})
        self.predicted_data = np.array([], dtype=dt)

        predict_months_num = self.predict_years * 12

        # latest date from history_data
        latest_history_date_str, latest_ws = self.history_data[-1]
        latest_history_date                = datetime.datetime.strptime(latest_history_date_str, '%Y/%m/%d')

        current_date = latest_history_date
        current_ws   = latest_ws
        if isinstance(significant_world_scale, list):
            xlist = np.array([0, predict_months_num])
            tlist = np.array(significant_world_scale)
            wlist = estimate(xlist, tlist, 1)
            significant_world_scale_array = {index: calc_y(index, wlist, 1) for index in range(predict_months_num)}
        for predict_month_num in range(predict_months_num):
            current_date     = add_month(current_date)
            current_date_str = datetime.datetime.strftime(current_date, '%Y/%m/%d')

            # change ws by mode
            if sinario_mode == 'medium':
                current_ws = current_ws
            elif sinario_mode == 'oilprice_dec' or sinario_mode == 'oilprice_inc':
                current_ws = round(significant_world_scale_array[predict_month_num], 3)
            else:
                current_ws = significant_world_scale

            # change ws by mode
            self.predicted_data = np.append(self.predicted_data, np.array([(current_date_str, round(current_ws, 4))], dtype=dt))

        return
    '''

    # generate world scale scenario with oil price correlation
    def generate_sinario_with_oil_corr(self, sinario_mode, latest_oilprice_history_data, oilprice_predicted_data):
        if sinario_mode == DERIVE_SINARIO_MODE['maintain']:
            self.generate_sinario(sinario_mode)
            return

        # predicted data type
        dt   = np.dtype({'names':   ('date', 'ws'),
                         'formats': ('S10' , np.float)})
        self.predicted_data = np.array([], dtype=dt)

        previous_month, previous_oilprice    = latest_oilprice_history_data
        previous_month, previous_world_scale = self.history_data[-1]
        for predict_month, predicted_oilprice in oilprice_predicted_data:
            change_rate           = calc_change_rate(previous_oilprice, predicted_oilprice)
            predicted_world_scale = self.calc_ws(previous_world_scale * (1.0 - change_rate))
            previous_month, previous_oilprice    = predict_month, predicted_oilprice
            previous_month, previous_world_scale = predict_month, predicted_world_scale
            self.predicted_data = np.append(self.predicted_data, np.array([(predict_month, round(predicted_world_scale, 4))], dtype=dt))
        return

    def calc_ws(self, current_ws):
        return self.u * current_ws if prob(self.p) else self.d * current_ws

    def calc_ws_with_oilprice(self, oilprice):
        return (self.alpha * oilprice + self.beta)
