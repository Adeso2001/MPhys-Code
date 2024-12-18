# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 15:09:15 2024

@author: Oliver
"""

import numpy as np
import matplotlib.pyplot as plt

file_name = "liquid N2 05-12-24 almostdone2.csv"

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
ch7_time = np.array([])
ch0_voltage = np.array([])
ch1_voltage = np.array([])
ch2_voltage = np.array([])
ch3_voltage = np.array([])
ch4_voltage = np.array([])
ch5_voltage = np.array([])
ch6_voltage = np.array([])
ch7_voltage = np.array([])
ch0_temperature = np.array([])
ch1_temperature = np.array([])
ch2_temperature = np.array([])
ch3_temperature = np.array([])
ch4_temperature = np.array([])
ch5_temperature = np.array([])
ch6_temperature = np.array([])
ch7_temperature = np.array([])

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

data = np.genfromtxt("DT-600 330 format Std Crv.330", dtype = 'str', delimiter = ',')
number_strings = data[7:]

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
    elif chanel_no == 7:
        ch7_time = np.append(ch7_time, data_temp[v,0])
        ch7_voltage = np.append(ch7_voltage, data_temp[v,2])
        ch7_temperature = np.append(ch7_temperature, data_temp[v,3])
    v+=1

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

for voltage_measurement in ch7_voltage:
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
        
output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage (V)")
ax.set_title("Liquid nitrogen test 1")
#ax.set_xlim([0,data1[-1,0]])
ax.set_xlim([0,2000])
ax.set_ylim([0.5,1.1])

ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)

ax.plot(ch4_time,ch4_voltage,color = "Tab:blue",alpha = 0.7, linewidth = 0.8,
        label = "Transistor 1")
ax.plot(ch5_time,ch5_voltage,color = "Tab:red",alpha = 0.7, linewidth = 0.8,
        label = "Transistor 2")
ax.plot(ch6_time,ch6_voltage,color = "Tab:green",alpha = 0.7, linewidth = 0.8,
        label = "Transistor 3")
ax.plot(ch7_time,ch7_voltage,color = "Tab:gray",alpha = 0.7, linewidth = 0.8,
        label = "Calibrated Diode")
ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("Week 10 Liquid N2 test voltages.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)
        

#----------------------------------------------------------------

ch7_temperature_slice = temperature[1200:13000]
ch4_voltage_slice = ch4_voltage[1200:13000]
ch5_voltage_slice = ch5_voltage[1200:13000]
ch6_voltage_slice = ch6_voltage[1200:13000]
ch7_voltage_slice = ch7_voltage[1200:13000]


def compute_average_temperature_and_uncertainty(voltages, temperatures, z_score_threshold=3, min_points=1):
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

VT_array_1 = compute_average_temperature_and_uncertainty(ch7_temperature_slice, ch4_voltage_slice)
VT_array_2 = compute_average_temperature_and_uncertainty(ch7_temperature_slice, ch5_voltage_slice)
VT_array_3 = compute_average_temperature_and_uncertainty(ch7_temperature_slice, ch6_voltage_slice)
VT_array_cal = compute_average_temperature_and_uncertainty(ch7_temperature_slice, ch7_voltage_slice)

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_xlabel("Temperature (°K)")
ax.set_ylabel("Voltage (V)")
ax.set_title("Voltage-Temperature graphs for our Diodes")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)



ax.scatter(VT_array_1[:,0],VT_array_1[:,1], marker = '+', s = 1,
           label = "Transistor 1", zorder = 3, alpha = 0.7)
ax.errorbar(VT_array_1[:,0],
           VT_array_1[:,1],
           (VT_array_1[:,2]/2),
           fmt = 'x',
           markersize = 0,
           ecolor = 'red',
           zorder = 1,
           elinewidth = 1)
ax.scatter(VT_array_2[:,0],VT_array_2[:,1], marker = '+', s = 1,
           label = "Transistor 2", zorder = 3, alpha = 0.7)
ax.errorbar(VT_array_2[:,0],
           VT_array_2[:,1],
           (VT_array_2[:,2]/2),
           fmt = 'x',
           markersize = 0,
           ecolor = 'red',
           zorder = 1,
           elinewidth = 1)
ax.scatter(VT_array_3[:,0],VT_array_3[:,1], marker = '+', s = 1,
           label = "Transistor 3", zorder = 3, alpha = 0.7)
ax.errorbar(VT_array_3[:,0],
           VT_array_3[:,1],
           (VT_array_3[:,2]/2),
           fmt = 'x',
           markersize = 0,
           ecolor = 'red',
           zorder = 1,
           elinewidth = 1)
ax.scatter(VT_array_cal[:,0],VT_array_cal[:,1], marker = '+', s = 1,
           label = "Calibrated Diode", zorder = 3, alpha = 0.7)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("VT graph LiquidN wk11.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)
