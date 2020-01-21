import numpy as np
from scipy import stats
A = np.array([1.566,	1.357,	1.415,	1.498,	0.714,  1.500])
B = np.array([1.056,	0.529,	1.080,	0.818,	0.826,  0.892])
print(stats.mannwhitneyu(A, B,alternative='greater'))

'''
A = np.array([1.57,	1.36,	1.41,	1.50,])
B = np.array([1.06,	0.529,	1.08,	0.818,	0.827,])
print(stats.mannwhitneyu(A, B,alternative='greater'))
'''