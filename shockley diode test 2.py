# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 21:07:02 2024

@author: Oliver
"""

import numpy as np
import matplotlib.pyplot as plt


data = [
    [1, 0.09058, 500.0],
    [2, 0.11251, 490.0],
    [3, 0.13545, 480.0],
    [4, 0.18275, 460.0],
    [5, 0.27852, 420.0],
    [6, 0.38485, 375.0],
    [7, 0.50182, 325.0],
    [8, 0.58272, 290.0],
    [9, 0.65102, 260.0],
    [10, 0.71815, 230.0],
    [11, 0.77295, 205.0],
    [12, 0.82665, 180.0],
    [13, 0.86857, 160.0],
    [14, 0.90950, 140.0],
    [15, 0.94909, 120.0],
    [16, 0.97769, 105.0],
    [17, 1.00531, 90.0],
    [18, 1.03172, 75.0],
    [19, 1.05692, 60.0],
    [20, 1.08274, 44.0],
    [21, 1.09382, 37.0],
    [22, 1.10242, 32.0],
    [23, 1.10822, 29.0],
    [24, 1.11277, 27.0],
    [25, 1.11566, 26.0],
    [26, 1.11945, 25.0],
    [27, 1.12592, 24.0],
    [28, 1.14082, 23.0],
    [29, 1.16280, 22.0],
    [30, 1.18155, 21.0],
    [31, 1.26752, 15.5],
    [32, 1.31316, 13.0],
    [33, 1.36969, 10.5],
    [34, 1.44226, 8.0],
    [35, 1.57312, 4.4],
    [36, 1.61799, 2.8],
    [37, 1.64059, 1.7],
    [38, 1.64421, 1.4]
]

def calculate_reverse_bias(T_0,I_0,T):
    boltzman = 8.617333262*10**(-5)
    Eg = 1.14
    term1 = I_0 * ((T/T_0) ** 3 )
    term2 = np.exp((Eg / boltzman) * (1/T_0 - 1/T))
    I_s = np.multiply(term1 , term2)
    return I_s

def calculate_voltage(ideality,T,I_D,I_0,T_0):
    boltzman = 1.380649*10**(-23)
    boltzman_ev = 8.617333262*10**(-5)
    q = 1.6 * 10 ** -19
    Eg = 1.14
    if T>20:
        boltzman = 1.380649*10**(-23)
        Is = calculate_reverse_bias(T_0,I_0,T)
        print(Is)
        q = 1.6 * 10 ** -19
        prefactor = (ideality * boltzman * T) / q
        log_term = np.log(np.multiply(I_D,(1/Is)) + 1)
        voltage = prefactor * log_term
    else:
        voltage = (ideality * boltzman * (T / q)) * (
            np.log(I_D) - np.log(I_0 * ((T/T_0)**3)) - (
                (Eg / boltzman_ev) * (1/T_0 - 1/T)))
    
    return voltage
    #return Is


ideal = 1
is_bc = (100 * (90 ** -9))

ideal = 1.05
is_bc = (100 * (80 ** -9))

ideal = 1.012
is_bc = (100 * (85 ** -9))

temp_array = np.linspace(0.1,500,9999)
hahaha = np.array([])
for temp in temp_array:
    
    voltage_array = calculate_voltage(ideal , temp, (10 ** -6), is_bc, 298)
    hahaha = np.append(hahaha,voltage_array)

# Convert to a numpy array
new_fig = plt.figure(0)
ax1 = new_fig.add_subplot(111)

ax1.set_ylabel("Voltage (V)")
ax1.set_xlabel("Temperature (°K)")

ax1.set_xlim([1,500])

array = np.array(data)
#
voltage = array[:,1]
temperature = array[:,2]

plt.rcParams.update({'font.size': 14})

ax1.grid(True, color='grey', dashes=(4, 2), zorder = 0)

ax1.plot(temperature,voltage,linewidth = 2,label = "DT-670 Data",alpha = 0.6)
ax1.plot(temp_array,hahaha,linewidth = 2,label = "Equation Simulated Data",alpha = 0.6)

ax1.set_xscale('log')

ax1.legend()
new_fig.tight_layout()
new_fig.savefig("simulated voltage current report",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(new_fig)

#-------------------------------------------------------------------------
def calculate_current(T,T_0,I_0,V,ideality):
    boltzman = 1.380649*10**(-23)
    boltzman_ev = 8.617333262*10**(-5)
    q = 1.6 * 10 ** -19
    Is = calculate_reverse_bias(T_0, I_0, T)
    current = Is * (np.exp((q * V)/(ideality*boltzman*T)) - 1)
    print(Is)
    return current
#is_bc = 1 * (10 ** -6)
voltage_array_20 = np.linspace(0,1.23,9999)
voltage_array_100 = np.linspace(0,6.19,9999)
voltage_array_300 = np.linspace(0,18.5,9999)
current_20 = calculate_current(20, 298, is_bc, voltage_array_20, ideal) * (10 ** 6)
current_100 = calculate_current(100, 298, is_bc, voltage_array_100, ideal) * (10 ** 6)
current_300 = calculate_current(300, 298, is_bc, voltage_array_300, ideal) * (10 ** 6)



new_fig = plt.figure(0)
ax1 = new_fig.add_subplot(111)

ax1.set_xlabel("Voltage (V)")
ax1.set_ylabel("Current (µA)")
ax1.set_ylim([-5,100])
ax1.set_xlim([0,1.3])

#ax1.set_yscale('log')
#ax1.set_ylim([(10**-30),100])

ax1.grid(True, color='grey', dashes=(4, 2), zorder = 0)

ax1.plot(voltage_array_20,current_20,linewidth = 2,label = "20°K current",alpha = 0.6)
ax1.plot(voltage_array_100,current_100,linewidth = 2,label = "100°K current",alpha = 0.6)
ax1.plot(voltage_array_300,current_300,linewidth = 2,label = "300°K current",alpha = 0.6)

ax1.legend()
new_fig.tight_layout()
new_fig.savefig("simulated temp voltage report",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(new_fig)