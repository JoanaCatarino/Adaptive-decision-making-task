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
from signal import pause
from gpio_map import *

class FreeLickingTask:
    # Function to handle LED control
    async def handle_led(led, duration, color):
        print(f"{color} button pressed! Turning on {color} LED...")
        led.on()
        await asyncio.sleep(duration)  # Keep LED on for the specified duration
        led.off()
        print(f"{color} LED off.")
    
    # Setup button press event listeners
    def on_red_button_press():
        print("Red button detected")
        asyncio.create_task(handle_led(led_red, 1, "Red"))
    
    def on_blue_button_press():
        print("Blue button detected")
        asyncio.create_task(handle_led(led_blue, 1, "Blue"))
    
    # Main function
    async def main():
        # Assign button press callbacks
        button_red.when_pressed = on_button_red_press
        button_blue.when_pressed = on_button_blue_press
    
        # Run asyncio event loop
        print("Monitoring buttons. Press Ctrl+C to exit.")
        while True:
            await asyncio.sleep(1)  # Keep the loop alive

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")