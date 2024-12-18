# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 11:24:43 2024

@author: Oliver
"""

import numpy as np
data = np.genfromtxt("DT-600 330 format Std Crv.330", dtype = 'str', delimiter = ',')

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

number_strings = data[7:]

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

print(data_array)

data2 = np.genfromtxt("liquid nitrogen with calibrated diode longer.csv", delimiter = ',',
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

counter = 0
dummy_voltage = 0.0
previous_v = 0
previous_t = 0
temperature = []

calibration_data_current = data_array
voltage_values = calibration_data_current[:, 1]
temperature_values = calibration_data_current[:, 2]

for voltage_measurement in ch2_voltage2:
    counter += 1

    if counter % 100 == 0:
        print(f"{counter} of {len(ch2_voltage2)}")
        
    if voltage_measurement == previous_v:
        temperature.append(previous_t)
    else:
        # Use searchsorted to find the appropriate index
        i = np.searchsorted(voltage_values, voltage_measurement)
        
        if i == 0:
            # Handle case where measurement is below the first calibration point
            temperature_temp = temperature_values[0]
        elif i >= len(calibration_data_current):
            # Handle case where measurement is above the last calibration point
            temperature_temp = temperature_values[-1]
        else:
            # Interpolate between breakpoints to find temperature
            temp_before = temperature_values[i - 1]
            temp_after = temperature_values[i]
            voltage_before = voltage_values[i - 1]
            voltage_after = voltage_values[i]
            
            temperature_temp = temp_before + (temp_after - temp_before) * (voltage_measurement - voltage_before) / (voltage_after - voltage_before)

        temperature.append(temperature_temp)
        previous_t = temperature_temp
        previous_v = voltage_measurement

# Convert temperature list to a NumPy array if needed
temperature = np.array(temperature)
print(temperature)