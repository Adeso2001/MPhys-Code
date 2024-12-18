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

data2 = np.genfromtxt("lm334 diode calibration data hotter 12112024.csv", delimiter = ',',
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
ax.plot(ch0_time,ch2_voltage,
           label = "IN4002 diode", zorder = 3, alpha = 0.7)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("week 8 lm334 and transistor hotter.png",dpi = 1000,
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
output_figure1.savefig("Wk 8 VT graph LM334 hotter.png",dpi = 1000,
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
output_figure1.savefig("Wk 8 VT graph transistor diode Hotter.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

#-------------------------

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_xlabel("Temperature (°K)")
ax.set_ylabel("Voltage (V)")
ax.set_title("Voltage-Temperature graph for IN4002")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)


#ax.scatter(temperature,ch0_voltage, marker = '.', s = 5,
#           label = "LM334", zorder = 3, alpha = 0.7)
ax.scatter(temperature,ch2_voltage, marker = '.', s = 5,
           label = "IN4002 Diode", zorder = 2, alpha = 0.7)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("Wk 8 VT graph transistor IN4002 Hotter.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

#temperature_sliced = temperature[1150:]
#ch2_voltage_sliced = ch2_voltage[1150:]

temperature_sliced = temperature[1500:]
ch2_voltage_sliced = ch2_voltage[1500:]

def compute_average_temperature_and_uncertainty2(voltages, temperatures, voltage_jump_threshold=0.00):
    """
    Computes the average temperature and temperature range for each unique voltage,
    discounting any outliers caused by sudden voltage jumps.

    Parameters:
    - voltages: List or numpy array of voltage measurements.
    - temperatures: List or numpy array of temperature measurements corresponding to voltages.
    - voltage_jump_threshold: The threshold for detecting sudden voltage jumps. Voltage readings with a
                               jump greater than this threshold are considered outliers.

    Returns:
    - A 2D numpy array with columns [voltage, average_temperature, temperature_range] for each unique voltage.
    """
    # Initialize a dictionary to store temperatures corresponding to each voltage
    voltage_to_temperatures = {}

    # Flag for detecting voltage jumps
    previous_voltage = None

    # Group temperatures by corresponding voltage, excluding outliers
    for voltage, temp in zip(voltages, temperatures):
        if previous_voltage is not None:
            voltage_jump = abs(voltage - previous_voltage)
            if voltage_jump > voltage_jump_threshold:
                # If there's a sudden voltage jump, skip both the voltage and the temperature for this point
                previous_voltage = voltage  # Update to current voltage to continue checking subsequent values
                continue  # Skip adding this voltage-temperature pair to the dictionary
        
        # Add temperature to the list for this voltage
        if voltage not in voltage_to_temperatures:
            voltage_to_temperatures[voltage] = []
        voltage_to_temperatures[voltage].append(temp)

        # Update the previous_voltage to current voltage
        previous_voltage = voltage
    
    # List to store the final results
    results = []

    # For each unique voltage, compute the average temperature and temperature range
    for voltage in voltage_to_temperatures:
        temps = voltage_to_temperatures[voltage]
        avg_temp = np.mean(temps)  # Average temperature for the given voltage
        temp_range = (np.min(temps), np.max(temps))  # Range of temperatures for the given voltage
        
        # Append the results (voltage, avg_temp, and temp range)
        results.append([voltage, avg_temp, temp_range[1] - temp_range[0]])  # Store voltage, avg temp, and temperature range
    
    # Convert the results list to a 2D numpy array
    results_array = np.array(results)
    
    return results_array


def compute_average_temperature_and_uncertainty(voltages, temperatures, z_score_threshold=3, min_points=4):
    """
    Computes the average temperature and temperature range for each unique voltage,
    excluding temperature outliers based on the z-score method and ignoring voltages with too few points.

    Parameters:
    - voltages: List or numpy array of voltage measurements.
    - temperatures: List or numpy array of temperature measurements corresponding to voltages.
    - z_score_threshold: The number of standard deviations away from the mean a temperature must be
                          to be considered an outlier.
    - min_points: The minimum number of data points required for a voltage to be considered (exclude otherwise).

    Returns:
    - A 2D numpy array with columns [voltage, average_temperature, temperature_range] for each unique voltage.
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
        for temp in temps:
            z_score = (temp - mean_temp) / std_temp if std_temp != 0 else 0  # Avoid division by zero
            if abs(z_score) <= z_score_threshold:
                filtered_temps.append(temp)
        
        # Calculate the average and range of the filtered (non-outlier) temperatures
        avg_temp = np.mean(filtered_temps)
        temp_range = (np.min(filtered_temps), np.max(filtered_temps))

        # Append the results (voltage, avg_temp, and temp range)
        results.append([voltage, avg_temp, temp_range[1] - temp_range[0]])  # Store voltage, avg temp, and temperature range
    
    # Convert the results list to a 2D numpy array
    results_array = np.array(results)
    
    return results_array



vt_array_transistor = compute_average_temperature_and_uncertainty(
    ch1_voltage,temperature)

transistor_calibration_voltages = vt_array_transistor[:,0]
transistor_calibration_temperatures = vt_array_transistor[:,1]
transistor_calibration_unc = vt_array_transistor[:,2]/2

vt_array_IN4002 = compute_average_temperature_and_uncertainty(
    ch2_voltage,temperature)

vt_array_IN4002_sliced = compute_average_temperature_and_uncertainty(
    ch2_voltage_sliced,temperature_sliced)

IN4002_calibration_voltages = vt_array_IN4002[:,0]
IN4002_calibration_temperatures = vt_array_IN4002[:,1]
IN4002_calibration_unc = vt_array_IN4002[:,2]/2


IN4002_calibration_voltages_sliced = vt_array_IN4002_sliced[:,0]
IN4002_calibration_temperatures_sliced = vt_array_IN4002_sliced[:,1]
IN4002_calibration_unc_sliced = vt_array_IN4002_sliced[:,2]/2
#------------------------------------
 
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
output_figure1.savefig("Wk 8 VT graph transistor diode Hotter sorted.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

def write_voltage_temperature_to_file(voltages, temperatures, output_file='voltage_temperature_data_hotter_diode.txt'):
    """
    Writes the voltage and temperature data to a text file in decreasing order of temperature.
    
    Parameters:
    - voltages: List or numpy array of voltage measurements.
    - temperatures: List or numpy array of temperature measurements corresponding to voltages.
    - output_file: The name of the output text file where the data will be saved.
    """
    # Combine the voltages and temperatures into a list of tuples (voltage, temperature)
    voltage_temp_pairs = list(zip(voltages, temperatures))
    
    # Sort the list by temperature in decreasing order
    sorted_voltage_temp_pairs = sorted(voltage_temp_pairs, key=lambda x: x[1], reverse=True)
    
    # Open the output file for writing
    with open(output_file, 'w') as file:
        # Iterate over the sorted data and write each entry to the file
        for idx, (voltage, temperature) in enumerate(sorted_voltage_temp_pairs, start=1):
            # Apply 7 significant figures for values >= 1 and 6 significant figures for values < 1
            if voltage < 1:
                formatted_voltage = f"{voltage:.6g}"
            else:
                formatted_voltage = f"{voltage:.7g}"
            
            if temperature < 1:
                formatted_temperature = f"{temperature:.6g}"
            else:
                formatted_temperature = f"{temperature:.7g}"
            
            # Write the entry number (with 2 leading spaces), voltage, and temperature to the file
            file.write(f"  {idx} {formatted_voltage} {formatted_temperature}\n")


write_voltage_temperature_to_file(transistor_calibration_voltages, transistor_calibration_temperatures)

#----------------------------------------

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_ylabel("Temperature (°K)")
ax.set_xlabel("Voltage (V)")
ax.set_title("Voltage-Temperature graph for IN4002 cleaned up")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)

ax.scatter(IN4002_calibration_voltages,
           IN4002_calibration_temperatures,
           marker = 'x', s = 10,
           label = "IN4002", zorder = 2,
           color = 'black')
ax.errorbar(IN4002_calibration_voltages,
           IN4002_calibration_temperatures,
           yerr = IN4002_calibration_unc,
           fmt = 'x',
           markersize = 0,
           ecolor = 'red',
           zorder = 1,
           elinewidth = 1)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("Wk 8 VT graph transistor IN4002 Hotter sorted.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

import Omega_fit2 as of

of.fit(IN4002_calibration_voltages,IN4002_calibration_temperatures,
       IN4002_calibration_unc, fit_type = 0,
       initial_guess = (0,0),
       graph_ylabel = "Temperature (°K)",
       graph_xlabel = "Voltage (V)",
       graph_filename = "IN4002 straight line fit",
       function_returns = False,
       graph_legend = False,
       graph_title = "IN4002 straight line fit")


# COOLDOWN ONLY CODE =============================

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_xlabel("Temperature (°K)")
ax.set_ylabel("Voltage (V)")
ax.set_title("VT graph sliced for IN4002")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)


#ax.scatter(temperature,ch0_voltage, marker = '.', s = 5,
#           label = "LM334", zorder = 3, alpha = 0.7)
ax.scatter(temperature_sliced,ch2_voltage_sliced, marker = '.', s = 5,
           label = "IN4002 Diode", zorder = 2, alpha = 0.7)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("Wk 8 VT graph IN4002 sliced Hotter.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

#----------------------

output_figure1 = plt.figure(0)
ax = output_figure1.add_subplot(111)


ax.set_ylabel("Temperature (°K)")
ax.set_xlabel("Voltage (V)")
ax.set_title("VT graph for IN4002 Sliced cleaned up")
    
ax.grid(True, color='grey', dashes=(4, 2), zorder = 0)

ax.scatter(IN4002_calibration_voltages_sliced,
           IN4002_calibration_temperatures_sliced,
           marker = 'x', s = 10,
           label = "IN4002", zorder = 2,
           color = 'black')
ax.errorbar(IN4002_calibration_voltages_sliced,
           IN4002_calibration_temperatures_sliced,
           yerr = IN4002_calibration_unc_sliced,
           fmt = 'x',
           markersize = 0,
           ecolor = 'red',
           zorder = 1,
           elinewidth = 1)

ax.legend()

output_figure1.tight_layout()
output_figure1.savefig("Wk 8 VT graph IN4002 Hotter Sliced sorted.png",dpi = 1000,
                       bbox_inches = "tight")

plt.show()
plt.close(output_figure1)

#----------------------

of.fit(IN4002_calibration_voltages_sliced,
       IN4002_calibration_temperatures_sliced,
       IN4002_calibration_unc_sliced, fit_type = 0,
       initial_guess = (0,0),
       graph_ylabel = "Temperature (°K)",
       graph_xlabel = "Voltage (V)",
       graph_filename = "IN4002 sliced straight line fit",
       function_returns = False,
       graph_legend = False,
       graph_title = "IN4002 Sliced Straight Line Fit")
