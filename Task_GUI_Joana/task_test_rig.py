# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:32:26 2024

@author: JoanaCatarino

Test rig script
- Start this task should enable the buttons that allow to test different rig components
- All the functions connected to commands related to sound (tones and white noise) should be directly imported 
from the sound_generator file. 
- Functions to test LEDs (blue and white) are generated here
- Functions to flush water are generated here with some components imported from file x
"""
# virtual pin factory
from gpiozero.pins.mock import MockFactory
from gpiozero import Device
Device.pin_factory = MockFactory()


import asyncio
from gpio_map import *
from sound_generator import tone_10KHz, tone_5KHz, white_noise


class TestRig:
    def __init__(self, ui):
        self.ui = ui

    def start(self):
        print('Test rig starting')
        self.ui.Box1_10Tone.clicked.connect(tone_10KHz)
        self.ui.Box1_5Tone.clicked.connect(tone_5KHz)
        self.ui.Box1_Punishment.clicked.connect(white_noise)

        def stop():
            print('Test rig stopping')
            self.ui.Box1_10Tone.clicked.disconnect(tone_10KHz)
            self.ui.Box1_5Tone.clicked.disconnect(tone_5KHz)
            self.ui.Box1_Punishment.clicked.disconnect(white_noise)

        self.stop = stop
        
# Test blue LED
async def led_blue_action():
    led_blue.on()
    await asyncio.sleep(1)
    led_blue.off() 
    
# Test white LED on left spout
async def led_white_l_action():
    led_white_l.on()
    await asyncio.sleep(1)
    led_white_l.off() 
 
# Test white LED on right spout
async def led_white_r_action():
    led_white_r.on()
    await asyncio.sleep(1)
    led_white_r.off() 
    
    
# Need to define functions to flush water on right spout and left spout
    