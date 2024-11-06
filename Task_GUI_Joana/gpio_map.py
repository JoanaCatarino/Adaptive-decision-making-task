# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 18:41:05 2024

@author: JoanaCatarino
"""

from gpiozero import LED, Button, OutputDevice

# Gpio map (pin numbers should be reproduced across boxes) - Pin numbers should be changed when the rig is being built

led_blue = LED(22)
led_red = LED(25) # Free licking script with buttons
led_white_l = LED(5)
led_white_r = LED(6)
button_blue = Button(26) # Free licking script with buttons
button_red = Button(16) # Free licking script with buttons
#pump = OutputDevice(26) this is the module we use to connect the pumps


# Real GPIO map for all the rig/task components
#led_white_l = LED(26) #GND 39
#led_white_r = LED(11) #GND 25
#led_blue = LED(17) #GND 9
#pump_l = OutputDevice(14) #no GND
#pump_r = OutputDevice(18) #no GND
#laser = OutputDevice(24) #no GND and only ephys
#btn_l = Button(1) #GND 30
#btn_r = Button(16) #GND 34


# Specify which names to export when 'from gpio_pins import *' is used
__all__ = ['led_blue', 'led_red', 'led_white_l', 'led_white_r', 'button_blue', 'button_red']

# Updated all
#__all__= ['led_white_l', 'led_white_r', 'led_blue', 'pump_l', 'pump_r', 'laser', 'btn_l', 'btn_r']
