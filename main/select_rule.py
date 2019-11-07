import csv
import sys
import random
sys.path.append('../public')
from my_modules import *
from constants  import *

def load_ship_rules():
    path = '../output/ship_rule.csv'
    rule = []
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != 'a':
                list = []
                for element in range(len(row)):
                    list.append(float(row[element]))
                rule.append(list)
    return rule

def select_rules(rule,oil,freight,exchange,own_ship):
    max_fitness = -10
    result = None
    for one in rule:
        if adapt_rule(oil,freight,exchange,own_ship,one):
            if max_fitness < one[-2] or (max_fitness == one[-2] and random.randint(0,1) < 0.5):
                result = one
                max_fitness = one[-2]
            else:
                pass
    return result

def adapt_rule(oil_price,freight,exchange,own_ship,rule):
    actionlist = rule[8:14]
    a,b = rule[0],rule[1]
    if a == b or ( a <= oil_price and oil_price <= b):
        c,d = rule[2],rule[3]
        if c == d or ( c <= freight and freight <= d):
            e,f = rule[4],rule[5]
            if e == f or (e <= exchange and exchange <= f):
                g,h = rule[6],rule[7]
                if g == h or (g <= own_ship and own_ship <= h):
                    return True
    return False

def main():
    rule = load_ship_rules()
    #given variables
    oil = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    freight = int(sys.argv[2]) if len(sys.argv) > 2 else 800
    exchange = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    own_ship = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    print(select_rules(rule,oil,freight,exchange,own_ship))

if __name__ == "__main__":
    main()
