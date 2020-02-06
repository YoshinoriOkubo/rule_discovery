import numpy as np
from scipy import stats
A = [2.85,2.88,2.63,2.83]
B = [2.10,2.18,2.11,2.09]
print(stats.ttest_ind(A, B, equal_var=False))