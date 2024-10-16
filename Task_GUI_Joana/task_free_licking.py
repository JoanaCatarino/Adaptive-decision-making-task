# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:47:58 2024

@author: JoanaCatarino

 -- Free Licking task --
- The goal of this task is to make the animals familiarized with the spouts and the reward type they give (sucrose water)
- In this task animals should receive a reward when they lick either of the spouts
- Criterion: After 100 licks a Quiet window of 3000 ms is introduced - never on the first session 
"""
'''
class FreeLickingTask:
    def start (self):
        print ('Free Licking task starting')
        def stop():
            print ('Free Licking task stopping')
        self.stop = stop
'''

import asyncio
from gpiozero import *

class FreeLickingTask:
    # Function to handle button press asynchronously
    async def handle_button_press(led, color):
        print(f'{color} button pressed! LED on!')
        led.on()
        await asyncio.sleep(1)  # Keep LED on for 1 second
        led.off()
        print(f'{color} LED off.')
    
    
    # Function to monitor button presses
    async def monitor_buttons():
        while True:
            if red_button.is_pressed:
                await handle_button_press(red_led, "Red")
            if blue_button.is_pressed:
                await handle_button_press(blue_led, "Blue")
            await asyncio.sleep(0.1)  # Small delay to prevent CPU overuse
    
    
    # Main function to start the asyncio loop
    async def main():
        await monitor_buttons()

