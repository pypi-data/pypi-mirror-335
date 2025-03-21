#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 17:06:23 2024

@author: valentinsauvage
"""

#%%
def normal_liter_to_liter(temperature,pressure,value):
    return value * 101325/pressure * 273.15/temperature

def standard_liter_to_liter(temperature,pressure,value):
    return value * 101325/pressure * 288.15/temperature

