# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 18:41:05 2024

@author: JoanaCatarino
"""

from gpiozero import LED, Button, OutputDevice, Device

# Gpio map (pin numbers should be reproduced across boxes) - Pin numbers should be changed when the rig is being built
#The following pins are reserved for the HiFiBerry Amp2 and cannot be reassigned:

#GPIO18, GPIO19, GPIO21 (I²S audio communication).
#5V pins (Pins 2 and 4) and ground pins used for power (Pin 6).
#GPIO2 and GPIO3 if the Amp2 uses I²C for additional functions like EEPROM or configuration.


# Real GPIO map for all the rig/task components
led_white_l = LED(26) #GND 39
led_white_r = LED(11) #GND 25
led_blue = LED(17) #GND 9
pump_l = OutputDevice(22) #no GND
pump_r = OutputDevice(27) #no GND
laser = OutputDevice(24) #no GND and only ephys
btn_l = Button(1) #GND 30
btn_r = Button(16) #GND 34


# Specify which names to export when 'from gpio_pins import *' is used
#__all__ = ['led_blue', 'led_red', 'led_white_l', 'led_white_r', 'button_blue', 'button_red']

# Updated all
__all__= ['led_white_l', 'led_white_r', 'led_blue', 'pump_l', 'pump_r', 'laser', 'btn_l', 'btn_r']