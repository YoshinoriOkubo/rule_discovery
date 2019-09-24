import random
import copy
import time
first = time.time()
lifecycle = 15

def do_ga(ship,uncertain):
    pass

def market(x):
    d = x + random.randint(-1,1)
    return min(max(d,0),15)

def convert2to10(a,b,c,d):
    return a*8 + b*4 + c*2 + d

def fitness_funxtion():
    pass

def crossing(a,b,point1,point2):
    #for exapmle, a = ['1','2','2',...,'3']
    temp1 = []
    temp2 = []
    if point1 > point2:
        point1,point2 = point2,point1
    for i in range(0,point1):
        temp1.append(a[i])
        temp2.append(b[i])
    for i in range(point1,point2):
        temp1.append(b[i])
        temp2.append(a[i])
    for i in range(point2,len(a)):
        temp1.append(a[i])
        temp2.append(b[i])
    return [temp1,temp2]

def mutation(individual):
    x = random.randint(0,8)
    if x == 8:
        individual[x] = random.randint(0,5)
    else:
        individual[x] = random.randint(0,1)
    return individual


#def exchange(rule):
#    newRule = []
#    for i in range(0,4):
#        newRule.append(rule[i+4])
#    for i in range(0,4):
#        newRule.append(rule[i])
#    for i in range(0,2):
#        newRule.append(rule[i+8])
#    return newRule

def generateIndividual():
    temp = []
    for j in range(8):
        temp.append(random.randint(0,1))
    temp.append(random.randint(0,5))
    temp.append(0)
    return temp

generation = 100 # the number of generation
group = [] # group that has individual
num = 2000  # the number of individual
demand = [5] # market demand that determines  which function is more efficient
ark = 0 # the number used to roulette in crossing
alpha = 0.05 # the rate of mutation

#randomly generating individual group
for i in range(num):
    group.append(generateIndividual())

#randomly generating market demand
for i in range(1,generation):
    demand.append(market(demand[i-1]))

#genetic algorithm
for gene in range(generation):
    print('{}%完了'.format(gene*100.0/generation))
    #crossing
    temp = copy.deepcopy(group)
    for i in range(0,num,2):
        a,b = crossing(temp[i],temp[i+1],random.randint(0,9),random.randint(0,9))
        temp.append(a)
        temp.append(b)

    #mutation
    for individual in temp:
        if random.random() < alpha:
            individual = mutation(individual)

    #rule check
    for k in range(len(temp)):
        rule = temp[k]
        lower = convert2to10(rule[0],rule[1],rule[2],rule[3])
        upper = convert2to10(rule[4],rule[5],rule[6],rule[7])
        if lower > upper:
            temp[k] = exchange(rule)

    #computation of fitness
    for one in range(len(temp)):
        rule = temp[one]
        rule[9] = fitness(rule,demand)

    #reduce the number of individual
    num -= 10

    #selection
    probability = 0
    for i in range(len(temp)):
        probability += temp[i][9]
    roulette = 0
    for i in range(num):
        roulette = random.randint(0,probability)
        while roulette > 0:
            roulette -= temp[ark][9]
            ark = (ark + 1) % num
        group[i] = temp[ark]

#print result
group.sort(key=lambda x:x[9],reverse = True)
for i in range(0,1):
    thisone = group[i]
    a = convert2to10(thisone[0],thisone[1],thisone[2],thisone[3])
    b = convert2to10(thisone[4],thisone[5],thisone[6],thisone[7])
    order = translate(thisone[8])
    #if thisone[9] > 400:
    print('0<demand<{0} -> function{1} \n{0}<demand<{2} -> function{3} \n{2}<demand<15 -> function{4}  \n score = {5}'.format(a,order[0],b,order[1],order[2],thisone[9]))
print('finish')
exe = time.time() - first
print('Spent time is {0}'.format(exe))
