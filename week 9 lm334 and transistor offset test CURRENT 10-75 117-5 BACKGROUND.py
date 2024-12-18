# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 19:01:50 2024

@author: Oliver
"""

import numpy as np
import matplotlib.pyplot as plt
import Omega_fit2 as of

test = 9
if test == 4:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp 10-75 117-5 better DAQ.csv"
elif test == 5:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp 10-75 117-5 better DAQ 2.csv"
elif test == 6:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp 10-75 117-5 better DAQ 3.csv"
elif test == 7:
    file_name = "blowing test (2 peaks at end).csv"
elif test == 8:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp wk9.csv"
elif test == 9:
    file_name = "28-11-24 reading.csv"
elif test == 10:
    file_name = "28-11-24 reading.csv"

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
ch4_time = np.array([])
ch5_time = np.array([])
ch6_time = np.array([])
ch0_voltage = np.array([])
ch1_voltage = np.array([])
ch2_voltage = np.array([])
ch3_voltage = np.array([])
ch4_voltage = np.array([])
ch5_voltage = np.array([])
ch6_voltage = np.array([])
ch0_temperature = np.array([])
ch1_temperature = np.array([])
ch2_temperature = np.array([])
ch3_temperature = np.array([])
ch4_temperature = np.array([])
ch5_temperature = np.array([])
ch6_temperature = np.array([])

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
    elif chanel_no == 5:
        ch5_time = np.append(ch5_time, data_temp[v,0])
        ch5_voltage = np.append(ch5_voltage, data_temp[v,2])
        ch5_temperature = np.append(ch5_temperature, data_temp[v,3])
    elif chanel_no == 4:
        ch4_time = np.append(ch4_time, data_temp[v,0])
        ch4_voltage = np.append(ch4_voltage, data_temp[v,2])
        ch4_temperature = np.append(ch4_temperature, data_temp[v,3])
    elif chanel_no == 6:
        ch6_time = np.append(ch6_time, data_temp[v,0])
        ch6_voltage = np.append(ch6_voltage, data_temp[v,2])
        ch6_temperature = np.append(ch6_temperature, data_temp[v,3])
    v+=1


if test == 8: 
    ch1_temperature= ch5_temperature
    ch0_voltage= ch6_voltage

if test == 9: 
    ch1_temperature= ch6_temperature
    ch0_voltage= ch4_voltage
    

def string_to_numpy_array(input_string):
    # Split the string by whitespace and filter out empty strings
    number_strings = input_string.split()
    
    # Convert the list of strings to a numpy array of floats (or ints)
    numbers_array = np.array([float(num) for num in number_strings])
    
    return numbers_array

def get_info_after_colon_trimmed(input_string):
    # Find the index of the first colon
    colon_index = input_string.find(':')
    
    # Check if a colon was found
    if colon_index != -1:
        # Extract everything after the colon
        info_after_colon = input_string[colon_index + 1:]
        # Remove spaces immediately after the colon
        return info_after_colon.lstrip()  # This removes leading spaces only
    else:
        return "No colon found in the string."

data = np.genfromtxt("BC568 high t calibration2.330", dtype = 'str', delimiter = ',')
number_strings = data[7:]

#if test == 9:
#    data = np.genfromtxt("LM334 470k calibration 121124.330", dtype = 'str', delimiter = ',')

data_array = np.zeros((0,3),dtype = 'float')

for data_entry in number_strings:
    temp_data_array = np.array([[0.,0.,0.]] )
    temp_numpy_array = string_to_numpy_array(data_entry)
    temp_data_array[0] = temp_numpy_array
    data_array = np.vstack((data_array,temp_data_array))

sensor_model = get_info_after_colon_trimmed(data[0])
serial_number = get_info_after_colon_trimmed(data[1])
interpolation_method = get_info_after_colon_trimmed(data[2])
setpoint_limit = get_info_after_colon_trimmed(data[3])
data_format = get_info_after_colon_trimmed(data[4])
no_breakpoints = get_info_after_colon_trimmed(data[5])
units = str(data[6])

header_tuple = (sensor_model,serial_number,interpolation_method,
                setpoint_limit,data_format,no_breakpoints,units)

counter = 0
dummy_voltage = 0.0
previous_v = 0
previous_t = 0
temperature = []


calibration_data_current = data_array
voltage_values = calibration_data_current[:, 1]
temperature_values = calibration_data_current[:, 2]

for voltage_measurement in ch6_voltage:
    counter += 1
    #print(voltage_measurement)
    if counter % 100 == 0:
        print(f"{counter} of {len(ch1_voltage)}")
        
    if voltage_measurement == previous_v:
        temperature.append(previous_t)
    else:
        # Use searchsorted to find the appropriate index
        i = np.searchsorted(voltage_values, voltage_measurement)
        
        if i == 0:
            # Handle case where measurement is below the first calibration point
            # Extrapolate using the gradient between the first two points
            voltage_before = voltage_values[0]
            voltage_after = voltage_values[1]
            temp_before = temperature_values[0]
            temp_after = temperature_values[1]
            
            gradient = (temp_after - temp_before) / (voltage_after - voltage_before)
            temperature_temp = temp_before + gradient * (voltage_measurement - voltage_before)
        
        elif i >= len(calibration_data_current):
            # Handle case where measurement is above the last calibration point
            # Extrapolate using the gradient between the last two points
            voltage_before = voltage_values[-2]
            voltage_after = voltage_values[-1]
            temp_before = temperature_values[-2]
            temp_after = temperature_values[-1]
            
            gradient = (temp_after - temp_before) / (voltage_after - voltage_before)
            temperature_temp = temp_before + gradient * (voltage_measurement - voltage_before)
        
        else:
            # Interpolate between breakpoints to find temperature
            temp_before = temperature_values[i - 1]
            temp_after = temperature_values[i]
            voltage_before = voltage_values[i - 1]
            voltage_after = voltage_values[i]
            
            temperature_temp = temp_before + (temp_after - temp_before) * (voltage_measurement - voltage_before) / (voltage_after - voltage_before)
        
        #print(temperature_temp)
        temperature.append(temperature_temp)
        previous_t = temperature_temp
        previous_v = voltage_measurement

    
#-------------

#ch1_temperature = temperature

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
if test == 9:
    ch0_current = (ch0_voltage/473200) * (10**6)
if test == 10:
    ch0_current = (ch5_voltage/478500) * (10**6)
ax.plot(ch0_time,ch0_current,
           label = "Current", zorder = 3,linewidth = 0.6, color = 'black')
#bx.plot(ch0_time,ch1_temperature,
#           label = "Transistor temperature", zorder = 3,linewidth = 1)
bx.plot(ch0_time,temperature,
           label = "Transistor temperature", zorder = 3,linewidth = 1)

#ax.plot(ch0_time,ch2_voltage,
#           label = "IN4002 diode", zorder = 3, alpha = 0.7)

ax.legend()
bx.legend()

output_figure1.tight_layout()
#output_figure1.savefig(f"week 9 lm334 and transistor offset test CURRENT {test}.png",dpi = 1000,
#                       bbox_inches = "tight")

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
#ax.scatter(ch1_temperature,ch0_current, marker = 'x', s = 10,
#           label = "I across 470KΩ resistor", zorder = 2,
#           color = 'black')
ax.scatter(temperature,ch0_current, marker = 'x', s = 10,
           label = "I across 470KΩ resistor", zorder = 2,
           color = 'black')

ax.legend()

output_figure1.tight_layout()
#output_figure1.savefig(f"week 9 lm334 and transistor offset test {test} IT hot+cold.png",dpi = 1000,
#                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

#-------------------------------------------------------

#ch1_temperature_slice = ch1_temperature[1075:8175]
ch1_temperature_slice = temperature[1075:8175]
ch0_voltage_slice = ch0_voltage[1075:8175]
ch5_voltage_slice = ch5_voltage[1075:8175]
ch0_current_slice = ch0_current[1075:8175]

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
#output_figure1.savefig(f"week 9 lm334 and transistor offset test {test} IT cold.png",dpi = 1000,
#                       bbox_inches = "tight")

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
if test == 10:
    VT_array = compute_average_temperature_and_uncertainty(ch1_temperature_slice, ch5_voltage_slice)


sorted_temp = VT_array[:,0]
sorted_voltage = VT_array[:,1]
sorted_current = (sorted_voltage/478500) * (10 ** 6)
sorted_voltage_unc = VT_array[:,2]/2
sorted_current_unc = (sorted_voltage_unc/478500) * (10 ** 6)

if test == 9 :
    sorted_temp = VT_array[:,0]
    sorted_voltage = VT_array[:,1]
    sorted_current = (sorted_voltage/473200) * (10 ** 6)
    sorted_voltage_unc = VT_array[:,2]/2
    sorted_current_unc = (sorted_voltage_unc/473200) * (10 ** 6)

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
#output_figure1.savefig(f"Wk 9 IT graph transistor IN4002 + LM334 Sorted {test}.png",dpi = 1000,
#                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

sorted_current_unc = sorted_current_unc
pos = np.where(sorted_current_unc == 0)

sorted_temp = np.delete(sorted_temp,pos)
sorted_current = np.delete(sorted_current,pos)
sorted_current_unc = np.delete(sorted_current_unc,pos)
    
test_9_sorted_temp = sorted_temp
test_9_sorted_current = sorted_current
test_9_sorted_current_unc = sorted_current_unc


test = 10
if test == 4:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp 10-75 117-5 better DAQ.csv"
elif test == 5:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp 10-75 117-5 better DAQ 2.csv"
elif test == 6:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp 10-75 117-5 better DAQ 3.csv"
elif test == 7:
    file_name = "blowing test (2 peaks at end).csv"
elif test == 8:
    file_name = "lm334 in4002 combined circuit output 470Kohm + temp wk9.csv"
elif test == 9:
    file_name = "28-11-24 reading.csv"
elif test == 10:
    file_name = "28-11-24 reading.csv"

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
ch4_time = np.array([])
ch5_time = np.array([])
ch6_time = np.array([])
ch0_voltage = np.array([])
ch1_voltage = np.array([])
ch2_voltage = np.array([])
ch3_voltage = np.array([])
ch4_voltage = np.array([])
ch5_voltage = np.array([])
ch6_voltage = np.array([])
ch0_temperature = np.array([])
ch1_temperature = np.array([])
ch2_temperature = np.array([])
ch3_temperature = np.array([])
ch4_temperature = np.array([])
ch5_temperature = np.array([])
ch6_temperature = np.array([])

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
    elif chanel_no == 5:
        ch5_time = np.append(ch5_time, data_temp[v,0])
        ch5_voltage = np.append(ch5_voltage, data_temp[v,2])
        ch5_temperature = np.append(ch5_temperature, data_temp[v,3])
    elif chanel_no == 4:
        ch4_time = np.append(ch4_time, data_temp[v,0])
        ch4_voltage = np.append(ch4_voltage, data_temp[v,2])
        ch4_temperature = np.append(ch4_temperature, data_temp[v,3])
    elif chanel_no == 6:
        ch6_time = np.append(ch6_time, data_temp[v,0])
        ch6_voltage = np.append(ch6_voltage, data_temp[v,2])
        ch6_temperature = np.append(ch6_temperature, data_temp[v,3])
    v+=1


if test == 8: 
    ch1_temperature= ch5_temperature
    ch0_voltage= ch6_voltage

if test == 9: 
    ch1_temperature= ch6_temperature
    ch0_voltage= ch4_voltage
    

def string_to_numpy_array(input_string):
    # Split the string by whitespace and filter out empty strings
    number_strings = input_string.split()
    
    # Convert the list of strings to a numpy array of floats (or ints)
    numbers_array = np.array([float(num) for num in number_strings])
    
    return numbers_array

def get_info_after_colon_trimmed(input_string):
    # Find the index of the first colon
    colon_index = input_string.find(':')
    
    # Check if a colon was found
    if colon_index != -1:
        # Extract everything after the colon
        info_after_colon = input_string[colon_index + 1:]
        # Remove spaces immediately after the colon
        return info_after_colon.lstrip()  # This removes leading spaces only
    else:
        return "No colon found in the string."

data = np.genfromtxt("BC568 high t calibration2.330", dtype = 'str', delimiter = ',')
number_strings = data[7:]

#if test == 9:
#    data = np.genfromtxt("LM334 470k calibration 121124.330", dtype = 'str', delimiter = ',')

data_array = np.zeros((0,3),dtype = 'float')

for data_entry in number_strings:
    temp_data_array = np.array([[0.,0.,0.]] )
    temp_numpy_array = string_to_numpy_array(data_entry)
    temp_data_array[0] = temp_numpy_array
    data_array = np.vstack((data_array,temp_data_array))

sensor_model = get_info_after_colon_trimmed(data[0])
serial_number = get_info_after_colon_trimmed(data[1])
interpolation_method = get_info_after_colon_trimmed(data[2])
setpoint_limit = get_info_after_colon_trimmed(data[3])
data_format = get_info_after_colon_trimmed(data[4])
no_breakpoints = get_info_after_colon_trimmed(data[5])
units = str(data[6])

header_tuple = (sensor_model,serial_number,interpolation_method,
                setpoint_limit,data_format,no_breakpoints,units)

counter = 0
dummy_voltage = 0.0
previous_v = 0
previous_t = 0
temperature = []


calibration_data_current = data_array
voltage_values = calibration_data_current[:, 1]
temperature_values = calibration_data_current[:, 2]

for voltage_measurement in ch6_voltage:
    counter += 1
    #print(voltage_measurement)
    if counter % 100 == 0:
        print(f"{counter} of {len(ch1_voltage)}")
        
    if voltage_measurement == previous_v:
        temperature.append(previous_t)
    else:
        # Use searchsorted to find the appropriate index
        i = np.searchsorted(voltage_values, voltage_measurement)
        
        if i == 0:
            # Handle case where measurement is below the first calibration point
            # Extrapolate using the gradient between the first two points
            voltage_before = voltage_values[0]
            voltage_after = voltage_values[1]
            temp_before = temperature_values[0]
            temp_after = temperature_values[1]
            
            gradient = (temp_after - temp_before) / (voltage_after - voltage_before)
            temperature_temp = temp_before + gradient * (voltage_measurement - voltage_before)
        
        elif i >= len(calibration_data_current):
            # Handle case where measurement is above the last calibration point
            # Extrapolate using the gradient between the last two points
            voltage_before = voltage_values[-2]
            voltage_after = voltage_values[-1]
            temp_before = temperature_values[-2]
            temp_after = temperature_values[-1]
            
            gradient = (temp_after - temp_before) / (voltage_after - voltage_before)
            temperature_temp = temp_before + gradient * (voltage_measurement - voltage_before)
        
        else:
            # Interpolate between breakpoints to find temperature
            temp_before = temperature_values[i - 1]
            temp_after = temperature_values[i]
            voltage_before = voltage_values[i - 1]
            voltage_after = voltage_values[i]
            
            temperature_temp = temp_before + (temp_after - temp_before) * (voltage_measurement - voltage_before) / (voltage_after - voltage_before)
        
        #print(temperature_temp)
        temperature.append(temperature_temp)
        previous_t = temperature_temp
        previous_v = voltage_measurement

    
#-------------

#ch1_temperature = temperature

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
if test == 9:
    ch0_current = (ch0_voltage/473200) * (10**6)
if test == 10:
    ch0_current = (ch5_voltage/478500) * (10**6)
ax.plot(ch0_time,ch0_current,
           label = "Current", zorder = 3,linewidth = 0.6, color = 'black')
#bx.plot(ch0_time,ch1_temperature,
#           label = "Transistor temperature", zorder = 3,linewidth = 1)
bx.plot(ch0_time,temperature,
           label = "Transistor temperature", zorder = 3,linewidth = 1)

#ax.plot(ch0_time,ch2_voltage,
#           label = "IN4002 diode", zorder = 3, alpha = 0.7)

ax.legend()
bx.legend()

output_figure1.tight_layout()
#output_figure1.savefig(f"week 9 lm334 and transistor offset test CURRENT {test}.png",dpi = 1000,
#                       bbox_inches = "tight")

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
#ax.scatter(ch1_temperature,ch0_current, marker = 'x', s = 10,
#           label = "I across 470KΩ resistor", zorder = 2,
#           color = 'black')
ax.scatter(temperature,ch0_current, marker = 'x', s = 10,
           label = "I across 470KΩ resistor", zorder = 2,
           color = 'black')

ax.legend()

output_figure1.tight_layout()
#output_figure1.savefig(f"week 9 lm334 and transistor offset test {test} IT hot+cold.png",dpi = 1000,
#                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

#-------------------------------------------------------

#ch1_temperature_slice = ch1_temperature[1075:8175]
ch1_temperature_slice = temperature[1075:8175]
ch0_voltage_slice = ch0_voltage[1075:8175]
ch5_voltage_slice = ch5_voltage[1075:8175]
ch0_current_slice = ch0_current[1075:8175]

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
#output_figure1.savefig(f"week 9 lm334 and transistor offset test {test} IT cold.png",dpi = 1000,
#                       bbox_inches = "tight")

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
if test == 10:
    VT_array = compute_average_temperature_and_uncertainty(ch1_temperature_slice, ch5_voltage_slice)


sorted_temp = VT_array[:,0]
sorted_voltage = VT_array[:,1]
sorted_current = (sorted_voltage/478500) * (10 ** 6)
sorted_voltage_unc = VT_array[:,2]/2
sorted_current_unc = (sorted_voltage_unc/478500) * (10 ** 6)

if test == 9 :
    sorted_temp = VT_array[:,0]
    sorted_voltage = VT_array[:,1]
    sorted_current = (sorted_voltage/473200) * (10 ** 6)
    sorted_voltage_unc = VT_array[:,2]/2
    sorted_current_unc = (sorted_voltage_unc/473200) * (10 ** 6)

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
#output_figure1.savefig(f"Wk 9 IT graph transistor IN4002 + LM334 Sorted {test}.png",dpi = 1000,
#                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

sorted_current_unc = sorted_current_unc
pos = np.where(sorted_current_unc == 0)

sorted_temp = np.delete(sorted_temp,pos)
sorted_current = np.delete(sorted_current,pos)
sorted_current_unc = np.delete(sorted_current_unc,pos)

bounds_set = np.array([[300,340],[10.175,10.1925]])
of.fit((test_9_sorted_temp,sorted_temp),
       (test_9_sorted_current,sorted_current),
       (test_9_sorted_current_unc,sorted_current_unc),
       x_err = (sorted_current_unc*0+0.00001),
       fit_type = 0,
       initial_guess = (0.00057,10),
       exclude_outliers = False,
       fitting_method = 'lm',
       graph_xlabel = "Temperature (°K)",
       graph_ylabel = "Current (μA)",
       graph_filename = "IN4002 + LM334 straight line fit test comparison",
       function_returns = False,
       graph_legend = False,
       graph_title = "IN4002 + LM334 straight line fit comparison",
       highlight_outliers = False,
       graph_marker_colour = ("tab:blue","black"))
