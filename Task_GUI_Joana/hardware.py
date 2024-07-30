# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 16:17:34 2024

@author: JoanaCatarino

IMP:
In this file we should do the pin map and also the functions map
the pin map will tell the location for all the components connected
to the raspberry pi while the function map will have the commands that execute
the different functions.

All the functions that I need to run the task will then be called in this script

"""
# =============================================================================
# 
# xiao's code
# from gpiozero import LED 
# from time import sleep 
# import asyncio
# 
# 
# class FunctionMap:
#     def __init__(self):
#         self.led = False
#         
# 
#     def led_blue(self): 
#         self.led = True
#         print ('LED is ON')
#         sleep(1)
#         self.led = False
#         print('LED id Off')
# =============================================================================
 
from gpiozero import LED
from time import sleep
import asyncio

# Functions to import
from gpio_map import * # Import everything from gpio map (all the pins)
from sound_generator import tone_10KHz, tone_5KHz, white_noise
from task_test_rig import led_blue_action, led_white_l_action, led_white_r_action

# Function map - gives a command name to every function needed
function_map = {
    'led_blue': led_blue_action
    'led_white_l': led_white_l_action,
    'led_white_r': led_white_r_action,
    'tone_10khz': tone_10KHz,
    'tone_5khz': tone_5KHz,
    'white_noise': white_noise
    }

 
class FunctionMap:
    def __init__(self):
        self.function_map = function_map
        
    async def execute_command(self, command):
        if command in self.function_map:
            await self.function_map[command]()
        else:
            print(f'Command {command} not found')



