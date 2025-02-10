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
        self.threshold_left = 0 # Threshold for the lick to count as a lick in the left spout
        self.threshold_right = 5 # Threshold for the lick to count as a lick in the right spout
        self.valve_opening = 0.5 # time in seconds the valve stays open
        
        # Counters for tracking licks
        self.total_licks = 0 # Counts the number of times the threshold was surpassed (puts together both piezos)
        self.licks_left = 0 # Counts licks on the Left spout (above threshold - valid licks)
        self.licks_right = 0 # Counts licks on the Right spout (above threshold - valid licks)


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
                        time.sleep(self.valve_opening)  # Adjust this for the desired ON duration
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
                        time.sleep(self.valve_opening)
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

    
    def set_thresholds(self, left, right):
        """Sets the thresholds for the piezo adders and updates the GUI."""
        self.threshold_left = left
        self.threshold_right = right
        
        # Update the GUI thresholds
        self.gui_controls.update_thresholds(self.threshold_left, self.threshold_right)

       
