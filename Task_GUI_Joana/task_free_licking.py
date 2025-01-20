# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:47:58 2024

@author: JoanaCatarino

 -- Free Licking task --
- The goal of this task is to make the animals familiarized with the spouts and the reward type they give (sucrose water)
- In this task animals should receive a reward when they lick either of the spouts
- Criterion: After 100 licks a Quiet window of 3000 ms is introduced - never on the first session 

Important
- when pump is set to ON it is actually OFF and when it is set to OFF it is pumping water
"""

import threading
import time

from PyQt5.QtCore import QTimer
from piezo_reader import PiezoReader
from gpio_map import *


class FreeLickingTask:
    
    def __init__(self, gui_controls):
        """
        Initializes the FreeLickingTask class.

        Args:
            gui_controls: An instance of GuiControls to access piezo_reader and UI components.
        """
        self.gui_controls = gui_controls
        self.piezo_reader = gui_controls.piezo_reader
        self.running = False
        self.threshold_left = 5 # Threshold for the lick to count as a lick in the left spout
        self.threshold_right = 5 # Threshold for the lick to count as a lick in the right spout
        self.led_on_duration = 0.5 # time in seconds the LED stays on
        
        # Counters for tracking licks
        self.total_licks = 0 # Counts the number of times the threshold was surpassed (puts together both piezos)
        self.licks_left = 0 # Counts licks on the Left spout (above threshold - valid licks)
        self.licks_right = 0 # Counts licks on the Right spout (above threshold - valid licks)
        
    def set_thresholds(self, left, right):
        self.threshold_left = left
        self.threshold_right = right
        

    def start(self):
        """Starts the FreeLicking task."""
        print("Starting Free Licking Task...")
                
        # Turn the LEDS ON initially
        pump_l.on()
        pump_r.on()
        
        # Reset counters
        self.total_licks = 0 
        self.licks_left = 0 
        self.licks_right = 0 
        
        # Update Gui display immediately
        self.gui_controls.update_total_licks(0)
        self.gui_controls.update_licks_left(0)
        self.gui_controls.update_licks_right(0)
        
        self.running = True
        self.print_thread = threading.Thread(target=self.monitor_piezo_values, daemon=True)
        self.print_thread.start()

    def stop(self):
        """Stops the Free Licking task."""
        print("Stopping Free Licking Task...")
        self.running = False
        if self.print_thread.is_alive():
            self.print_thread.join()
        pump_l.on()

    def monitor_piezo_values(self):
        """
        Continuously prints the piezo_adder1 values while the task is running and checks the threshold.
        """
        try:
            while self.running:
                
                # Monitor piezo_adder1 (left spout) and control pump_l
                if self.piezo_reader.piezo_adder1:
                    latest_value1 = self.piezo_reader.piezo_adder1[-1]
                    print(f'Piezo Adder 1: {latest_value1}')
                    
                    # Check if the value exceeds the threshold
                    if latest_value1 > self.threshold_left:
                        print('Threshold exceeded! Flashing pump_l')
                        pump_l.off()
                        time.sleep(self.led_on_duration)  # Adjust this for the desired ON duration
                        pump_l.on()
                        
                        self.total_licks += 1 # Implement total licks
                        self.licks_left +=1 # Implement licks left
                        
                        self.gui_controls.update_total_licks(self.total_licks) # Update the total trials in the GUI
                        self.gui_controls.update_licks_left(self.licks_left) # Update licks left in the GUI
                
                
                # Monitor piezo_adder2 (right spout) and control pump_r
                if self.piezo_reader.piezo_adder2:
                    latest_value2 = self.piezo_reader.piezo_adder2[-1]
                    print(f'Piezo Adder 2:{latest_value2}')
                    
                    # Check if the value exceeds the threshold
                    if latest_value2 > self.threshold_right:
                        print('Threshold exceeded! Flashing pump_r')
                        pump_r.off()
                        time.sleep(self.led_on_duration)
                        pump_r.on()
                        
                        self.total_licks += 1 # Implement total licks
                        self.licks_right +=1 # Implement licks right
                        
                        self.gui_controls.update_total_licks(self.total_licks) # Update the total trials in the GUI
                        self.gui_controls.update_licks_right(self.licks_right) # Update licks right in the GUI

                        
                # Print the total trials count
                print(f'Total licks = {self.total_licks}')

                time.sleep(0.1)  # Adjust for the desired frequency
        
        except Exception as e:
            pump_l.on()  # Turn off pump_l in case of error
            pump_r.on()  # Turn off pump_r in case of error



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
