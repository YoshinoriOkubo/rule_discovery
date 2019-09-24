class Oilprice:
    def __init__(self, history_data=None, neu=None, sigma=None, u=None, d=None, p=None):
        self.default_xlabel = "date".title()
        self.default_ylabel = "flat rate".title() + " [%]"
        if history_data is None:
            self.history_data = load_flat_rate_history_data()
            self.draw_history_data()
        else:
            self.history_data = history_data
        # initialize parameters
        if (neu is None or sigma is None or u is None or d is None or p is None):
            self.calc_params_from_history()
        else:
            self.neu, self.sigma, self.u, self.d, self.p = neu, sigma, u, d, p
