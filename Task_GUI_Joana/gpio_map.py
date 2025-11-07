# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 18:41:05 2024

@author: JoanaCatarino

- Gpio map (pin numbers should be reproduced across boxes):
    - defines which devices are connect to the different pins in the raspberry pi
    - the following GPIO map is used throughout all the task scripts to send and receive information and to make the different task elements possible
    
- The following pins are reserved for the HiFiBerry Amp2 and cannot be reassigned:
    - GPIO18, GPIO19, GPIO21 (I²S audio communication).
    - 5V pins (Pins 2 and 4) and ground pins used for power (Pin 6).
    - GPIO2 and GPIO3 if the Amp2 uses I²C for additional functions like EEPROM or configuration.
"""

from gpiozero import LED, Button, OutputDevice, Device


# Real GPIO map for all the rig/task components
led_white_r = LED(26) #GND 39
led_white_l = LED(23) #GND 25
led_blue = LED(17) #GND 9
pump_l = OutputDevice(22) #no GND
pump_r = OutputDevice(27) #no GND
laser = OutputDevice(24) #no GND and only ephys (confirm this??) - red laser for optotagging
ttl_blue = LED(25) #DI4 nidq
ttl_stim = LED(16) #DI5 nidq
ttl_reward = LED(5) #DI7 nidq
ttl_punishment = LED(6) #DI6 nidq

# needs to be updated with the different pin numbers for the Grounds that are being used

# Updated all
__all__= ['led_white_l', 'led_white_r', 'led_blue', 'pump_l', 'pump_r', 'laser', 'ttl_blue', 'ttl_stim', 'ttl_reward', 'ttl_punishment']