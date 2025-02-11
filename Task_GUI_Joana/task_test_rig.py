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

import asyncio
from gpio_map import *
from gpiozero import LED
from time import sleep
from sound_generator import tone_10KHz, tone_5KHz, white_noise
from form_updt import Ui_TaskGui
from qasync import asyncSlot  # Import asyncSlot decorator

        
class TestRig:
    def __init__(self, ui):
        self.ui = ui
            
        self.start()
        
    # Test white LED on right spout
    def pumpR():
        pump_r.off()
        sleep(0.5)
        pump_r.on()
        
    def play_10KHz(self):
        print("Playing 10KHz Tone")
        tone_10KHz()

    def play_5KHz(self):
        print("Playing 5KHz Tone")
        tone_5KHz()

    def play_white_noise(self):
        print("Playing White Noise")
        white_noise()


    def start(self):
        
        pump_l.on()
        pump_r.on()
        
        print('Test rig starting')
        self.ui.chk_10Tone.clicked.disconnect()
        self.ui.chk_10Tone.clicked.connect(self.play_10KHz)
        self.ui.chk_5Tone.clicked.disconnect()
        self.ui.chk_5Tone.clicked.connect(self.play_5KHz)
        self.ui.chk_Punishment.clicked.disconnect()
        self.ui.chk_Punishment.clicked.connect(self.play_white_noise)
        self.ui.chk_BlueLED.clicked.connect(blueLED)
        self.ui.chk_WhiteLED_Left.clicked.connect(whiteLLED)
        self.ui.chk_WhiteLED_Right.clicked.connect(whiteRLED)
        self.ui.chk_Reward_left.clicked.connect(pumpL)
        self.ui.chk_Reward_right.clicked.connect(pumpR)


        def stop():
            
            print('Test rig stopping')
            
            self.ui.chk_10Tone.clicked.disconnect(tone_10KHz)
            self.ui.chk_5Tone.clicked.disconnect(tone_5KHz)
            self.ui.chk_Punishment.clicked.disconnect(white_noise)
            self.ui.chk_BlueLED.clicked.disconnect(blueLED)            
            self.ui.chk_WhiteLED_Left.clicked.disconnect(whiteLLED)
            self.ui.chk_WhiteLED_Right.clicked.disconnect(whiteRLED)
            self.ui.chk_Reward_left.clicked.disconnect(pumpL)
            self.ui.chk_Reward_right.clicked.disconnect(pumpR)
            
        self.stop = stop


# Test blue LED
def blueLED():
    led_blue.on()
    sleep(1)
    led_blue.off()

# Test white LED on left spout
def whiteLLED():
    led_white_l.on()
    sleep(1)
    led_white_l.off()

# Test white LED on right spout
def whiteRLED():
    led_white_r.on()
    sleep(1)
    led_white_r.off()

# Test white LED on left spout
def pumpL():
    pump_l.off()
    sleep(0.5)
    pump_l.on()



