import numpy as np
from scipy import stats
from scipy.stats import brunnermunzel
'''
A = np.array([277,	272,	309,	320,	217,  320.1])
B = np.array([229,	218,	229,	199,	225,  253])
print(stats.mannwhitneyu(A, B,alternative='greater'))
A = np.array([277,	272,	309,	320,	  320.1])
B = np.array([218,	229,  253])
print(stats.mannwhitneyu(A, B,alternative='greater'))
'''
'''
A = np.array([2727,2888,2632,2835])
B = np.array([2101,2180,2113,2093])
print(stats.mannwhitneyu(A, B,alternative='greater'))
print(stats.mannwhitneyu(A, B,alternative='two-sided'))
'''
A = [2.85,2.88,2.63,2.83]
B = [2.10,2.18,2.11,2.09]
'''
#print(brunnermunzel(a, b))
A_var = np.var(A, ddof=1)  # Aの不偏分散
B_var = np.var(B, ddof=1)  # Bの不偏分散
A_df = len(A) - 1  # Aの自由度
B_df = len(B) - 1  # Bの自由度
f = A_var / B_var  # F比の値
one_sided_pval1 = stats.f.cdf(f, A_df, B_df)  # 片側検定のp値 1
one_sided_pval2 = stats.f.sf(f, A_df, B_df)   # 片側検定のp値 2
two_sided_pval = min(one_sided_pval1, one_sided_pval2) * 2  # 両側検定のp値

print('F:       ', round(f, 3))
#print(stats.ttest_rel(A, B))
#print(stats.ttest_ind(A, B))
#print('p-value: ', round(one_sided_pval1, 3))
#print('p-value: ', round(one_sided_pval2, 3))
3print('p-value: ', round(two_sided_pval, 3))
'''
print(stats.ttest_ind(A, B, equal_var=False))

'''
A = np.array([1.566,	1.357,	1.415,	1.498,	0.714,  1.500])
B = np.array([1.056,	0.529,	1.080,	0.818,	0.826,  0.892])
print(stats.mannwhitneyu(A, B,alternative='greater'))
'''