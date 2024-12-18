# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 19:19:46 2024

@author: Oliver
"""

import numpy as np
import matplotlib.pyplot as plt


data2 = np.genfromtxt("noise reduction 19-11-24.csv", delimiter = ',',
                         skip_header = 1)

data2[:,0] = data2[:,0] - data2[0,0]

time = data2[:,0]
chanel = data2[:,1]
voltage = data2[:,2]

i=0
v=0
data_temp = data2
ch0_time = np.array([])
ch1_time = np.array([])
ch2_time = np.array([])
ch3_time = np.array([])
ch0_voltage = np.array([])
ch1_voltage = np.array([])
ch2_voltage = np.array([])
ch3_voltage = np.array([])
ch0_temperature = np.array([])
ch1_temperature = np.array([])
ch2_temperature = np.array([])
ch3_temperature = np.array([])

for chanel_no in chanel:
    if chanel_no == 0:
        ch0_time = np.append(ch0_time, data_temp[v,0])
        ch0_voltage = np.append(ch0_voltage, data_temp[v,2])
        ch0_temperature = np.append(ch0_temperature, data_temp[v,3])
    elif chanel_no == 1:
        ch1_time = np.append(ch1_time, data_temp[v,0])
        ch1_voltage = np.append(ch1_voltage, data_temp[v,2])
        ch1_temperature = np.append(ch1_temperature, data_temp[v,3])
    elif chanel_no == 2:
        ch2_time = np.append(ch2_time, data_temp[v,0])
        ch2_voltage = np.append(ch2_voltage, data_temp[v,2])
        ch2_temperature = np.append(ch2_temperature, data_temp[v,3])
    elif chanel_no == 3:
        ch3_time = np.append(ch3_time, data_temp[v,0])
        ch3_voltage = np.append(ch3_voltage, data_temp[v,2])
        ch3_temperature = np.append(ch3_temperature, data_temp[v,3])
    v+=1


output_figure = plt.figure(0)
ax1 = output_figure.add_subplot(111)
ax1.grid(True, color='grey', dashes=(4, 2), zorder = 0)
ax1.plot(ch0_time,ch2_voltage)
ax1.set_xlim((0,95))
ax1.set_ylim((4.76,4.83))



plt.show()
plt.close(output_figure)

#====================================================

output_figure = plt.figure(0)
ax1 = output_figure.add_subplot(111)
ax1.grid(True, color='grey', dashes=(4, 2), zorder = 0)
ax1.plot(ch0_time,ch2_voltage)
ax1.set_xlim((0,22))
ax1.set_ylim((4.76,4.83))

ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Voltage (V)")
ax1.set_title("No noise reduction")

output_figure.tight_layout()
output_figure.savefig("no_noise_reduction_20-11-24.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure)


#=====================================================

slice_val=116
output_time = ch0_time[slice_val:] 
output_time = output_time - output_time[0]
output_voltage = ch2_voltage[slice_val:]

output_figure = plt.figure(0)
ax1 = output_figure.add_subplot(111)
ax1.grid(True, color='grey', dashes=(4, 2), zorder = 0)
ax1.plot(output_time,output_voltage )
ax1.set_xlim((0,15))
ax1.set_ylim((4.76,4.83))

ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Voltage (V)")
ax1.set_title("Capacitors used for noise reduction")

output_figure.tight_layout()
output_figure.savefig("capacitor_noise_reduction_20-11-24.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure)

#=====================================================

slice_val=198
output_time = ch0_time[slice_val:] 
output_time = output_time - output_time[0]
output_voltage = ch2_voltage[slice_val:]

output_figure = plt.figure(0)
ax1 = output_figure.add_subplot(111)
ax1.grid(True, color='grey', dashes=(4, 2), zorder = 0)
ax1.plot(output_time,output_voltage )
ax1.set_xlim((0,15))
ax1.set_ylim((4.76,4.83))

ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Voltage (V)")
ax1.set_title("Capacitors and Oscillosocpe used for noise reduction")

output_figure.tight_layout()
output_figure.savefig("capacitor_oscilloscope_noise_reduction_20-11-24.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure)


#=====================================================

slice_val=300
output_time = ch0_time[slice_val:] 
output_time = output_time - output_time[0]
output_voltage = ch2_voltage[slice_val:]

output_figure = plt.figure(0)
ax1 = output_figure.add_subplot(111)
ax1.grid(True, color='grey', dashes=(4, 2), zorder = 0)
ax1.plot(output_time,output_voltage )
ax1.set_xlim((0,20))
ax1.set_ylim((4.76,4.83))

ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Voltage (V)")
ax1.set_title("Oscillosocpe used for noise reduction")

output_figure.tight_layout()
output_figure.savefig("oscilloscope_noise_reduction_20-11-24.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure)

