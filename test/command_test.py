import subprocess
import time

start = time.time()
'''
print('pattern 1 speed will start')
cmd = "python3 ga.py 1"
subprocess.call(cmd.split(),cwd = "../models")
'''
'''
print('pattern 2 sell will start')
cmd = "python3 ga.py 2"
subprocess.call(cmd.split(),cwd = "../models")
'''

print('pattern 3 charter out will start')
cmd = "python3 ga.py 3"
subprocess.call(cmd.split(),cwd = "../models")

'''
print('pattern 4 charter in will start')
cmd = "python3 ga.py 4"
subprocess.call(cmd.split(),cwd = "../models")
'''
'''
print('pattern 5 integrate will start')
cmd = "python3 ga.py 5"
subprocess.call(cmd.split(),cwd = "../models")
'''
print(time.time()-start)
