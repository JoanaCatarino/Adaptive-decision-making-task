# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:47:58 2024

@author: JoanaCatarino

 -- Free Licking task --
- The goal of this task is to make the animals familiarized with the spouts and the reward type they give (sucrose water)
- In this task animals should receive a reward when they lick either of the spouts
- Criterion: After 100 licks a Quiet window of 3000 ms is introduced - never on the first session 
"""
from gpiozero import *
from signal import pause
from datetime import datetime
import os
import threading
import time



class FreeLickingTask:
    def start (self):
        print ('Free Licking task starting')
        def stop():
            print ('Free Licking task stopping')
        self.stop = stop


# Define Quiet window time
quiet_window = 2

# Initializer counters:
red_btn_presses = 0
blue_btn_presses = 0
red_led_on_count = 0
blue_led_on_count = 0
total_presses = 0
early_presses = 0
red_early_presses = 0
blue_early_presses = 0


# Timestamps for the last button press
last_red_press_time = 0
last_blue_press_time = 0


def start_countdown(button):
    while True:
        # Calculate remaining time for the next valid press
        current_time = time.time()
        if button == "red":
            time_remaining = max(0, quiet_window - (current_time - last_red_press_time))
        elif button == "blue":
            time_remaining = max(0, quiet_window - (current_time - last_blue_press_time))
        
        # Display the remaining time
        print(f"Time until next {button} press: {time_remaining:.1f} seconds")
        
        # Sleep briefly to avoid excessive printing
        time.sleep(0.1)

# Start countdowns in separate threads
threading.Thread(target=start_countdown, args=("red",), daemon=True).start()
threading.Thread(target=start_countdown, args=("blue",), daemon=True).start()

def red_btn_pressed():
    global red_btn_presses, red_led_on_count, total_presses, red_early_presses, early_presses, last_red_press_time
    current_time = time.time()
    
    if quiet_window > 0 and current_time - last_red_press_time < quiet_window:
        red_early_presses += 1
        early_presses += 1  # Increment combined early presses counter
        last_red_press_time = current_time  # Reset last press time
        print("Red button early press, countdown reset")
    else:
        red_btn_presses += 1
        total_presses += 1
        red_led_on_count += 1
        led_red.on()
        last_red_press_time = current_time
        print("Red button valid press")

def red_btn_released():
    led_red.off()
    
def blue_btn_pressed():
    global blue_btn_presses, blue_led_on_count, total_presses, blue_early_presses, early_presses, last_blue_press_time
    current_time = time.time()
    
    if quiet_window > 0 and current_time - last_blue_press_time < quiet_window:
        blue_early_presses += 1
        early_presses += 1  # Increment combined early presses counter
        last_blue_press_time = current_time  # Reset last press time
        print("Blue button early press, countdown reset")
    else:
        blue_btn_presses += 1
        total_presses += 1
        blue_led_on_count += 1
        led_blue.on()
        last_blue_press_time = current_time
        print("Blue button valid press")

def blue_btn_released():
    led_blue.off()

# Attach callbacks to button events
button_red.when_pressed = red_btn_pressed
button_blue.when_pressed = blue_btn_pressed
button_red.when_released = red_btn_released
button_blue.when_released = blue_btn_released

    

    
    
    
    