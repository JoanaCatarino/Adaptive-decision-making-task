# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 18:41:05 2024

@author: JoanaCatarino
"""

from gpiozero import LED, Button

# Gpio map (pin numbers should be reproduced across boxes)

led_blue = LED (22)
#led_white_L = LED()
#led_white_R = LED()
#button_reward = Button ()


# Specify which names to export when 'from gpio_pins import *' is used
__all__ = ['led_blue', 'led_white_L', 'led_white_R', 'button_reward']
