# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 18:41:05 2024

@author: JoanaCatarino
"""

from gpiozero import LED

# Gpio map (pin numbers should be reproduced across boxes) - Pin numbers should be changed when the rig is being built

led_blue = LED(22)
led_white_l = LED(5)
led_white_r = LED(6)

# Specify which names to export when 'from gpio_pins import *' is used
__all__ = ['led_blue', 'led_white_l', 'led_white_r']
