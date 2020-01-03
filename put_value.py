# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 20:34:59 2020

@author: Lnofeisone
"""

from BSM_options import BSM_put_value
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['font.family'] = 'serif'

# Model and Option Parameters
S0 = 7
K = 5  # strike price
T = 3  # time-to-maturity
r = 0.01  # constant, riskless short term rate
vol = .48  # constant volatility

option_value = BSM_put_value(S0, K, T, r, vol)
print("Option Value: ", round(option_value, 3))

# Sample Data Generation
S = np.linspace(1, 10, 150)  # vector of index level values
h = np.maximum(K-S, 0)  # inner value of option

# calculate call and put option values
P = [BSM_put_value(S0, K, T, r, vol) for S0 in S]


# Graphical Output
plt.figure()
plt.plot(S, h, 'b-.', lw=2.5, label='intrinsic value')
# plot intrinsic value
plt.plot(S, P, 'r', lw=2.5, label='present value')
# plot option present value
plt.grid(True)
plt.legend(loc=0)
plt.xlabel('index level $S_0$')
plt.ylabel('present value $C(t=0)$')