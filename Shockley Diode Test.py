# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 20:46:26 2024

@author: Oliver
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as co
from scipy.constants import physical_constants as pyc

K = co.Boltzmann
q = co.elementary_charge
T_BC = 100
n_BC = 0.11866
n_IN = 0.053686
C_334 = 0.227
Is_BC = 0.1
Is_IN = 5
Id_IN = 6
R1 = 11147
R2 = 121578
K_ev = (pyc['Boltzmann constant in eV/K'][0])

def output_voltage(T_IN,C_IN):
    prefactor = (K * T_BC) / (q * n_BC)
    R1R2_ratio = (C_IN-C_334) / C_334
    VD_per_k = (C_334 + (K / ( q * n_IN)) * np.log((Id_IN / Is_IN) + 1)) / ((R1R2_ratio) *(R1))
    log_term = np.log( ( (T_IN / Is_BC) * ( (C_334 / R1) + VD_per_k) ) * 1000 + 1 )
    V_measured = prefactor * log_term
    return V_measured

T_IN_range = np.linspace(280,305,1000)
V_measured_array = output_voltage(300,2.5)
C_IN_val = 3.15
R1 = 11147
R2 = 121578
#V_measured_array = output_voltage(T_IN_range,C_IN_val)



def sat_curr(original_is,original_is_temp,new_temp):
    new_current = original_is * ((new_temp/original_is_temp) ** 3) * (
        np.exp( (1.1 / K_ev) * (1/original_is_temp - 1/new_temp) ))
    return new_current

def diode_voltage(temperature,diode_current,saturation_current, saturation_current_temperature,ideality):
    voltage_drop = ((K * temperature) / (q * ideality)) * np.log(
        (diode_current / sat_curr(
            saturation_current, saturation_current_temperature, temperature)) + 1)
    return voltage_drop

def find_R2(I_out_des, tempco_lm, tempco_in, IN_temp, IN_current, IN_sat, IN_sat_temp, IN_ideality):
    r2r1_ratio = (tempco_in - tempco_lm) / tempco_lm
    r2 = (1/I_out_des) * (
        tempco_lm * IN_temp * (r2r1_ratio + 1) + diode_voltage(IN_temp,IN_current,IN_sat,IN_sat_temp,IN_ideality))
    return r2

def find_R1(I_out_des, tempco_lm, tempco_in, IN_temp, IN_current, IN_sat, IN_sat_temp, IN_ideality):
    r2r1_ratio = (tempco_in - tempco_lm) / tempco_lm
    r1 = (1/I_out_des) * (
        tempco_lm * IN_temp + (tempco_lm * IN_temp + diode_voltage(
            IN_temp,IN_current,IN_sat,IN_sat_temp,IN_ideality)) / r2r1_ratio)
    return r1

def find_Iset(IN_temp,assumed_tempco_IN, true_tempco_IN, tempco_lm, I_out_des, IN_current, IN_sat, IN_sat_temp, IN_ideality, IN_fit_c):
    assumed_r1r2_ratio = (assumed_tempco_IN - tempco_lm) / tempco_lm
    Iset = (IN_temp *  (tempco_lm / find_R1(
        I_out_des, tempco_lm, assumed_tempco_IN, IN_temp,
        IN_current, IN_sat, IN_sat_temp, IN_ideality)) + (
            (IN_temp * tempco_lm +  IN_temp * (-true_tempco_IN) + IN_fit_c  ) / find_R2(I_out_des, tempco_lm, assumed_tempco_IN, IN_temp, IN_current, IN_sat, IN_sat_temp, IN_ideality)))
            
print(find_Iset(295, 10000, 3.15, 0.227, 10, 6, 5, 298.15, n_IN, 1.2792))
    
    
    
print(sat_curr(5,298.15,(273.15+25)))
print(diode_voltage(100,6,5,298.15,n_IN))
