# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 09:28:56 2020

@author: Lnofeisone
"""

from BSM_options import BSM_call_value
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['font.family'] = 'serif'

# Model and Option Parameters
S0 = 6
K = 5  # strike price
T = 3  # time-to-maturity
r = 0.01  # constant, riskless short term rate
vol = .48  # constant volatility

option_value = BSM_call_value(S0, K, T, r, vol)
print("Option Value: ", round(option_value, 3))

# Sample Data Generation
S = np.linspace(1, 10, 150)  # vector of index level values
h = np.maximum(S - K, 0)  # inner value of option
C = [BSM_call_value(S0, K, T, r, vol) for S0 in S]
# calculate call option values

# Graphical Output
plt.figure()
plt.plot(S, h, 'b-.', lw=2.5, label='intrinsic value')
# plot intrinsic value
plt.plot(S, C, 'r', lw=2.5, label='present value')
# plot option present value
plt.grid(True)
plt.legend(loc=0)
plt.xlabel('index level $S_0$')
plt.ylabel('present value $C(t=0)$')
