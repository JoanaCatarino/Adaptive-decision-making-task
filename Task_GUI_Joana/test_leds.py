# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 10:30:50 2025

@author: JoanaCatarino

file to try to do the led sequence

"""
import asyncio
from gpio_map import *

# List of LEDs to include in the sequence
leds = [led_white_r, led_white_l, pump_l, pump_r]

async def blink_led(led, duration=0.5):
    """Turn on an LED for the specified duration."""
    led.on()
    await asyncio.sleep(duration)
    led.off()

async def start_blinking(cycles=3, on_time=0.5, off_time=0.5):
    """
    Start the blinking sequence for the LEDs.

    Args:
        cycles (int): Number of times the sequence should repeat.
        on_time (float): Duration for which each LED stays ON.
        off_time (float): Duration for which each LED stays OFF.
    """
    print("Starting LED sequence...")
    try:
        # Ensure cycles is an integer
        cycles = int(cycles)  # Cast cycles to an integer
        
        for _ in range(cycles):
            for led in leds:
                await blink_led(led, duration=on_time)
                await asyncio.sleep(off_time)  # Wait off_time after each LED
    
    except asyncio.CancelledError:
        # Turn off all LEDs when the task is canceled
        for led in leds:
            led.off()
        
        print("LED sequence stopped.")

'''
import asyncio
from gpio_map import *
from gpiozero import LED
from time import sleep
from sound_generator import tone_10KHz, tone_5KHz, white_noise
from form_updt import Ui_TaskGui
from qasync import asyncSlot  # Import asyncSlot decorator


leds = [led_white_l, led_white_r, pump_l, pump_r] 

async def blink_led_sequence(leds, cycles=3, on_time=1, off_time=1):
    """
    Blink a list of LEDs in a sequence.

    Args:
        leds (list): List of gpiozero LED objects.
        cycles (int): Number of times the sequence should repeat.
        on_time (float): Duration for which each LED stays ON.
        off_time (float): Duration for which each LED stays OFF.
    """
    for _ in range(cycles):
        for led in leds:
            led.on()
            await asyncio.sleep(on_time)
            led.off()
            await asyncio.sleep(off_time)

def setup_led_sequence_button(ui_element, leds, cycles=3, on_time=1, off_time=1):
    """
    Connect a button to trigger the LED sequence.

    Args:
        ui_element (QPushButton): The button element from the UI.
        leds (list): List of gpiozero LED objects.
        cycles (int): Number of times the sequence should repeat.
        on_time (float): Duration for which each LED stays ON.
        off_time (float): Duration for which each LED stays OFF.
    """

    async def start_led_sequence():
        print('Starting LED sequence...')
        await blink_led_sequence(leds, cycles, on_time, off_time)
'''

