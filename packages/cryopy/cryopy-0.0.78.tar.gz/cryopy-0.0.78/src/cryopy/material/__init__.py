#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

def plot_single(ARRAY_x,ARRAY_y,xlabel,ylabel,grid,xscale,yscale,title):
    
    plt.figure()
    plot(ARRAY_x,ARRAY_y,label='')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(grid)
    plt.xscale(xscale)
    plt.yscale(yscale)
    plt.title(title)
    
    
    
def plot(ARRAY_x,ARRAY_y,label=''):
    plt.plot(ARRAY_x,ARRAY_y,label = label)
    
    
    
def plot_multiple(ARRAY_ARRAY_x,ARRAY_ARRAY_y,ARRAY_label,xlabel,ylabel,grid,xscale,yscale,title):
    
    plt.figure()
    for i in range(len(ARRAY_ARRAY_x)):
        ARRAY_x = ARRAY_ARRAY_x[i]
        ARRAY_y = ARRAY_ARRAY_y[i]
        label = ARRAY_label[i]
        
        plot(ARRAY_x,ARRAY_y,label=label)
        
    plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(grid)
    plt.xscale(xscale)
    plt.yscale(yscale)
    plt.title(title)
    
    
    
    
    
    
    