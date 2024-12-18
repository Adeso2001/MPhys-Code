# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 14:26:23 2024

@author: Oliver
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import e,k

def diode_eq(V,T):
    I_s = (10**-7)
    return ((10**-7) * (np.exp((e*V)/(k*T)) - 1))

v_array = np.linspace(-0.5,0.1,9999)
I_300 = diode_eq(v_array,300)
I_300 = I_300 * 10 ** 6
I_200 = diode_eq(v_array,200)
I_200 = I_200 * 10 ** 6
I_100 = diode_eq(v_array,100)
I_100 = I_100 * 10 ** 6
I_50 = diode_eq(v_array,50)
I_50 = I_50 * 10 ** 6

fig = plt.figure(0)
ax = fig.add_subplot(111)
ax.grid(
    True, color='grey', dashes=(4, 2), zorder = 0)

ax.plot(v_array,I_300,linewidth = 0.8,label = "300K")
ax.plot(v_array,I_200,linewidth = 0.8,label = "200K")
ax.plot(v_array,I_100,linewidth = 0.8,label = "100K")
ax.plot(v_array,I_50,linewidth = 0.8,label = "50K")

plt.legend()
ax.set_ylabel("Current (μA)")
ax.set_xlabel("Voltage (V)")
ax.plot([0,0],[-1,2], color = 'black',linewidth = 0.5)
ax.plot([-1,1],[0,0], color = 'black',linewidth = 0.5)
ax.set_ylim([-0.2,1.2])
ax.set_xlim([-0.1,0.1])
fig.tight_layout()

plt.savefig("diodeIV.png",dpi=200)