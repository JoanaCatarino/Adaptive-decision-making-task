# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:47:58 2024

@author: JoanaCatarino

 -- Free Licking task --
- The goal of this task is to make the animals familiarized with the spouts and the reward type they give (sucrose water)
- In this task animals should receive a reward when they lick either of the spouts
- Criterion: After 100 licks a Quiet window of 3000 ms is introduced - never on the first session 
"""
from gpio_map import *
from signal import pause
import os
import threading
import time


class FreeLickingTask:

    # Define Quiet window time
    quiet_window = 0 # seconds

    def __init__(self):
        
        # Initializer counters:
        self.red_btn_presses = 0
        self.blue_btn_presses = 0
        self.red_led_on_count = 0
        self.blue_led_on_count = 0
        self.total_presses = 0
        self.early_presses = 0
        self.red_early_presses = 0
        self.blue_early_presses = 0

        # Timestamps for the last button press
        self.last_red_press_time = 0
        self.last_blue_press_time = 0
        
        self.running = False  # Control flag for threads


    def start(self):
        print('Free Licking Task starting')
        self.running = True # Set running to True to start threads
        self.attach_callbacks()
        
        # Start countdowns in seperated threads
        threading.Thread(target=self.start_countdown, args=("red",), daemon=True).start()
        threading.Thread(target=self.start_countdown, args=("blue",), daemon=True).start()
        
        pause() # Keeps the script alive and listens for events like button press


    def start_countdown(self, button):
        while self.running: # Only runs while self.running is True
            current_time = time.time()
            
            # Determine the time remaining based on the quiet window
            if button == "red":
                if self.quiet_window > 0:
                    time_remaining = max(0, self.quiet_window - (current_time - self.last_red_press_time))
                else:
                    time_remaining = 0 # Quiet window is 0, so no countdown
            
            elif button == "blue":
                if self.quiet_window > 0:
                    time_remaining = max(0, self.quiet_window - (current_time - self.last_blue_press_time))
                else:
                    time_remaining = 0 # Quiet window is 0, so no countdown
                    
                    
            # Display the remaining time when the quiet window is greater than 0
            if self.quiet_window > 0 and ((button == 'red' and self.last_red_press_time > 0) or (button == 'blue' and self.last_blue_press_time > 0)):
                print(f"Time until next {button} press: {time_remaining:.1f} seconds")
            
            # Sleep briefly to avoid excessive printing
            time.sleep(0.1)


    def red_btn_pressed(self):
        print('red button pressed')
        current_time = time.time()
        
        # If quiet window is 0, allow the LED to turn on with each press
        if self.quiet_window == 0:
            self.red_btn_presses += 1
            self.total_presses += 1
            self.red_led_on_count += 1
            led_red.on() # Turn LED on
            print('red button pressed')
        
        # When quiet window is greater than 0
        # If pressed during the quiet window, reset the timer and don't turn on the LED
        elif self.quiet_window > 0 and current_time - self.last_red_press_time < self.quiet_window:
            self.red_early_presses += 1
            self.early_presses += 1  # Total presses - combines both red and blue
            self.last_red_press_time = current_time  # Reset last press time
            print("Red early press")
        else:
            # If pressed outside the quiet window, allow LED to turn on
            self.red_btn_presses += 1
            self.total_presses += 1
            self.red_led_on_count += 1
            led_red.on()
            self.last_red_press_time = current_time
            print("Red button valid press")


    def red_btn_released(self):
        led_red.off()
    
    
    def blue_btn_pressed(self):
        print('blue button pressed')
        current_time = time.time()
        
        # If quiet window is 0, allow the LED to turn on with each press
        if self.quiet_window == 0:
            self.blue_btn_presses += 1
            self.total_presses += 1
            self.blue_led_on_count += 1
            led_blue.on() # Turn LED on
            print('blue button pressed')        

        # When quiet window is greater than 0
        # If pressed during the quiet window, reset the timer and don't turn on the LED        
        elif self.quiet_window > 0 and current_time - self.last_blue_press_time < self.quiet_window:
            self.blue_early_presses += 1
            self.early_presses += 1  # Increment combined early presses counter
            self.last_blue_press_time = current_time  # Reset last press time
            print("Blue early press")
        else:
            # If pressed outside the quiet window, allow LED to turn on
            self.blue_btn_presses += 1
            self.total_presses += 1
            self.blue_led_on_count += 1
            led_blue.on()
            self.last_blue_press_time = current_time
            print("Blue button valid press")


    def blue_btn_released(self):
        led_blue.off()


    def attach_callbacks(self):
        # Attach callbacks to button events
        button_red.when_pressed = self.red_btn_pressed
        button_blue.when_pressed = self.blue_btn_pressed
        button_red.when_released = self.red_btn_released
        button_blue.when_released = self.blue_btn_released

    
    def stop(self):
        print('Free Licking task stopping')
        self.running = False  # Stop the countdown threads
        
    