# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:47:58 2024

@author: JoanaCatarino

 -- Free Licking task --
- The goal of this task is to make the animals familiarized with the spouts and the reward type they give (sucrose water)
- In this task animals should receive a reward when they lick either of the spouts
- Criterion: After 100 licks a Quiet window of 3000 ms is introduced - never on the first session 
"""

import threading
import time


class FreeLickingTask:
    def __init__(self, ui):
        """
        Initialize the Free Licking Task with a reference to the GUI object.
        """
        self.ui = ui  # Reference to the GUI object
        self.running = False
        self.thread = None

    def start(self):
        """
        Starts the Free Licking Task by initializing the serial connection, starting piezo plots,
        and launching a thread to monitor and print piezo values.
        """
        if not self.running:
            print("Free Licking Task starting...")
            self.running = True


            # Launch a thread to monitor and print piezo values
            self.thread = threading.Thread(target=self._print_piezo_values)
            self.thread.start()

    def stop(self):
        """
        Stops the Free Licking Task by stopping the piezo timer and the thread.
        """
        if self.running:
            print("Stopping Free Licking Task...")
            self.running = False

            # Stop the piezo update timer in the GUI
            self.ui.piezo_timer.stop()

            # Wait for the thread to finish
            if self.thread:
                self.thread.join()

            print("Free Licking Task stopped.")

    def _print_piezo_values(self):
        """
        Continuously prints the piezo_adder1 values while the task is running.
        """
        try:
            while self.running:
                if self.ui.piezo_adder1:
                    print(f"Piezo Adder 1: {self.ui.piezo_adder1[-1]}")
                time.sleep(0.1)  # Adjust this for the desired printing frequency
        except Exception as e:
            print(f"Error during piezo reading: {e}")















'''
from gpio_map import *
from PyQt5.QtCore import QThread, pyqtSignal
from signal import pause
import os
import threading
import time

from piezo_reader import PiezoReader

def print_piezo_values():
    piezo_reader = PiezoReader()
    piezo_reader.setup_serial_connection()
    piezo_reader.start_reading()

    try:
        while True:
            if piezo_reader.piezo_adder1:
                print(f"Piezo Adder 1: {piezo_reader.piezo_adder1[-1]}")
            time.sleep(0.1)  # Adjust this for the desired printing frequency
    except KeyboardInterrupt:
        print("Stopping...")
        piezo_reader.stop()


class FreeLickingTask:

    def __init__(self, ui):
        self.ui = ui
    
    def start(self):
        print_piezo_values()
        
        def stop():
            print('Done printing')
            
        self.stop = stop
'''



'''    
    update_qw = pyqtSignal(float)
        
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        # Define Quiet window time
        self.quiet_window = 0 # seconds
        
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
        
        # Flags to track if remaining time reached zero
        self.red_remaining_time_zero = False
        self.blue_remaining_time_zero = False
        
        self.running = False  # Control flag for threads
        
        # Connect the signal to the method that updates
        self.update_qw.connect(self.update_variables)

    
    def update_variables(self, new_qw_value):
        # Method to handle the update if needed
        self.quiet_window = new_qw_value
        print(f'QW updated to {new_qw_value}s - FL script')


    def run(self):
        print('Free Licking Task starting')
        self.running = True # Set running to True to start threads
        
        while self.running:
            self.attach_callbacks()
            
            # Start countdowns in seperated threads
            threading.Thread(target=self.start_countdown, args=("red",), daemon=True).start()
            threading.Thread(target=self.start_countdown, args=("blue",), daemon=True).start()
            
            pause() # Keeps the script alive and listens for events like button press
        
        
        def stop():
            print('Free Licking task stopping')
            self.running = False  # Stop the countdown threads
    
        self.stop = stop
        


    def start_countdown(self, button):
        
        while self.running: # Only runs while self.running is True
            current_time = time.time()
            
            # Determine the time remaining based on the quiet window
            if button == "red":
                if self.quiet_window > 0:
                    #print(f' executing task with quet window = {self.quiet_window}')
                    time_remaining = max(0, self.quiet_window - (current_time - self.last_red_press_time))
                else:
                    time_remaining = 0 # Quiet window is 0, so no countdown
                    
                if time_remaining > 0:
                    print(f"Time until next {button} press: {time_remaining:.1f} seconds")
                
                elif time_remaining == 0 and not self.red_remaining_time_zero:
                    # print once when time reaches 0, then stop printing
                    print(f"Time until next {button} press: 0 seconds")
                    self.red_remaining_time_zero = True
            
            
            elif button == "blue":
                if self.quiet_window > 0:
                    time_remaining = max(0, self.quiet_window - (current_time - self.last_blue_press_time))
                else:
                    time_remaining = 0 # Quiet window is 0, so no countdown
                    
                if time_remaining > 0:
                    print(f"Time until next {button} press: {time_remaining:.1f} seconds")
                
                elif time_remaining == 0 and not self.blue_remaining_time_zero:
                    # print once when time reaches 0, then stop printing
                    print(f"Time until next {button} press: 0 seconds")
                    self.blue_remaining_time_zero = True # Set flag to prevent further printing                   
                    
            # Sleep briefly to avoid excessive printing
            time.sleep(0.1)
           

    def attach_callbacks(self):
        # Attach callbacks to button events
        button_red.when_pressed = self.red_btn_pressed
        button_blue.when_pressed = self.blue_btn_pressed
        button_red.when_released = self.red_btn_released
        button_blue.when_released = self.blue_btn_released

    
    def stop(self):
        print('Free Licking task stopping')
        self.running = False  # Stop the countdown threads
        
        

    def red_btn_pressed(self):
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
            self.red_remaining_time_zero = False # Reset flag to False on a valid press
            print("Red early press")
        else:
            # If pressed outside the quiet window, allow LED to turn on
            self.red_btn_presses += 1
            self.total_presses += 1
            self.red_led_on_count += 1
            led_red.on()
            self.last_red_press_time = current_time
            self.red_remaining_time_zero = False
            print("Red button valid press")


    def red_btn_released(self):
        led_red.off()
    
    
    def blue_btn_pressed(self):
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
            self.blue_remaining_time_zero = False
            print("Blue early press")
        else:
            # If pressed outside the quiet window, allow LED to turn on
            self.blue_btn_presses += 1
            self.total_presses += 1
            self.blue_led_on_count += 1
            led_blue.on()
            self.last_blue_press_time = current_time
            self.blue_remaining_time_zero = False
            print("Blue button valid press")


    def blue_btn_released(self):
        led_blue.off()
        
'''        
