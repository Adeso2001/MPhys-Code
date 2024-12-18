# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:32:17 2023

Program for automating the aquisition of fits using Curve_fit and ODR from 
scipy

Go to line 580 to add additional models

Oliver Ades - University of manchester
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from scipy.optimize import curve_fit
from scipy import odr


FILE_NAME = 'conduction_data'
FILE_TYPE_CSV = True
SKIP_DATAPOINT = []
DELIMITER = ','

STDS_COUNTED_AS_OUTLIER = 3

# Pick from fit_type list:
# 0 -- linear -- y = A * x + B
# 1 -- exponential -- y = A * (x ** B)
# 2 -- exponential cutoff -- y = A * exp(-B * x)
# 3 -- Thermal diffusivity cutoff -- y = A / (1 + A / (B * x))
# 4 -- parabola -- y = A * (x ** 2) + B * x + C
# 5 -- Cubic fit -- y = A * (x ** 3) + B * (x ** 2) + B * x + D
# 6 -- sinusoidal -- y = A * sin(B * x + C) + D
# 7 -- decaying_sinusoidal -- y = A * exp(B) * sin(C * x + D) + E
# 8 -- arctan minimum -- 
# y = ((z * ( ( arctan( z / F ) / pi ) + 0.5) + F / pi) + g) / 100,
# where z = (A * ( x - B) - C + D * sin(E * (x - B)))
FIT_TYPE = 2
PARAMETERS_GUESS = (0.032, 750)

DISTRIBUTION_SIZE = 5000
GRAPH_NAME = 'Test_plot'
DPI = 1000

UNCERTAINTY_DECIMAL_PLACE_ACCURACY = 10
UNCERTAINTY_RANGE_SEARCH = 2

def round_uncertainty(number, uncertainty_on_number):
    """
    This function is used to round a number to the same accuracy as the
    uncertainty at 2.s.f.. This uses the round function, however if the float
    ends in a zero this will be removed by the program. To get around this the
    function checks for if this has happened and manually adds the 0 back if
    it has been removed.


    Parameters
    ----------
    number : float/integer
        Number which is to be rounded to the same accuracy as the uncertainty
        as 2.s.f
    uncertainty_on_number : float/integer
        Uncertainty on the aformentioned number. It is set to be rounded to
        2.s.f

    Returns
    -------
    message_return : string
        string containting the rounded values with uncertainty

    """

    # Finds the x10 power needed to represent the number, which can be used to
    # get the numbers in the x10 power form
    log10_number = (np.log10(abs(number)))
    pow_10_number = math.floor(log10_number)

    # Updates numbers to x10 power form
    number_updated = number * 10 ** (-pow_10_number)
    uncertainty_on_number_updated = (
        uncertainty_on_number * 10 ** (-pow_10_number))

    # Finds x10 power of uncertainty so the numbers can be rounded
    log10_uncertainty_updated = (np.log10(abs(uncertainty_on_number_updated)))
    pow_10_uncertainty_updated = math.floor(log10_uncertainty_updated)

    # specifies the amount of rounding to take place so that uncertainty is
    # 2.s.f
    rounding_number = 1 - pow_10_uncertainty_updated
    rounded_number = round(number_updated, rounding_number)
    rounded_uncertainty = round(uncertainty_on_number_updated, rounding_number)

    # puts number in a form where it is to same accuracy as 2.s.f uncertainty
    string_rounded_number = str(rounded_number)
    if "e" in string_rounded_number:
        string_rounded_number = ("{0:f}").format(rounded_number)
    if len(string_rounded_number) != (rounding_number + 2):
        string_rounded_number = string_rounded_number + '0'

    # putes uncertainty in a form where it is 2.s.f
    string_rounded_uncertainty = str(rounded_uncertainty)
    if "e" in string_rounded_uncertainty:
        string_rounded_uncertainty = ("{0:f}").format(rounded_uncertainty)
    if string_rounded_uncertainty[0] == '0':
        if len(string_rounded_uncertainty) != (rounding_number + 2):
            string_rounded_uncertainty = string_rounded_uncertainty + '0'
    elif string_rounded_uncertainty[1] == '.':
        if len(string_rounded_uncertainty) != (rounding_number + 2):
            string_rounded_uncertainty = string_rounded_uncertainty + '0'

    # formats the previous numbers into a message that is returned
    message_return = ("( {0} ± {1} ) x10^{2}").format(
        string_rounded_number, string_rounded_uncertainty, pow_10_number)

    return message_return

def round_3sf(number, uncertainty_on_number):
    """
    This function is used to round a number and its associated uncertainty to
    3.s.f. This uses the round function, however if the float ends in a zero
    this will be removed by the program. To get around this the function checks
    for if this has happened and manually adds the 0 back if it has been
    removed.


    Parameters
    ----------
    number : float/integer
        Number which is to be rounded to 3.s.f
    uncertainty_on_number : float/integer
        Uncertainty on the aformentioned number. It is set to be rounded to
        the same accuracy as the first number

    Returns
    -------
    string_3sf_number : string
        string of the original number but now rounded to 3.s.f
    string_3sf_uncertainty : string
        string of the original uncertainty, but rounded to the same accuracy as
        the 3.s.f number

    """

    # Finds the x10 power needed to represent the number, which can be used to
    # round to 3sf
    log10_number = np.log10(number)
    pow_10_number = math.floor(log10_number)
    rounding_digit = 2 - pow_10_number

    # rounds the number
    three_sf_number = round(number, rounding_digit)
    three_sf_uncertainty = round(uncertainty_on_number, rounding_digit)

    # in the case of a number greater than 100
    if three_sf_number >= 100:
        return int(three_sf_number), int(three_sf_uncertainty)

    # round function removes 0 from end of rounded number, so this adds it back
    # in to the number itself
    string_3sf_number = str(three_sf_number)
    if "e" in string_3sf_number:
        string_3sf_number = ("{0:f}").format(three_sf_number)
    if "." in string_3sf_number:
        if string_3sf_number[0] == '0':
            if len(string_3sf_number) != (rounding_digit + 2):
                string_3sf_number = string_3sf_number + '0'
        elif string_3sf_number[1] == '.':
            if len(string_3sf_number) != (rounding_digit + 2):
                string_3sf_number = string_3sf_number + '0'
        elif string_3sf_number[2] == '.':
            if len(string_3sf_number) != (rounding_digit + 3):
                string_3sf_number = string_3sf_number + '0'

    # repeats previous steps with the uncertainty
    string_3sf_uncertainty = str(three_sf_uncertainty)
    if "e" in string_3sf_uncertainty:
        string_3sf_uncertainty = ("{0:f}").format(three_sf_uncertainty)
    if "." in string_3sf_uncertainty:
        if string_3sf_uncertainty[0] == '0':
            if len(string_3sf_uncertainty) != (rounding_digit + 2):
                string_3sf_uncertainty = string_3sf_uncertainty + '0'
        elif string_3sf_uncertainty[1] == '.':
            if len(string_3sf_uncertainty) != (rounding_digit + 2):
                string_3sf_uncertainty = string_3sf_uncertainty + '0'
        elif string_3sf_uncertainty[2] == '.':
            if len(string_3sf_uncertainty) != (rounding_digit + 3):
                string_3sf_uncertainty = string_3sf_uncertainty + '0'

    return string_3sf_number, string_3sf_uncertainty

def read_file():
    """
    Reads the file as specified in the global variables and returns a numpy
    array of the values contained in the file 

    Also performs validation on the information to ensure it wont crash the
    program
    """

    # assigns extension type
    if FILE_TYPE_CSV is True:
        extension = '.csv'
    else:
        extension = '.txt'

    file_name = FILE_NAME + extension

    # reads data in from txt or csv file
    try:
        individual_file_data = np.genfromtxt(file_name, delimiter=',')

    # In the event of an OS error where the function couldnt find the file
    except OSError:
        print("")
        print("ERROR:")
        print(("The program was unable to find the file '{0}' in the " +
               "working directory. Please check if the name of the file is" +
               " correct or if the file is in the correct " +
               "folder.").format(file_name))
        return False

    # In the event of a value error
    except ValueError:

        # Have not encountered value error with .csv file so cause of error
        # unknown and send warning message
        if extension == '.csv':
            print("")
            print("ERROR:")
            print(("The program ran into an unknown value error whilst " +
                   "trying to read the file '{0}'. Please ensure the file " +
                   "is formatted as previously " +
                   "specified.").format(file_name))

        # Value error when there is a header in txt files, so try to read file
        # again with first line skipped incase this works instead
        if extension == '.txt':
            try:
                individual_file_data = np.genfromtxt(
                    file_name, delimiter=',', skip_header=1)
            except:
                print("")
                print("ERROR:")
                print(("The program ran into a value error whilst trying to " +
                       "read the file '{0}'. This could be due to an " +
                       "inconsistent number of columns or rows in the file. " +
                       "Please ensure the file is formatted " +
                       "correctly.").format(file_name))
                return False
    # In the event an hitherto unencountered error
    except:
        print("")
        print("ERROR:")
        print(("The program ran into an unknown error whilst trying to read " +
              "the file '{0}'. Please ensure the file is formatted as " +
               "previously specified.").format(file_name))
        return False

    # try/except loop to make one_dimentional_str true only if it is a one
    # dimentional array with nan (can send warning if txt not comma-delimited)
    try:
        one_dimentional_str = np.isnan(individual_file_data[0])
        if one_dimentional_str != True:
            one_dimentional_str = False
    except:
        one_dimentional_str = False

    # Defines variables that will later be used for validation
    dimensions = np.shape(individual_file_data)
    columns = dimensions[1]

    # Function returns false if the file is empty
    if len(individual_file_data) == 0:
        print("")
        print("ERROR:")
        print(("The file '{0}' appears to be empty. Please ensure you have " +
              "entered the correct file and the file is empty and " +
               "saved.").format(file_name))
        return False

    # Function returns false and gives specific message for non-comma-delimited
    # txt files
    elif extension == '.txt' and one_dimentional_str:
        print("")
        print("ERROR:")
        print(("the text file '{0}' doesnt seem to be formatted correctly. " +
              "Please ensure the text file is comma delimited next " +
               "time.").format(file_name))
        return False

    # In the event of less columns than the program needs to function
    elif columns < 3:
        print("")
        print("ERROR:")
        print(("the file '{0}' doesnt seem to have the correct amount of " +
               "columns. Please ensure there are three columns next time, " +
               "with the first column being time (in hours), second activity" +
               " (TBq), and third uncertainty on " +
               "activity(TBq)").format(file_name))
        return False

    # Removes columns beyond the third (for example if header contains extra or
    # there is further information not necessary for program)
    shrunk_array = individual_file_data[:, :3]

    # Tests for nan values and creates array where filtered data will be added
    data_nan_test = np.isnan(shrunk_array)
    filtered_data = np.zeros((0, 3))

    # For loop which goes through the data array and adds lines with no nans
    # and where the uncertainty is non zero
    iterator = 0
    for line in data_nan_test:
        if not(line[0] or line[1] or line[2] or shrunk_array[iterator, 2] == 0):
            filtered_data = np.vstack(
                (filtered_data, shrunk_array[iterator, :]))
        iterator += 1

    filtered_data_dimensions = np.shape(filtered_data)
    filtered_data_rows = filtered_data_dimensions[0]

    # In the event that after filtering there is no data left, the program will
    # tell the user and return a value of False
    if filtered_data_rows == 0:
        print("")
        print("ERROR:")
        print(("The file '{0}' doesnt seem to contain any data which" +
              " the program can read. Please ensure the data contains only " +
               "numbers and is formatted as previously " +
               "specified").format(file_name))
        return False

    return filtered_data

def fit(x_data,y_data,y_err, x_err = "default", fit_type = FIT_TYPE, 
        set_bounds = False, initial_guess = PARAMETERS_GUESS, 
        fitting_method = "lm", exclude_outliers = True, 
        outlier_sigma = STDS_COUNTED_AS_OUTLIER, highlight_outliers = True, 
        graph_outlier_colour = "orange", set_significance = 1, 
        residuals = True, residuals_log_scale = False,
        graph_font_size = 12, graph_save = True, graph_title = "Graph Title", 
        graph_filename = GRAPH_NAME , graph_xlabel = "Independent Variable", 
        graph_ylabel = "Dependent Variable", graph_bounds = "default",
        graph_grid = True, graph_scatter = True, graph_marker = 'x',
        graph_marker_size = 35, graph_marker_thickness = 1.5, 
        graph_marker_colour = 'tab:blue', graph_marker_label = 'default',
        graph_fit = True, graph_fit_colour = "black", graph_fit_alpha = 0.5,
        graph_fit_thickness = 2, graph_fit_style = 'solid',
        graph_fit_name = "predicted model",graph_error = True,
        graph_error_colour = "red", graph_error_thickness = 0.5,
        graph_error_cap_size = 0, graph_legend = True, 
        graph_legend_location = "default", graph_dpi = 1000, 
        full_output = False, print_answers = True, print_answer_round = False, 
        disable_graph = False, output_chi = True, function_returns = True):
    
    #~~~~~~~~~~
    
    # Tests entered parameters to see if they correspond to multiple data sets
    # or models.
    comparison_amount = 1
    
    try:
        
        float(x_data[0])
        is_x_data_tuple = False
        # notes highest and lowest x values
        sorted_x_data = np.sort(x_data)
        lower_x_bound = sorted_x_data[0]
        upper_x_bound = sorted_x_data[-1]
    except:
        is_x_data_tuple = True
        comparison_amount = len(x_data)
        # Searches highest and lowest values in each data set and notes them
        for i in range(0,comparison_amount):
            x_data_component = x_data[i]
            sorted_x_data = np.sort(x_data_component)
            
            if i == 0:
                lower_x_bound = sorted_x_data[0]
                upper_x_bound = sorted_x_data[-1]
            else:
                if lower_x_bound > sorted_x_data[0]:
                    lower_x_bound = sorted_x_data[0]
                if upper_x_bound < sorted_x_data[-1]:
                    upper_x_bound = sorted_x_data[-1]
        
    try:
        float(y_data[0])
        is_y_data_tuple = False
    except:
        is_y_data_tuple = True
        comparison_amount = len(y_data)
        
    try:
        float(y_err[0])
        is_y_err_tuple = False
    except:
        is_y_err_tuple = True
        comparison_amount = len(y_err)
        
    try:
        x_err_component = x_err[0]
        if x_err_component == "default":
            is_x_err_tuple = True
            comparison_amount = len(x_err)
        else:
            try:
                float(x_err_component[0])
                is_x_err_tuple = True
                comparison_amount = len(x_err)
            except:
                is_x_err_tuple = False
    except:
        is_x_err_tuple = False

    if type(fit_type) is tuple:
        is_fit_type_tuple = True
        comparison_amount = len(fit_type)
    else:
        is_fit_type_tuple = False

    try:
        set_bounds_component = set_bounds[0]
        if set_bounds_component is False:
            is_set_bounds_tuple = True
            comparison_amount = len(set_bounds)
        else:
            try:
                set_bounds_component[0]
                is_set_bounds_tuple = True
                comparison_amount = len(set_bounds)
            except:
                is_set_bounds_tuple  = False
    except:
        is_set_bounds_tuple  = False
    
    try:
        initial_guess_component = initial_guess[0]
        initial_guess_component[0]
        is_initial_guess_tuple = True
        comparison_amount = len(initial_guess)  
    except:
        is_initial_guess_tuple  = False
 
    if type(fitting_method) is tuple:
        is_fitting_method_tuple = True 
        comparison_amount = len(fitting_method)
    else:
        is_fitting_method_tuple = False
   
    try:
        exclude_outliers[0]
        is_exclude_outliers_tuple = True
        comparison_amount = len(exclude_outliers)
    except:
        is_exclude_outliers_tuple = False
 
    try:
        outlier_sigma[0]
        is_outlier_sigma_tuple = True
        comparison_amount = len(outlier_sigma)
    except:
        is_outlier_sigma_tuple = False
    
    #~~~~~~~~~~  
    
    # Converts all data into a tuple form which the program will use to carry 
    # out the code    
        
    if is_x_data_tuple is True:
        x_data_tuple = x_data
    else:
        x_data_tuple = ()
        for i in range(0,comparison_amount):
            x_data_tuple = x_data_tuple + (x_data,)
    
    if is_y_data_tuple is True:
        y_data_tuple = y_data
    else:
        y_data_tuple = ()
        for i in range(0,comparison_amount):
            y_data_tuple = y_data_tuple + (y_data,)
    
    if is_y_err_tuple is True:
        y_err_tuple = y_err
    else:
        y_err_tuple = ()
        for i in range(0,comparison_amount):
            y_err_tuple = y_err_tuple + (y_err,)
    
    if is_x_err_tuple is True:
        x_err_tuple = x_err
    else:
        x_err_tuple = ()
        for i in range(0,comparison_amount):
            x_err_tuple = x_err_tuple + (x_err,)
            
    if is_fit_type_tuple is True:
        fit_type_tuple = fit_type
    else:
        fit_type_tuple = ()
        for i in range(0,comparison_amount):
            fit_type_tuple = fit_type_tuple + (fit_type,)
    
    if is_set_bounds_tuple is True:
        set_bounds_tuple = set_bounds
    else:
        set_bounds_tuple = ()
        for i in range(0,comparison_amount):
            set_bounds_tuple = set_bounds_tuple + (set_bounds,)
    
    if is_initial_guess_tuple is True:
        initial_guess_tuple = initial_guess
    else:
        initial_guess_tuple = ()
        for i in range(0,comparison_amount):
            initial_guess_tuple = initial_guess_tuple + (initial_guess,)
    
    if is_fitting_method_tuple is True:
        fitting_method_tuple = fitting_method
    else:
        fitting_method_tuple = ()
        for i in range(0,comparison_amount):
            fitting_method_tuple = fitting_method_tuple + (fitting_method,)
            
    if is_exclude_outliers_tuple is True:
        exclude_outliers_tuple = exclude_outliers
    else:
        exclude_outliers_tuple = ()
        for i in range(0,comparison_amount):
            exclude_outliers_tuple = exclude_outliers_tuple + (exclude_outliers,)
    
    if is_outlier_sigma_tuple is True:
        outlier_sigma_tuple = outlier_sigma
    else:
        outlier_sigma_tuple = ()
        for i in range(0,comparison_amount):
            outlier_sigma_tuple = outlier_sigma_tuple + (outlier_sigma,)
    
    #~~~~~~~~~~
    
    # Defines an x distribution used later in graphs
    if graph_bounds != "default":
        x_dist_start = graph_bounds[0,0]
        x_dist_end = graph_bounds[0,1]
    else:
        x_bounds_difference = upper_x_bound - lower_x_bound
        x_dist_start = lower_x_bound - (x_bounds_difference * 0.1)
        x_dist_end = upper_x_bound + (x_bounds_difference * 0.1)
    
    x_distribution = np.linspace(x_dist_start, x_dist_end, 9999)
    
    # Finds best guess of the parameters and their uncertainties along with the 
    # chi squared. Also models how the x and y values change along a 
    # distribution.
    
    y_distribution_tuple = ()
    non_outlier_x_data_tuple = ()
    non_outlier_y_data_tuple = ()
    non_outlier_x_err_tuple = ()
    non_outlier_y_err_tuple = ()
    outliers_x_data_tuple = ()
    outliers_y_data_tuple = ()
    parameters_best_guess_tuple = ()
    parameter_uncertainties_tuple = ()
    reduced_chi_squared_tuple = ()
    predicted_y_data_tuple = ()
    residual_tuple = ()
    outlier_residual_tuple = ()
    nonoutlier_residual_tuple = ()
    
    for i in range(0,comparison_amount):
           
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        #
        
        #
        
        """
        # To add additional models enter a new function in the
        # area below:
        """
        
        #
        
        #
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
        # Defines the model types that may be used by the program
        # Defines linear model function for curve_fit
        if fit_type_tuple[i] in (0, 'linear'):  
            def model_algebra(x, a, b):
                return ( a * x + b )
            fit_algebra = 'a * x + b'
            fit_name = 'linear'
            
        elif fit_type_tuple[i] in (1, 'simple linear'):  
            def model_algebra(x, a):
                return ( a * x )
            fit_algebra = 'a * x'
            fit_name = 'simple linear'
            
            
        # Defines exponential decay model function used by the program
        elif fit_type_tuple[i] in (2, 'exponential decay'):  
            def model_algebra(x,a,b):
                return (a * np.exp( -b * x ))
            fit_algebra = 'a * exp( -b * x )'
            fit_name = 'exponential decay'
            
        # Defines quadratic model function used by the program
        elif fit_type_tuple[i] in (3, 'quadratic'):  
            def model_algebra(x,a,b,c):
                return (a * (x ** 2) + b * x + c)
            fit_algebra = 'a * (x ** 2) + b * x + c'
            fit_name = 'quadratic'
        
        # Defines quadratic model function used by the program
        elif fit_type_tuple[i] in (4, 'poly3'):  
            def model_algebra(x,a,b,c,d):
                return (a * (x ** 3) + b * (x ** 2) + c * x + d)
            fit_algebra = 'a * (x ** 3) + b * (x ** 2) + c * x + d'
            fit_name = '3rd order polynomial'
        
        # Defines quadratic model function used by the program
        elif fit_type_tuple[i] in (5, 'poly4'):  
            def model_algebra(x,a,b,c,d,e):
                return (a * (x ** 4) + b * (x ** 3) + c * (x ** 2) + d * x + e)
            fit_algebra = 'a * (x ** 4) + b * (x ** 3) + c * (x ** 2) + d * x + e'
            fit_name = 'eth order polynomial'
        
        
        # If fit index is entered wrong will end function and tell user
        else:
            print("The fit index you entered does not correspond to a function." +
                  " Please enter a valid number or check you have correctly " +
                  "spelt the name of the fit.")
            return None 
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        #
        
        #
        
        #
        
        #
        
        #
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # Lays out code for an ODR analysis
        if fitting_method_tuple[i] == "odr":
            
            if x_err_tuple[i] is False:
                print("ERROR: x_err tuple invalid for chosen fitting" + 
                      " method")
                return None
                
            # Uses model algebra to construct a function ODR can use
            def model_function(p,x):
                return model_algebra(x, *p)
            
            # Sets model for ODR
            odr_model = odr.Model(model_function)

            # Set data for odr
            data = odr.RealData(x_data_tuple[i], y = y_data_tuple[i], 
                                sx = x_err_tuple[i], sy = y_err_tuple[i])

            # Combines data and model into a single obejct thing
            original_distance_reg = odr.ODR(
                data,odr_model,beta0 = initial_guess)

            # Runs the odr and saves result to a new variable
            odr_output = original_distance_reg.run()

            # Takes important values from the output variable
            parameters_best_guess = odr_output.beta
            reduced_chi_squared = odr_output.res_var
            
            
            #parameter_uncertainties = odr_output.sd_beta
            parameter_uncertainties = np.sqrt(np.diag(odr_output.cov_beta))
            #parameter_uncertainties = np.sqrt(np.diag(odr_output.cov_beta * (odr_output.res_var ** 2)))
            #parameter_uncertainties = np.sqrt((np.diag( (odr_output.cov_beta )) / odr_output.res_var))
            #parameter_uncertainties = np.sqrt(np.diag(odr_output.cov_beta))
            
            parameter_amount = len(initial_guess_tuple[i])
            
            # calculates difference between the y-data and expected values based on 
            # the model using ODR parameters
            expected_difference = np.abs(
                model_function(parameters_best_guess, x_data_tuple[i]) - y_data_tuple[i])
                
            # finds array positions where the difference between model and data is more
            # than the allowed amount of STD * uncertainty
            outlier_positions = np.where( 
                expected_difference > ( outlier_sigma_tuple[i] * y_err_tuple[i] ) )
            
            # Seperates outlier and non-outlier data into new arrays
            outliers_x_data = x_data_tuple[i][outlier_positions]
            outliers_y_data = y_data_tuple[i][outlier_positions]
            
            non_outlier_x_data = np.delete(x_data_tuple[i],outlier_positions)
            non_outlier_y_data = np.delete(y_data_tuple[i],outlier_positions)
            non_outlier_x_err = np.delete(x_err_tuple[i],outlier_positions)
            non_outlier_y_err = np.delete(y_err_tuple[i],outlier_positions)
            
            # Returns answers straight away in specific scenario to reduce
            # lag from the exclude outliers using recursion
            if disable_graph is True and print_answers is False:
                if output_chi is True:
                    return parameters_best_guess, parameter_uncertainties, reduced_chi_squared
                else:
                    return parameters_best_guess, parameter_uncertainties
            
            # Uses recursion to repeat function with only the non-outlier data
            if exclude_outliers is True:
                
                # Gets best guess of the parameters when no outliers are included
                parameters_best_guess, parameter_uncertainties, reduced_chi_squared  = fit(
                    non_outlier_x_data, non_outlier_y_data, 
                    non_outlier_y_err, x_err = non_outlier_x_err, 
                    fit_type = fit_type_tuple[i], 
                    initial_guess = initial_guess_tuple[i], 
                    fitting_method = "odr",
                    disable_graph = True, 
                    output_chi = True, 
                    print_answers = False)
                
            # This section calculates the reduced chi-squared                       
            if output_chi is True:
                
                # Changes data used to calculate the degrees of freedom
                if exclude_outliers is True:
                    chi_x_data = non_outlier_x_data
                else:
                    chi_x_data = x_data_tuple[i]
                    
                degrees_freedom = len(chi_x_data) - parameter_amount
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # If not using odr using curvefit
        else:
            
            # Uses model algebra to construct a function curvefit can use
            def model_function(x, *p):
                return model_algebra(x, *p)
        
            # Uses Curve_fit to estimate the parameters and uncertainty
            # If there are no bounds it is assumed that the fitting method is lm
            if set_bounds is not False:
                parameters_best_guess, parameters_covariance = curve_fit(
                    model_function, x_data_tuple[i], y_data_tuple[i], 
                    p0 = initial_guess_tuple[i],sigma = y_err_tuple[i], 
                    method = fitting_method_tuple[i], 
                    bounds = set_bounds_tuple[i], absolute_sigma=True)
            else:
                parameters_best_guess, parameters_covariance = curve_fit(
                    model_function, x_data_tuple[i], y_data_tuple[i], 
                    p0 = initial_guess_tuple[i], sigma = y_err_tuple[i],
                    absolute_sigma=True)
                
            # aquires number of parameters
            parameter_amount = len(initial_guess_tuple[i])
            
            # calculates difference between the y-data and expected values based on 
            # the model using curve_fit parameters
            expected_difference = np.abs(
                model_function(x_data_tuple[i], *parameters_best_guess) - y_data_tuple[i])
                
            # finds array positions where the difference between model and data is more
            # than the allowed amount of STD * uncertainty
            outlier_positions = np.where( 
                expected_difference > ( outlier_sigma_tuple[i] * y_err_tuple[i] ) )
            
            # Seperates outlier and non-outlier data into new arrays
            outliers_x_data = x_data_tuple[i][outlier_positions]
            outliers_y_data = y_data_tuple[i][outlier_positions]
            
            non_outlier_x_data = np.delete(x_data_tuple[i],outlier_positions)
            non_outlier_y_data = np.delete(y_data_tuple[i],outlier_positions)
            non_outlier_y_err = np.delete(y_err_tuple[i],outlier_positions)
            
            if type(x_err_tuple[i]) in (str,bool,int,tuple,float):
                non_outlier_x_err = False
            else:
                non_outlier_x_err = np.delete(y_err_tuple[i],outlier_positions)
            
            # Calculates the uncertainties of the parameters from the covariance
            # martix
            parameter_uncertainties = (
                np.absolute(np.diag(parameters_covariance))) ** 0.5
    
            # Returns answers straight away in specific scenario to reduce
            # lag from the exclude outliers using recursion
            if disable_graph is True and print_answers is False and output_chi is False:
                return parameters_best_guess, parameter_uncertainties
            
            # Uses recursion to repeat function with only the non-outlier data
            if exclude_outliers is True:
                
                # Gets best guess of the parameters when no outliers are included
                parameters_best_guess, parameter_uncertainties = fit(
                    non_outlier_x_data, non_outlier_y_data, non_outlier_y_err,
                    fit_type = fit_type_tuple[i],
                    initial_guess = initial_guess_tuple[i], disable_graph = True, 
                    output_chi = False, print_answers = False)
                
            # This section calculates the reduced chi-squared                       
            if output_chi is True:
                
                # Changes data used to calculate chi-squared depending on if outliers 
                # are excluded or not
                if exclude_outliers is True:
                    chi_x_data = non_outlier_x_data
                    chi_y_data = non_outlier_y_data
                    chi_y_err = non_outlier_y_err
                else:
                    chi_x_data = x_data_tuple[i]
                    chi_y_data = y_data_tuple[i]
                    chi_y_err = y_err_tuple[i]
                    
                degrees_freedom = len(chi_x_data) - parameter_amount
            
                # Calculates chi-squared
                chi_squared = np.sum((
                    (model_function(chi_x_data, 
                                    *parameters_best_guess) - chi_y_data) ** 2) / (
                        chi_y_err ** 2 ) )
                
                reduced_chi_squared = chi_squared / degrees_freedom
                
                #print((parameter_uncertainties/reduced_chi_squared)) 
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
        # This section prints the answers of the given loop
        # Prints the result of the curve_fit
        if print_answers is True:
            
            # Rounds answers to be ready for printing if user wants it so
            # Starts by creating an empty tuple it then appends rounded answers in 
            # a for loop
            rounded_answers = ( )
            if print_answer_round is True:
                for index in range(0,parameter_amount):
                    temp_rounded_string = round_uncertainty(
                        parameters_best_guess[index],
                        parameter_uncertainties[index])
                    rounded_answers = rounded_answers + (temp_rounded_string,)
            else:
                for index in range(0,parameter_amount):
                    temp_rounded_string = '( {0} ± {1} )'.format(
                        parameters_best_guess[index],
                        parameter_uncertainties[index])
                    rounded_answers = rounded_answers + (temp_rounded_string,)
            
            print("")
            print("--------------------------------------------")
            print("")
            print("For a {0} fit of type '{1}' using fitting method {2}...".format(
                fit_name, fit_algebra, fitting_method_tuple[i]))
            print("")
            print("--------------------------------------------")
            print("")
            print("The calculated parameters were:")
            # Uses for loop to print all the parameters one by one
            for print_counter in range(0,parameter_amount):
                
                # Sets letter of parameter so print statement correctly denotes it
                if print_counter == 0:
                    letter = 'a'
                elif print_counter == 1:
                    letter = 'b'
                elif print_counter == 2:
                    letter = 'c'
                elif print_counter == 3:
                    letter = 'd'
                elif print_counter == 4:
                    letter = 'e'
                elif print_counter == 5:
                    letter = 'f'
                elif print_counter == 6:
                    letter = 'g'
                elif print_counter == 7:
                    letter = 'h'
                elif print_counter == 8:
                    letter = 'i'
                elif print_counter == 9:
                    letter = 'j'
                elif print_counter == 10:
                    letter = 'k'
                elif print_counter == 11:
                    letter = 'l'
                elif print_counter == 12:
                    letter = 'm'
                elif print_counter == 13:
                    letter = 'n'
                elif print_counter == 14:
                    letter = 'o'
                elif print_counter == 15:
                    letter = 'p'
                elif print_counter == 16:
                    letter = 'q'
                elif print_counter == 17:
                    letter = 'r'
                elif print_counter == 18:
                    letter = 's'
                elif print_counter == 19:
                    letter = 't'
                elif print_counter == 20:
                    print("Woah that's a whole lot of parameters you've got there. " +
                          "Firstly, what the fuck? Secondly, if it's absolutelty " + 
                          "integral you have that many parameters, get in touch with " +
                          "Ollie and tell him you need more. Or update the code yourself" +
                          ". It's not really that hard.")
                    return None
                
                print("Parameter {0} is {1}".format(
                    letter, rounded_answers[print_counter]))
                
            # Prints reduced chi_squared
            if output_chi is True:
                
                # Rounds the chi squared if needed
                if print_answer_round is True:
                    chi_string = "{0:.2f}".format(reduced_chi_squared)
                else:
                    chi_string = "{0}".format(reduced_chi_squared)
                
                print("The reduced chi-squared is {0}".format(chi_string))
                print("")
            
            if full_output is True:
                
                # Calculates the maximum chi-squared based on the significance
                # specified in the function, then prints calculated answer
                chi_cdf_significance = (100 - set_significance) / 100
                max_chi = st.chi2.cdf(degrees_freedom,chi_cdf_significance)
                
                if print_answer_round is True:
                    print("The maximum chi-squared acceptance limit for a" + 
                          " significance of {0}% is {1:3}".format(
                              set_significance, max_chi))
                else:
                    print("The maximum chi-squared acceptance limit for a" + 
                          " significance of {0}% is {1}".format(
                              set_significance, max_chi))
            
                # Calculated then prints the R squared value of the model
                if exclude_outliers_tuple[i] is True:
                    R_x_data = non_outlier_x_data
                    R_y_data = non_outlier_y_data
                else:
                    R_x_data = x_data_tuple[i]
                    R_y_data = y_data_tuple[i]
                    
                calculated_residuals = (
                    R_y_data - model_function(R_x_data, *parameters_best_guess))
                calculated_res_sumsquares = np.sum( calculated_residuals ** 2 )
                
                total_sumsquares = np.sum((
                    R_y_data - np.mean(R_y_data) ) ** 2 )
                
                calculated_R_squared = 1 - (
                    calculated_res_sumsquares / total_sumsquares)
                
                if print_answer_round is True:
                    print("The calculated R squared of the model is {0:3}".format(
                        calculated_R_squared))
                else:
                    print("The calculated R squared of the model is {0}".format(
                        calculated_R_squared))
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # Creates a distribution of y points matching the earlier produced 
        # x points
        y_distribution = model_algebra(x_distribution, *parameters_best_guess)
        
        # Finds highest and lowest point of y distribution and updates if next loop gives 
        # higher value
        sorted_y_distribution = np.sort(y_distribution)
        
        y_upper_lim = sorted_y_distribution[-1]
        y_lower_lim = sorted_y_distribution[0]
        y_bounds_difference = y_upper_lim - y_lower_lim
        
        y_dist_max = y_upper_lim + y_bounds_difference * 0.1
        y_dist_min = y_lower_lim - y_bounds_difference * 0.1
        
        if i == 0:
            graph_y_max = y_dist_max
            graph_y_min = y_dist_min
        else:
            if graph_y_max < y_dist_max:
                graph_y_max = y_dist_max
            if graph_y_min > y_dist_min:
                graph_y_min = y_dist_min 
        
        # Finds residuals data for the residuals plot
        predicted_y_data = model_algebra(x_data_tuple[i], *parameters_best_guess)
        residual_data = y_data_tuple[i] - predicted_y_data
        outlier_residual = residual_data[outlier_positions]
        nonoutlier_residual = np.delete(residual_data,outlier_positions)
        
        # Appends results from this loop to the tuples
        y_distribution_tuple = y_distribution_tuple + (y_distribution,)
        non_outlier_x_data_tuple = non_outlier_x_data_tuple + (non_outlier_x_data,)
        non_outlier_y_data_tuple = non_outlier_y_data_tuple + (non_outlier_y_data,)
        non_outlier_x_err_tuple = non_outlier_x_err_tuple + (non_outlier_x_err,)
        non_outlier_y_err_tuple = non_outlier_y_err_tuple + (non_outlier_y_err,)
        outliers_x_data_tuple = outliers_x_data_tuple + (outliers_x_data,)
        outliers_y_data_tuple = outliers_y_data_tuple + (outliers_y_data,)
        parameters_best_guess_tuple = parameters_best_guess_tuple + (parameters_best_guess,)
        parameter_uncertainties_tuple = parameter_uncertainties_tuple + (parameter_uncertainties,)
        reduced_chi_squared_tuple = reduced_chi_squared_tuple + (reduced_chi_squared,)
        predicted_y_data_tuple = predicted_y_data_tuple + (predicted_y_data,)
        residual_tuple = residual_tuple + (residual_data,)
        outlier_residual_tuple = outlier_residual_tuple + (outlier_residual,)
        nonoutlier_residual_tuple = nonoutlier_residual_tuple + (nonoutlier_residual,)
    
    # Code for creating graph
    if disable_graph is False:
        
        # Defines tuples relevant to a scatter plot
        if graph_scatter is True:
            
            # Converts graph_marker into a tuple format
            if type(graph_marker) is tuple:
                graph_marker_tuple = graph_marker
            else:
                graph_marker_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_marker == "default":
                        graph_marker_tuple = graph_marker_tuple + ('x',)
                    else: 
                        graph_marker_tuple = graph_marker_tuple + (graph_marker,)
                    
            # Converts graph_marker_size into a tuple format
            if type(graph_marker_size) is tuple:
                graph_marker_size_tuple = graph_marker_size
            else:
                graph_marker_size_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_marker_size == "default":
                        graph_marker_size_tuple = graph_marker_size_tuple + (20,)
                    else: 
                        graph_marker_size_tuple = graph_marker_size_tuple + (
                            graph_marker_size,)
            
            # Converts graph_marker_thickness into a tuple format
            if type(graph_marker_thickness) is tuple:
                graph_marker_thickness_tuple = graph_marker_thickness
            else:
                graph_marker_thickness_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_marker_thickness == "default":
                        graph_marker_thickness_tuple = (
                            graph_marker_thickness_tuple + (2,))
                    else: 
                        graph_marker_thickness_tuple = (
                            graph_marker_thickness_tuple + (
                                graph_marker_thickness,))
            
            # Converts graph_marker_colour into a tuple format
            if type(graph_marker_colour) is tuple:
                graph_marker_colour_tuple = graph_marker_colour
            else:
                graph_marker_colour_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_marker_colour == "default":
                        graph_marker_colour_tuple = (
                            graph_marker_colour_tuple + ('tab:blue',))
                    else: 
                        graph_marker_colour_tuple = (
                            graph_marker_colour_tuple + (graph_marker_colour,))
            
            # Converts graph_marker_colour into a tuple format
            if type(graph_outlier_colour) is tuple:
                graph_outlier_colour_tuple = graph_outlier_colour
            else:
                graph_outlier_colour_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_outlier_colour == "default":
                        graph_outlier_colour_tuple = (
                            graph_outlier_colour_tuple + ('orange',))
                    else: 
                        graph_outlier_colour_tuple = (
                            graph_outlier_colour_tuple + (graph_outlier_colour,))
            
            # Converts graph_marker_label into a tuple format
            if type(graph_marker_label) is tuple:
                graph_marker_label_tuple = graph_marker_label
            else:
                graph_marker_label_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_marker_label == "default":
                        graph_marker_label_tuple = (
                            graph_marker_label_tuple + ('dataset {0}'.format(
                                (1 + i)),))
                    else: 
                        graph_marker_label_tuple = (
                            graph_marker_label_tuple + (graph_marker_label,))
        
        # Defines tuples relevant to a best fit line
        if graph_fit is True:
        
            # Converts graph_fit_colour into a tuple format
            if type(graph_fit_colour) is tuple:
                graph_fit_colour_tuple = graph_fit_colour
            else:
                graph_fit_colour_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_fit_colour == "default":
                        graph_fit_colour_tuple = (
                            graph_fit_colour_tuple + ('black',))
                    else: 
                        graph_fit_colour_tuple = (
                            graph_fit_colour_tuple + (graph_fit_colour,))
                        
            # Converts graph_fit_alpha into a tuple format
            if type(graph_fit_alpha) is tuple:
                graph_fit_alpha_tuple = graph_fit_alpha
            else:
                graph_fit_alpha_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_fit_alpha == "default":
                        graph_fit_alpha_tuple = (
                            graph_fit_alpha_tuple + (0.6,))
                    else: 
                        graph_fit_alpha_tuple = (
                            graph_fit_alpha_tuple + (graph_fit_alpha,))
                        
            # Converts graph_fit_thickness into a tuple format
            if type(graph_fit_thickness) is tuple:
                graph_fit_thickness_tuple = graph_fit_thickness
            else:
                graph_fit_thickness_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_fit_thickness == "default":
                        graph_fit_thickness_tuple = (
                            graph_fit_thickness_tuple + (2,))
                    else: 
                        graph_fit_thickness_tuple = (
                            graph_fit_thickness_tuple + (graph_fit_thickness,))
            
            # Converts graph_fit_style into a tuple format
            if type(graph_fit_style) is tuple:
                graph_fit_style_tuple = graph_fit_style
            else:
                graph_fit_style_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_fit_style == "default":
                        graph_fit_style_tuple = (
                            graph_fit_style_tuple + ('solid',))
                    else: 
                        graph_fit_style_tuple = (
                            graph_fit_style_tuple + (graph_fit_style,))
                    
            # Converts graph_fit_name into a tuple format
            if type(graph_fit_name) is tuple:
                graph_fit_name_tuple = graph_fit_name
            else:
                graph_fit_name_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_fit_name == "default":
                        graph_fit_name_tuple = (
                            graph_fit_name_tuple + ('Predicted fit {0}'.format(
                                (1 + i)),))
                    else: 
                        graph_fit_name_tuple = (
                            graph_fit_name_tuple + (graph_fit_name,))
        
        # Defines tuples relevant to a errorbars
        if graph_error is True:
            
            # Converts graph_error_colour into a tuple format
            if type(graph_error_colour) is tuple:
                graph_error_colour_tuple = graph_error_colour
            else:
                graph_error_colour_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_error_colour == "default":
                        graph_error_colour_tuple = (
                            graph_error_colour_tuple + ('red',))
                    else: 
                        graph_error_colour_tuple = (
                            graph_error_colour_tuple + (graph_error_colour,))
                        
            # Converts graph_error_thickness into a tuple format
            if type(graph_error_thickness) is tuple:
                graph_error_thickness_tuple = graph_error_thickness
            else:
                graph_error_thickness_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_error_thickness == "default":
                        graph_error_thickness_tuple = (
                            graph_error_thickness_tuple + (1,))
                    else: 
                        graph_error_thickness_tuple = (
                            graph_error_thickness_tuple + (
                                graph_error_thickness,))
                        
            # Converts graph_error_colour into a tuple format
            if type(graph_error_cap_size) is tuple:
                graph_error_cap_size_tuple = graph_error_cap_size
            else:
                graph_error_cap_size_tuple = ()    
                for i in range(0,comparison_amount):
                    if graph_error_cap_size == "default":
                        graph_error_cap_size_tuple = (
                            graph_error_cap_size_tuple + (0,))
                    else: 
                        graph_error_cap_size_tuple = (
                            graph_error_cap_size_tuple + (
                                graph_error_cap_size,))
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # Gets to work creating graph
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        #changes font size
        plt.rcParams.update({'font.size':graph_font_size})
        
        # Creates the figure/plot object
        if residuals is True:
            # sets dimensions of figure
            output_figure = plt.figure(0)
            output_figure.set_figheight(6)
            output_figure.set_figwidth(9)
            
            # sets layout of the subplots on the figure
            model_plot = plt.subplot2grid(
                shape=(3, 1), loc=(0, 0), rowspan=2)
            axes_residuals = plt.subplot2grid(
                shape=(3, 1), loc=(2, 0), rowspan=1)
            
        else:
            output_figure = plt.figure(0)
            model_plot = output_figure.add_subplot(111)
            
        # Plots labels on the figure
        try:
            model_plot.set_xlabel(graph_xlabel)
            model_plot.set_ylabel(graph_ylabel)
            model_plot.set_title(graph_title)
        except:
            print("")
            print("ERROR: Plot title/ x-label / y-label not recognised or " + 
                  "string. Using default bounds.")
            model_plot.set_xlabel("Independent Variable")
            model_plot.set_ylabel("Dependent Variable")
            model_plot.set_title("Graph Title")
            
        # Sets bounds for the graphs
        try:
            x_lower_lim = graph_bounds[0,0]
            x_upper_lim = graph_bounds[0,1]
            y_lower_lim = graph_bounds[1,0]
            y_upper_lim = graph_bounds[1,1]
            
            model_plot.set_xlim([x_lower_lim,x_upper_lim])
            model_plot.set_ylim([y_lower_lim,y_upper_lim])
        except:
            if not graph_bounds == "default":
                print("")
                print("The format of bounds given was not recognised. Using" +
                      " the default option instead.")
            
            model_plot.set_xlim([x_dist_start, x_dist_end])
            model_plot.set_ylim([graph_y_min, graph_y_max])
            
        # Adds a grid to the background of the graph
        if graph_grid is True:
            model_plot.grid(True, color='grey', dashes=(4, 2), zorder = 0)
        
        # Plots residuals on the graph
        if residuals is True:
            
            # Sets x axis same as rest of graph
            try:
                axes_residuals.set_xlabel(graph_xlabel)
            except:
                axes_residuals.set_xlabel("Independent Variable")
            
            # sets bounds for x axis
            try:
                axes_residuals.set_xlim([x_lower_lim,x_upper_lim])
                lower_x = x_lower_lim
                upper_x = x_upper_lim
            except:
                axes_residuals.set_xlim(
                    [x_dist_start, x_dist_end])
                lower_x = x_dist_start
                upper_x = x_dist_end
            
            # sets title for residuals graph
            axes_residuals.set_title("Residuals")
            
            # sets y axis to be a log scale if user wants it
            if residuals_log_scale is True:
                axes_residuals.set_yscale('log')
            
            # plots grid on residual
            if graph_grid is True:
                axes_residuals.grid(
                    True, color='grey', dashes=(4, 2), zorder = 0)
                
            # plots a straight line through centre of residuals graph
            axes_residuals.plot([lower_x,upper_x], [0,0], 
                            color = graph_fit_colour_tuple[0], alpha = graph_fit_alpha_tuple[0],
                            linewidth = graph_fit_thickness_tuple[0], 
                            linestyle = graph_fit_style_tuple[0], zorder = 2)
        
        # For loop plots all components on a graph
        for i in range (0,comparison_amount):
            z_order_multiplier = (i+1) * 7
            
            # Adds x_data as a scatter plot to the graph
            if graph_scatter is True:
                
                # Assigns data for the scatter / error plot depending on if 
                # outliers are excluded / highlighted / included.
                if exclude_outliers_tuple[i] is True:
                    scatter_x_data = non_outlier_x_data_tuple[i]
                    scatter_y_data = non_outlier_y_data_tuple[i]
                    
                    if highlight_outliers is True:
                        outlier_scatter_x_data = outliers_x_data_tuple[i]
                        outlier_scatter_y_data = outliers_y_data_tuple[i]
                        
                        if graph_error is True:
                            error_y_data = y_err_tuple[i]
                            error_x_position = x_data_tuple[i]
                            error_y_position = y_data_tuple[i]
                            
                            if x_err_tuple[i] is False:
                                pass
                            else:
                                error_x_data = x_err_tuple[i]
                    
                    elif graph_error is True and highlight_outliers is False:
                        error_y_data = non_outlier_y_err_tuple[i]
                        error_x_position = non_outlier_x_data_tuple[i]
                        error_y_position = non_outlier_y_data_tuple[i]
                        
                elif exclude_outliers_tuple[i] is False and highlight_outliers is True:
                    scatter_x_data = non_outlier_x_data_tuple[i]
                    scatter_y_data = non_outlier_y_data_tuple[i]
                    
                    outlier_scatter_x_data = outliers_x_data_tuple[i]
                    outlier_scatter_y_data = outliers_y_data_tuple[i]
                    
                    if graph_error is True:
                        error_y_data = y_err_tuple[i]
                        error_x_position = x_data_tuple[i]
                        error_y_position = y_data_tuple[i]
                        
                        if x_err_tuple[i] is False:
                            pass
                        else:
                            error_x_data = x_err_tuple[i]
                            
                else:
                    scatter_x_data = x_data_tuple[i]
                    scatter_y_data = y_data_tuple[i]
                    
                    if graph_error is True:
                        error_y_data = y_err_tuple[i]
                        error_x_position = x_data_tuple[i]
                        error_y_position = y_data_tuple[i]
                        
                        if x_err_tuple[i] is False:
                            pass
                        else:
                            error_x_data = x_err_tuple[i]
                
                if True in (is_x_data_tuple, is_y_data_tuple, is_y_err_tuple, 
                            is_x_err_tuple, is_exclude_outliers_tuple):
                    
                    if highlight_outliers is True:
                        
                        scatter_outlier_z = z_order_multiplier + 4                      
                        outlier_label = graph_marker_label_tuple[i] + " Outliers"                       
                        model_plot.scatter(outlier_scatter_x_data,
                                           outlier_scatter_y_data, 
                                           marker = graph_marker_tuple[i], s=graph_marker_size_tuple[i],
                                           linewidths = graph_marker_thickness_tuple[i], 
                                           color = graph_outlier_colour_tuple[i], 
                                           label = outlier_label, zorder = scatter_outlier_z)
                        
                    scatter_data_z = z_order_multiplier + 5
                    data_label = graph_marker_label_tuple[i] + " data"
                    model_plot.scatter(scatter_x_data, scatter_y_data,
                                       marker = graph_marker_tuple[i], s=graph_marker_size_tuple[i],
                                       linewidths = graph_marker_thickness_tuple[i], 
                                       color = graph_marker_colour_tuple[i],
                                       label = data_label, zorder = scatter_data_z)
                    
                    # Plots errorbar data if enabled
                    if graph_error is True:
                        
                        error_z = z_order_multiplier + 6
                        
                        try: 
                            x_err_tuple[i][0]
                            model_plot.errorbar(error_x_position, error_y_position, 
                                                xerr = error_x_data, yerr = error_y_data, 
                                                fmt='x', markersize=0,
                                                ecolor = graph_error_colour_tuple[i],
                                                elinewidth = graph_error_thickness_tuple[i],
                                                capsize = graph_error_cap_size_tuple[i],
                                                zorder = error_z)
                        except:
                            model_plot.errorbar(error_x_position, error_y_position, 
                                                error_y_data, fmt='x', markersize=0,
                                                ecolor = graph_error_colour_tuple[i],
                                                elinewidth = graph_error_thickness_tuple[i],
                                                capsize = graph_error_cap_size_tuple[i],
                                                zorder = error_z)
                    
                    
                else:
                    if i == 0:
                        # Plots the scatter points on the plot
                        if highlight_outliers is True:

                            scatter_outlier_z = z_order_multiplier + 4                      
                            outlier_label = graph_marker_label_tuple[i] + " Outliers"                       
                            model_plot.scatter(outlier_scatter_x_data,
                                               outlier_scatter_y_data, 
                                               marker = graph_marker_tuple[i], s=graph_marker_size_tuple[i],
                                               linewidths = graph_marker_thickness_tuple[i], 
                                               color = graph_outlier_colour_tuple[i], 
                                               label = outlier_label, zorder = scatter_outlier_z)
                            
                        scatter_data_z = z_order_multiplier + 5
                        data_label = graph_marker_label_tuple[i] + " data"
                        model_plot.scatter(scatter_x_data, scatter_y_data,
                                           marker = graph_marker_tuple[i], s=graph_marker_size_tuple[i],
                                           linewidths = graph_marker_thickness_tuple[i], 
                                           color = graph_marker_colour_tuple[i],
                                           label = data_label, zorder = scatter_data_z)
                        
                        # Plots errorbar data if enabled
                        if graph_error is True:
                            
                            error_z = z_order_multiplier + 6
                            
                            try: 
                                x_err_tuple[i][0]
                                model_plot.errorbar(error_x_position, error_y_position, 
                                                    xerr = error_x_data, yerr = error_y_data, 
                                                    fmt='x', markersize=0,
                                                    ecolor = graph_error_colour_tuple[i],
                                                    elinewidth = graph_error_thickness_tuple[i],
                                                    capsize = graph_error_cap_size_tuple[i],
                                                    zorder = error_z)
                            except:
                                model_plot.errorbar(error_x_position, error_y_position, 
                                                    error_y_data, fmt='x', markersize=0,
                                                    ecolor = graph_error_colour_tuple[i],
                                                    elinewidth = graph_error_thickness_tuple[i],
                                                    capsize = graph_error_cap_size_tuple[i],
                                                    zorder = error_z)
                                
            if graph_fit is True:
                
                plot_z = z_order_multiplier + 2
                model_plot.plot(x_distribution, y_distribution_tuple[i], 
                                color = graph_fit_colour_tuple[i], alpha = graph_fit_alpha_tuple[i],
                                linewidth = graph_fit_thickness_tuple[i], 
                                linestyle = graph_fit_style_tuple[i], 
                                label = graph_fit_name_tuple[i], zorder = plot_z)
            
            if residuals is True:
                
                if graph_error is True:
                    
                    res_error_z = z_order_multiplier + 5
                    
                    if exclude_outliers_tuple[i] is True and highlight_outliers is False:
                        axes_residuals.errorbar(
                            non_outlier_x_data_tuple[i], 
                            nonoutlier_residual_tuple[i], 
                            non_outlier_y_err_tuple[i],
                            fmt='x', markersize=0,
                            ecolor = graph_error_colour_tuple[i],
                            elinewidth = graph_error_thickness_tuple[i],
                            capsize = graph_error_cap_size_tuple[i],
                            zorder = res_error_z)
                    else:
                        axes_residuals.errorbar(
                            x_data_tuple[i], 
                            residual_tuple[i], 
                            y_err_tuple[i],
                            fmt='x', markersize=0,
                            ecolor = graph_error_colour_tuple[i],
                            elinewidth = graph_error_thickness_tuple[i],
                            capsize = graph_error_cap_size_tuple[i],
                            zorder = res_error_z)
                    
                    
                res_non_outlier_z = z_order_multiplier + 3
                
                # plots residual scatter data for non-outliers
                axes_residuals.scatter(non_outlier_x_data_tuple[i], 
                                       nonoutlier_residual_tuple[i],
                                   marker = graph_marker_tuple[i],
                                   s=graph_marker_size_tuple[i],
                                   linewidths = graph_marker_thickness_tuple[i], 
                                   color = graph_marker_colour_tuple[i], 
                                   zorder = res_non_outlier_z)
                    
                if highlight_outliers is True:
                    
                    res_outlier_z = z_order_multiplier + 4
                    
                    # plots residual scatter data for outliers
                    axes_residuals.scatter(outliers_x_data_tuple[i], 
                                           outlier_residual_tuple[i],
                                       marker = graph_marker_tuple[i],
                                       s=graph_marker_size_tuple[i],
                                       linewidths = graph_marker_thickness_tuple[i], 
                                       color = graph_outlier_colour_tuple[i], 
                                       zorder = res_non_outlier_z)
                    
                elif exclude_outliers_tuple[i] is False:
                    
                    res_outlier_z = z_order_multiplier + 4
                    
                    # plots residual scatter data for outliers, in this case colour is
                    # same as non-outliers
                    axes_residuals.scatter(outliers_x_data_tuple[i], 
                                           outlier_residual_tuple[i],
                                       marker = graph_marker_tuple[i],
                                       s=graph_marker_size_tuple[i],
                                       linewidths = graph_marker_thickness_tuple[i], 
                                       color = graph_marker_colour_tuple[i], 
                                       zorder = res_outlier_z)
                    
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # End of Loop Here
            
        # Plots a legend for the graph
        if graph_legend is True:
            
            # Checks for location response and plots in default area if
            # location info is invalid or given as default
            if graph_legend_location == "default":
                model_plot.legend()
            
            else:
                possible_legend_locations = (
                    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'best', 'upper right',
                    'upper left', 'upper center', 'center left', 'center',
                    'center right', 'lower left', 'lower_right', 
                    'lower center')
                
                if graph_legend_location in possible_legend_locations:
                    model_plot.legend(loc = graph_legend_location)
                
                else:
                    print("")
                    print("The legend location information was not " + 
                          "recognised, therefore the location was set to" + 
                          " default ('best').")
                    model_plot.legend()
        
        output_figure.tight_layout()
        
        model_png_filename = graph_filename + '.png'
        
        output_figure.savefig(model_png_filename, dpi = graph_dpi, 
                              bbox_inches = "tight")
        plt.show()
        plt.close(output_figure)
    
    if function_returns is True:
        
        # Based on function variables returns requested values
        if output_chi is True:
            return (parameters_best_guess_tuple, parameter_uncertainties_tuple, 
                    reduced_chi_squared_tuple)
        else:
            return parameters_best_guess_tuple, parameter_uncertainties_tuple
        
    else:
        return None
        
        
        
                
                
            
                
                
                    
                    
                
            
            
            
        
                
            
    