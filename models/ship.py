class Ship:
    def __init__(self, size, speed, route):
        self.size = size
        self.speed = speed# km/h
        self.route = route

    def calculate_income_per_month(self,oil_price):
        time_spent_to_one_trip = self.route/(self.speed * 24)
        number_of_trips = 365 / time_spent_to_one_trip
        balance = 8
        income_in_one_trip = self.size * 1600 / balance
        #1600doller/TEU http://www.jpmac.or.jp/relation/trend_graph/26_1_1.pdf
        cost_in_one_trip = self.route * self.change_dollers_per_Barrels_to_dollers_per_kg(oil_price) * self.calculate_fuel_consumption_from_speed()
        return (income_in_one_trip - cost_in_one_trip) * number_of_trips

    def change_speed(self,speed):
        self.speed = speed if speed > 18 else 18

    def calculate_fuel_consumption_from_speed(self):
        DWT = 10.8 * self.size + 12400
        DSP = 1.37 * DWT + 1660
        k_c0 = 6.87 * 10**(-5)
        k_c1 = 0.65
        LF = 0.8
        FO = self.speed*self.speed*k_c0*(DSP-DWT+k_c1*LF*DWT)*DSP**(-1/3)
        return FO #kg/km
        #http://www.nilim.go.jp/lab/bcg/siryou/tnn/tnn0494pdf/ks049404.pdf

    def change_dollers_per_Barrels_to_dollers_per_kg(self,oil_price):
        return oil_price / 135
        #1barrels = 135kg
