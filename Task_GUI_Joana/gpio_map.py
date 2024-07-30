# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 18:41:05 2024

@author: JoanaCatarino
"""

from gpiozero import LED

# Gpio map (pin numbers should be reproduced across boxes)

led_blue = LED(22)


# Specify which names to export when 'from gpio_pins import *' is used
__all__ = ['led_blue']
