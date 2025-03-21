#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 17:20:25 2024

@author: valentinsauvage
"""

def ohm_law(current = 0 , power = 0 , voltage = 0, resistance = 0):
    
    if current != 0 and power != 0:
        
        voltage = power/current
        resistance = power/current**2
        
    if current != 0 and voltage != 0:
        
        power = current*voltage
        resistance = voltage/current
        
    if current != 0 and resistance != 0:
        
        power = resistance*current**2
        voltage = resistance*current
        
    if power != 0 and voltage != 0:
        
        current = power/voltage
        resistance = voltage**2/power
        
    if power != 0 and resistance != 0:
        
        current = (power/resistance)**0.5
        voltage = (power*resistance)**0.5
        
    if voltage != 0 and resistance != 0:
        
        current = voltage/resistance
        power = voltage**2/resistance
        
    print('')
    print('Current      = ' + str(current) + ' A')
    print('Voltage      = ' + str(voltage) + ' V')
    print('Power        = ' + str(power) + ' W')
    print('Resistance   = ' + str(resistance) + ' Ohms')

        
    return current, voltage, power, resistance 




