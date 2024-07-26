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

from gpiozero import LED
from time import sleep
import asyncio

# Gpio map
led_blue = LED (22)
led_red = LED(26)

# Define actions for different commands 
async def led_blue_action():
    while True:
        led.on()
        sleep(1)
        led.off()
        sleep(1)


'''
async def led_blue_action():
    led_blue.on()
    await asyncio.sleep(1)
    led_blue.off()    
'''    
async def led_red_action():
    led_red.on()
    await asyncio.sleep(1)
    led_red.off()  


# Function map - gives a command name to every function needed
function_map = {
    'led_blue': led_blue_action,
    'led_red': led_red_action}