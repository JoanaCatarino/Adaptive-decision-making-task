# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 10:30:50 2025

@author: JoanaCatarino

file to try to do the led sequence

"""

import asyncio
from gpio_map import *
from gpiozero import LED
from time import sleep
from sound_generator import tone_10KHz, tone_5KHz, white_noise
from form_updt import Ui_TaskGui
from qasync import asyncSlot  # Import asyncSlot decorator


async def blink_led_sequence(leds, cycles=3, on_time=1, off_time=1):
    
    '''
    Blink a list of leds in a sequence
    
    Args:
    - leds (list): List of LED GPIO pins
    - cycles (int): Number of times the sequence should repeat
    - on_time (float): Duration for which each LED stays ON
    - off_time (float): Duration for which each LED stays OFF
    '''
    
    for _ in range (cycles):
        for led in leds:
            led.on()
            await asyncio.sleep(on_time)
            led.off()
            await asyncio.sleep(off_tme)
            
            
@asyncSlot()
async def start_led_sequence(self):
    '''
    Start the LED blink sequence when the blue led button is clicked
    '''
    print ('Starting LED sequence...')
            
    await blink_led_sequence(self.leds, cycles=5, on_time=0.5, off_time=0.5)               
        
        