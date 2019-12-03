# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 11:08:18 2019

@author: aleks ontman
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['font.family'] = 'serif'

#Option Strike

k = 3000

#Graphical Output
S = np.linspace(2000,5000, 100) #index level values
h = np.maximum(S-k, 0) #inner values of call option

plt.figure()
plt.plot(S, h, lw=2.5)
plt.xlabel('index level $S_t$ at maturity')
plt.ylabel('inner value of European call option')
plt.grid(True)