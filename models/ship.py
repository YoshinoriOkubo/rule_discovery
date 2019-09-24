class ship:

    def __init__(self, size, fuel_consumption, route):
        self.size = size
        self.fuel_consumption = fuel_consumption
        self.roule = route
        self.income = 0

    def calculate_income(fligth_rate, oil_price):
        self.income = size * fligth_rate - self.fuel_consumption * self.route * oil_price
