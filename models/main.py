import ship
import ga
import uncertain

ship = []
num_ship = 5
for i in range(num_seed):
    ship.append(ship(100,100,10000))

period = 100
flatRate = FlatRate(period)

do_ga(ship,uncertain)
