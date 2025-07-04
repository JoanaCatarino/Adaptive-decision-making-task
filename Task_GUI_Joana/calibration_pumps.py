# -*- coding: utf-8 -*-
"""
Created on Fri Jul  4 13:11:30 2025

@author: JoanaCatarino
"""

from gpio_map import *
from sound_generator import tone_8KHz
import time

def calibration_pumps():
    quant=100
    flush_duration = 0.079
    
    for i in range(quant):
        
        pump_l.off()
        pump_r.off()
        
        time.sleep(flush_duration)
        
        pump_l.on()
        pump_r.on()
        
        time.sleep(1) # one second of interval between flushes
        
    tone_8KHz()    
    print('Finished calibration')    