# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 19:01:50 2024

@author: Oliver
"""

import numpy as np
import matplotlib.pyplot as plt
import Omega_fit2 as of

test = 6
if test == 4:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp 10-75 117-5 better DAQ.csv"
elif test == 5:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp 10-75 117-5 better DAQ 2.csv"
elif test == 6:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp 10-75 117-5 better DAQ 3.csv"
elif test == 7:
    file_name = "blowing test (2 peaks at end).csv"

data2 = np.genfromtxt(file_name, delimiter = ',',
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
        ch2_voltage = np.append(ch2_voltage, data_temp[v,2])
        ch0_temperature = np.append(ch0_temperature, data_temp[v,3])
    elif chanel_no == 1:
        ch1_time = np.append(ch1_time, data_temp[v,0])
        ch1_voltage = np.append(ch1_voltage, data_temp[v,2])
        ch1_temperature = np.append(ch1_temperature, data_temp[v,3])
    elif chanel_no == 2:
        ch2_time = np.append(ch2_time, data_temp[v,0])
        ch0_voltage = np.append(ch0_voltage, data_temp[v,2])
        ch2_temperature = np.append(ch2_temperature, data_temp[v,3])
    elif chanel_no == 3:
        ch3_time = np.append(ch3_time, data_temp[v,0])
        ch3_voltage = np.append(ch3_voltage, data_temp[v,2])
        ch3_temperature = np.append(ch3_temperature, data_temp[v,3])
    v+=1
    
#-------------

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(211)
bx = output_figure1.add_subplot(212)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Current (μA)")
ax.set_title("IT offset (stycasted LM and transistor)")
#ax.set_xlim(0,800)

bx.set_xlabel("Time (s)")
bx.set_ylabel("Temperature (°K)")
#bx.set_xlim(0,800)


ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)
bx.grid(True, color='grey', dashes=(4, 2), zorder = 0)

ch0_current = (ch0_voltage/478500) * (10**6)

ax.plot(ch0_time,ch0_current,
           label = "Current", zorder = 3,linewidth = 0.6, color = 'black')
bx.plot(ch0_time,ch1_temperature,
           label = "Transistor temperature", zorder = 3,linewidth = 1)

#ax.plot(ch0_time,ch2_voltage,
#           label = "IN4002 diode", zorder = 3, alpha = 0.7)

ax.legend()
bx.legend()

output_figure1.tight_layout()
output_figure1.savefig(f"week 8 lm334 and transistor offset test CURRENT {test}.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

#-------------------------------------------------------

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_xlabel("Temperature (°K)")
ax.set_ylabel("Current (μA)")
ax.set_title("IT graph for LM334 + diode generator (heat up + cool down)")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)


#ax.scatter(temperature,ch0_voltage, marker = '.', s = 5,
#           label = "LM334", zorder = 3, alpha = 0.7)
ax.scatter(ch1_temperature,ch0_current, marker = 'x', s = 10,
           label = "I across 470KΩ resistor", zorder = 2,
           color = 'black')

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig(f"week 8 lm334 and transistor offset test {test} IT hot+cold.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

#-------------------------------------------------------

ch1_temperature_slice = ch1_temperature[1350:]
ch0_voltage_slice = ch0_voltage[1350:]
ch0_current_slice = ch0_current[1350:]

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_xlabel("Temperature (°K)")
ax.set_ylabel("Current (μA)")
ax.set_title("IT graph for LM334 + diode generator (cool down)")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)


#ax.scatter(temperature,ch0_voltage, marker = '.', s = 5,
#           label = "LM334", zorder = 3, alpha = 0.7)
ax.scatter(ch1_temperature_slice,
           ch0_current_slice
           , marker = 'x', s = 10,
           label = "I across 478KΩ resistor", zorder = 2,
           color = 'black')

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig(f"week 8 lm334 and transistor offset test {test} IT cold.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

def compute_average_temperature_and_uncertainty(voltages, temperatures, z_score_threshold=3, min_points=3):
    """
    Computes the average temperature and uncertainty (standard deviation) for each unique voltage,
    excluding temperature outliers based on the z-score method and ignoring voltages with too few points.

    Parameters:
    - voltages: List or numpy array of voltage measurements.
    - temperatures: List or numpy array of temperature measurements corresponding to voltages.
    - z_score_threshold: The number of standard deviations away from the mean a temperature must be
                          to be considered an outlier.
    - min_points: The minimum number of data points required for a voltage to be considered (exclude otherwise).

    Returns:
    - A 2D numpy array with columns [voltage, average_temperature, uncertainty] for each unique voltage.
      Uncertainty is computed as the standard deviation of the filtered temperatures.
    """
    # Initialize a dictionary to store temperatures corresponding to each voltage
    voltage_to_temperatures = {}

    # Group temperatures by corresponding voltage
    for voltage, temp in zip(voltages, temperatures):
        if voltage not in voltage_to_temperatures:
            voltage_to_temperatures[voltage] = []
        voltage_to_temperatures[voltage].append(temp)

    # List to store the final results
    results = []

    # For each unique voltage, process the temperature data
    for voltage, temps in voltage_to_temperatures.items():
        # Skip voltage if it has fewer than the minimum number of points
        if len(temps) < min_points:
            continue
        
        # Calculate the mean and standard deviation of temperatures for this voltage
        mean_temp = np.mean(temps)
        std_temp = np.std(temps)

        # Identify and exclude outlier temperatures using the z-score method
        filtered_temps = []
        
        if len(temps) > 2:  # Only filter outliers if there are more than 2 data points
            for temp in temps:
                z_score = (temp - mean_temp) / std_temp if std_temp != 0 else 0  # Avoid division by zero
                if abs(z_score) <= z_score_threshold:
                    filtered_temps.append(temp)
        else:
            # If there are only two or fewer data points, no filtering
            filtered_temps = temps
        
        # If after filtering there are not enough points, skip this voltage
        if len(filtered_temps) < min_points:
            continue
        
        # Calculate the average of the filtered temperatures
        avg_temp = np.mean(filtered_temps)

        # Calculate the uncertainty (standard deviation) of the filtered temperatures
        uncertainty = np.std(filtered_temps)

        # Append the results (voltage, avg_temp, and uncertainty)
        results.append([voltage, avg_temp, uncertainty])
    
    # Convert the results list to a 2D numpy array
    results_array = np.array(results)
    
    return results_array

VT_array = compute_average_temperature_and_uncertainty(ch1_temperature_slice, ch0_voltage_slice)


sorted_temp = VT_array[:,0]
sorted_voltage = VT_array[:,1]
sorted_current = (sorted_voltage/478500) * (10 ** 6)
sorted_voltage_unc = VT_array[:,2]/2
sorted_current_unc = (sorted_voltage_unc/478500) * (10 ** 6)

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_ylabel("Current (μA)")
ax.set_xlabel("Temperature (°K)")
ax.set_title(f"IT graph for IN4002 + LM334 combo trial {test}")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)

ax.scatter(sorted_temp,
           sorted_current,
           marker = 'x', s = 10,
           label = "I across 478KΩ resistor", zorder = 2,
           color = 'black')
ax.errorbar(sorted_temp,
           sorted_current,
           yerr = sorted_current_unc,
           fmt = 'x',
           markersize = 0,
           ecolor = 'red',
           zorder = 1,
           elinewidth = 1)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig(f"Wk 8 IT graph transistor IN4002 + LM334 Sorted {test}.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

of.fit(sorted_temp,sorted_current,
       sorted_current_unc, fit_type = 0,
       initial_guess = (0,0),
       graph_xlabel = "Temperature (°K)",
       graph_ylabel = "Current (μA)",
       graph_filename = f"IN4002 + LM334 straight line fit test {test}",
       function_returns = False,
       graph_legend = False,
       graph_title = f"IN4002 + LM334 straight line fit {test}")
