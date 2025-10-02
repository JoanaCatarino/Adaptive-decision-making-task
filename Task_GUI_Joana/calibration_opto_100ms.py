# -*- coding: utf-8 -*-
"""
Created on Thu Oct  2 09:57:54 2025

@author: JoanaCatarino
"""

from gpio_map import *
import time

def calibration_opto_100ms():
    quant=30 # 30 pulses just to test
    pulse_duration = 0.1  # 100ms
    interval_off = 1-pulse_duration # one pulse of 100ms per second
    
    for i in range(quant):
        
        print(f'pulse {i+1}/{quant}')
        laser.on()
        time.sleep(pulse_duration)
        laser.off()
        time.sleep(interval_off)
        
    print('Finished calibration for Opto 100ms')