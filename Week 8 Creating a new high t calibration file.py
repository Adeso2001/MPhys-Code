# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 11:24:43 2024

@author: Oliver
"""

import numpy as np
import matplotlib.pyplot as plt

data = np.genfromtxt("LM334 470k calibration 121124.330", dtype = 'str', delimiter = ',')

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

data2 = np.genfromtxt("lm334 diode calibration data hot 12112024.csv", delimiter = ',',
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

for voltage_measurement in ch0_voltage2:
    counter += 1
    #print(voltage_measurement)
    if counter % 100 == 0:
        print(f"{counter} of {len(ch2_voltage2)}")
        
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


# Convert temperature list to a NumPy array if needed
temperature = np.array(temperature)



#-------------

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage (V)")
ax.set_title("Voltage over Time plot (stycasted LM and transistor)")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)


ax.plot(ch0_time,ch0_voltage,
           label = "LM334", zorder = 3, alpha = 0.7)
ax.plot(ch0_time,ch1_voltage,
           label = "Transitor diode", zorder = 3, alpha = 0.7)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("week 8 lm334 and transistor.png",dpi = 1000,
                       bbox_inches = "tight")


plt.show()
plt.close(output_figure1)

#-------------------------

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_xlabel("Temperature (°K)")
ax.set_ylabel("Voltage (V)")
ax.set_title("Voltage-Temperature graphs for LM334")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)


ax.scatter(temperature,ch0_voltage, marker = '.', s = 5,
           label = "LM334", zorder = 3, alpha = 0.7)
#ax.scatter(temperature,ch1_voltage, marker = '.', s = 5,
#           label = "Transistor Diode", zorder = 2, alpha = 0.7)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("Wk 8 VT graph LM334.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

#-------------------------

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_xlabel("Temperature (°K)")
ax.set_ylabel("Voltage (V)")
ax.set_title("Voltage-Temperature graph for transistor")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)


#ax.scatter(temperature,ch0_voltage, marker = '.', s = 5,
#           label = "LM334", zorder = 3, alpha = 0.7)
ax.scatter(temperature,ch1_voltage, marker = '.', s = 5,
           label = "Transistor Diode", zorder = 2, alpha = 0.7)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("Wk 8 VT graph transistor diode Hot.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

def compute_average_temperature_and_uncertainty(voltages, temperatures):
    # Initialize a dictionary to store temperature values for each unique voltage
    voltage_to_temperatures = {}
    
    # Group temperatures by corresponding voltage measurements
    for voltage, temp in zip(voltages, temperatures):
        if voltage not in voltage_to_temperatures:
            voltage_to_temperatures[voltage] = []
        voltage_to_temperatures[voltage].append(temp)
    
    # List to store the final results
    results = []
    
    # For each unique voltage, compute the average temperature and the temperature range
    for voltage in voltage_to_temperatures:
        temps = voltage_to_temperatures[voltage]
        avg_temp = np.mean(temps)  # Average temperature for the given voltage
        temp_range = (np.min(temps), np.max(temps))  # Range of temperatures for the given voltage
        
        # Append the results (voltage, avg_temp, temp_range)
        results.append([voltage, avg_temp, temp_range[1] - temp_range[0]])  # Store voltage, avg temp, and temperature range
    
    # Convert the results list to a 2D numpy array
    results_array = np.array(results)
    
    return results_array

vt_array_transistor = compute_average_temperature_and_uncertainty(
    ch1_voltage,temperature)

transistor_calibration_voltages = vt_array_transistor[:,0]
transistor_calibration_temperatures = vt_array_transistor[:,1]
transistor_calibration_unc = vt_array_transistor[:,2]/2

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_ylabel("Temperature (°K)")
ax.set_xlabel("Voltage (V)")
ax.set_title("Voltage-Temperature graph for transistor cleaned up")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)

ax.scatter(transistor_calibration_voltages,
           transistor_calibration_temperatures,
           marker = 'x', s = 10,
           label = "Transistor Diode", zorder = 2,
           color = 'black')
ax.errorbar(transistor_calibration_voltages,
           transistor_calibration_temperatures,
           yerr = transistor_calibration_unc,
           fmt = 'x',
           markersize = 0,
           ecolor = 'red',
           zorder = 1,
           elinewidth = 1)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("Wk 8 VT graph transistor diode Hot sorted.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

np.set_printoptions(suppress=True)
np.savetxt("vt array.txt", vt_array_transistor, delimiter = ' ')
