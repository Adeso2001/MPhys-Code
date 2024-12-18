# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 16:15:03 2024

@author: Oliver
"""

import numpy as np
import matplotlib.pyplot as plt

data1 = np.genfromtxt("liquid nitrogen test 1.csv", skip_header=1,
                      delimiter =',')

data1[:,0] = data1[:,0] - data1[0,0]

time = (data1[:,0])
chanel = data1[:,1]
voltage = data1[:,2]

i=0
v=0
data_temp = data1
ch0_time = np.array([])
ch1_time = np.array([])
ch2_time = np.array([])
ch3_time = np.array([])
ch0_voltage = np.array([])
ch1_voltage = np.array([])
ch2_voltage = np.array([])
ch3_voltage = np.array([])

for chanel_no in chanel:
    if chanel_no == 0:
        ch0_time = np.append(ch0_time, data_temp[v,0])
        ch0_voltage = np.append(ch0_voltage, data_temp[v,2])
    elif chanel_no == 1:
        ch1_time = np.append(ch1_time, data_temp[v,0])
        ch1_voltage = np.append(ch1_voltage, data_temp[v,2])
    elif chanel_no == 2:
        ch2_time = np.append(ch2_time, data_temp[v,0])
        ch2_voltage = np.append(ch2_voltage, data_temp[v,2])
    elif chanel_no == 3:
        ch3_time = np.append(ch3_time, data_temp[v,0])
        ch3_voltage = np.append(ch3_voltage, data_temp[v,2])
    v+=1
    
ch0_time1 = ch0_time
ch1_time1 = ch1_time
ch2_time1 = ch2_time
ch3_time1 = ch3_time
ch0_voltage1 = ch0_voltage
ch1_voltage1 = ch1_voltage
ch2_voltage1 = ch2_voltage
ch3_voltage1 = ch3_voltage

data2 = np.genfromtxt("liquid nitrogen with calibrated diode longer.csv", skip_header=1,
                      delimiter =',')

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

for chanel_no in chanel:
    if chanel_no == 0:
        ch0_time = np.append(ch0_time, data_temp[v,0])
        ch0_voltage = np.append(ch0_voltage, data_temp[v,2])
    elif chanel_no == 1:
        ch1_time = np.append(ch1_time, data_temp[v,0])
        ch1_voltage = np.append(ch1_voltage, data_temp[v,2])
    elif chanel_no == 2:
        ch2_time = np.append(ch2_time, data_temp[v,0])
        ch2_voltage = np.append(ch2_voltage, data_temp[v,2])
    elif chanel_no == 3:
        ch3_time = np.append(ch3_time, data_temp[v,0])
        ch3_voltage = np.append(ch3_voltage, data_temp[v,2])
    v+=1
    
ch0_time2 = ch0_time
ch1_time2 = ch1_time
ch2_time2 = ch2_time
ch3_time2 = ch3_time
ch0_voltage2 = ch0_voltage
ch1_voltage2 = ch1_voltage
ch2_voltage2 = ch2_voltage
ch3_voltage2 = ch3_voltage

#===============================================

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage (V)")
ax.set_title("Liquid nitrogen test 1")
#ax.set_xlim([0,data1[-1,0]])
ax.set_xlim([0,700])
ax.set_ylim([0,1.2])

ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)

ax.plot(ch0_time1,ch0_voltage1,color = "Tab:blue",alpha = 0.7, linewidth = 1,
        label = "channel 0")
ax.plot(ch1_time1,ch1_voltage1,color = "Tab:red",alpha = 0.7, linewidth = 1,
        label = "channel 1")
ax.plot(ch2_time1,ch2_voltage1,color = "Tab:green",alpha = 0.7, linewidth = 1,
        label = "channel 2")
ax.plot(ch3_time1,ch3_voltage1,color = "Tab:gray",alpha = 0.7, linewidth = 1,
        label = "channel 3")
ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("Liquid N2 voltageTime 1.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

#===============================================

output_figure2 = plt.figure(0)
ax = output_figure2.add_subplot(111)


ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage (V)")
ax.set_title("Liquid Nitrogen Test 2 (with calibrated diode)")
#ax.set_xlim([0,data2[-1,0]])
ax.set_xlim([0,2500])
ax.set_ylim([0.5,1.1])


ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)

ax.plot(ch0_time2,ch0_voltage2,color = "Tab:blue",alpha = 0.7, linewidth = 1,
        label = "channel 0")
#ax.plot(ch1_time2,ch1_voltage2,color = "Tab:red",alpha = 0.7, linewidth = 1,
#        label = "channel 1")
ax.plot(ch2_time2,ch2_voltage2,color = "Tab:green",alpha = 0.7, linewidth = 1,
        label = "channel 2 (Calibrated)")
ax.plot(ch3_time2,ch3_voltage2,color = "Tab:gray",alpha = 0.7, linewidth = 1,
        label = "channel 3")
ax.legend()

output_figure2.tight_layout()
output_figure2.savefig("liquid N2 voltageTime 2 (w calibrated).png",dpi = 1000, 
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure2)




    