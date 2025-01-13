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

from test_leds import start_blinking


        
class TestRig:
    def __init__(self, ui):
        self.ui = ui
        
        # Define LED sequence
        self.leds = [led_white_r, led_white_l, pump_l, pump_r]
        
        # Turn off all LEDs initially
        for led in self.leds:
            led.off()
            
        self.start()

    

    def start(self):
        print('Test rig starting')
        self.ui.chk_10Tone.clicked.connect(tone_10KHz)
        self.ui.chk_5Tone.clicked.connect(tone_5KHz)
        self.ui.chk_Punishment.clicked.connect(white_noise)
        #self.ui.chk_BlueLED.clicked.connect(blueLED)
        
        self.ui.chk_BlueLED.clicked.connect(self.start_led_sequence)       

        
        #print(f"chk_BlueLED: {self.ui.chk_BlueLED}")
        #self.ui.chk_BlueLED.clicked.connect(lambda: print("Blink LEDs button clicked"))
        #self.ui.chk_BlueLED.clicked.connect(lambda checked: asyncio.create.task(self.blink_leds(checked)))
        self.ui.chk_WhiteLED_Left.clicked.connect(whiteLLED)
        self.ui.chk_WhiteLED_Right.clicked.connect(whiteRLED)
        self.ui.chk_Reward_left.clicked.connect(pumpL)
        self.ui.chk_Reward_right.clicked.connect(pumpR)


        def stop(self):
            print('Test rig stopping')
            self.ui.chk_10Tone.clicked.disconnect(tone_10KHz)
            self.ui.chk_5Tone.clicked.disconnect(tone_5KHz)
            self.ui.chk_Punishment.clicked.disconnect(white_noise)
            #self.ui.chk_BlueLED.clicked.disconnect(blueLED)
            self.ui.chk_BlueLED.clicked.disconnect(self.start_led_sequence)
            self.ui.chk_WhiteLED_Left.clicked.disconnect(whiteLLED)
            self.ui.chk_WhiteLED_Right.clicked.disconnect(whiteRLED)
            self.ui.chk_Reward_left.clicked.disconnect(pumpL)
            self.ui.chk_Reward_right.clicked.disconnect(pumpR)

            #gpio_map.Device.close()

        self.stop = stop


        @asyncSlot()
        async def start_led_sequence(self):
            """Start the LED blinking sequence when the button is pressed."""
            print("Starting LED sequence...")
            await start_blinking()



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
    pump_l.on()
    sleep(1)
    pump_l.off()

# Test white LED on right spout
def pumpR():
    pump_r.on()
    sleep(1)
    pump_r.off()


'''
# Blink a specific LED in sequence
async def blink_led_sequence(leds, cycles=3, on_time=1, off_time=1):
    """
    Blink a list of LEDs in sequence.

    Args:
        leds (list): List of LED objects to control.
        cycles (int): Number of times the sequence should repeat.
        on_time (float): Duration for which each LED stays ON.
        off_time (float): Duration for which each LED stays OFF.
    """
    for _ in range(cycles):  # Number of cycles to repeat
        for led in leds:
            led.on()  # Turn on the LED
            await asyncio.sleep(on_time)  # Wait for specified ON time
            led.off()  # Turn off the LED
            await asyncio.sleep(off_time)  # Wait for specified OFF time



# Need to define functions to flush water on right spout and left spout

# Need to define functions to flush water on right spout and left spout

'''

'''
   # @asyncSlot(bool) #use asyncSlot to handle async method
    async def blink_leds(self, checked):
        leds = [led_blue, led_white_l, led_white_r]
        print('Starting LED blinking sequence')
        await blink_led_sequence(leds, cycles=5, on_time=1, off_time=1)
        print('LED blinking sequence completed')

        self.stop = stop
'''