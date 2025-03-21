#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt



def plot(ARRAY_x,ARRAY_y,xlabel,ylabel,grid,xscale,yscale,title):
    
    plt.figure()
    plt.plot(ARRAY_x,ARRAY_y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(grid)
    plt.xscale(xscale)
    plt.yscale(yscale)
    plt.title(title)