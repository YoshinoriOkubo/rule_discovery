import numpy as np

class WorldScale:
    def __init__(self, history_data=None, neu=None, sigma=None, u=None, d=None, p=None, alpha=None, beta=None):
        self.default_xlabel = "date".title()
        self.default_ylabel = "world scale".title() + " [USD]"
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
