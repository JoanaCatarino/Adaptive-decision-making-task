# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:49:53 2024

@author: JoanaCatarino

Working on this file like it is the free licking script but to be moved to the correct file in the future

"""
import threading
import time
from PyQt5.QtCore import QTimer
from piezo_reader import PiezoReader
from gpio_map import *

class SpoutSamplingTask:
    
    def __init__(self, gui_controls): 
    
        self.gui_controls = gui_controls
        self.piezo_reader = gui_controls.piezo_reader        
        self.quiet_window = 3 # seconds
        self.inter_trial_interval = 0.5 # seconds
        self.response_window = 1 # second
        self.total_trials = 0
        self.trials = [] # list to store trial data
        
        self.running = False
        
        # Initialize time variables
        self.tstart = None # start of the task
        self.tlick = None # last lick
        self.t = None # current time
        self.last_led_time = None # Last time the LED was turned ON
        

    def start (self):
        print ('Spout Sampling task starting')
        
        # Turn the LEDS ON initially
        pump_l.on()
        pump_r.on()
        
        # Reset counter
        self.total_trials = 0
        
        # Update GUI display
        self.gui_controls.update_total_trials(0)
        
        self.running = True
        self.tstart = time.time() # record the start time
        self.last_led_time = self.tstart # initialize last LED time
        self.print_thread = threading.Thread(target=self.tests, daemon=True)
        self.print_thread.start()        
        
    def stop(self):
        """Stops the Spout Sampling task."""
        print("Stopping Spout Sampling Task...")
        
        self.running = False
        
        if self.print_thread.is_alive():
            self.print_thread.join()
        pump_l.on() 
        
        
    def tests(self):
        
        while self.running:
            self.t = time.time() - self.tstart # update current time based on the elapsed time
            
            # Check if enough time has passed since the last LED shine
            if self.last_led_time is None or (time.time() - self.last_led_time >= self.response_window):
                
                led_white_l.on()  
                print(f"LED ON at t: {self.t:.2f} sec (Trial:{self.total_trials + 1})")
                time.sleep(0.2)  # Keep LED ON for 0.2 seconds
                led_white_l.off()                 
                
                self.total_trials +=1
                self.gui_controls.update_total_trials(self.total_trials)
                self.trials.append((self.total_trials, self.t)) #save trials and time in a list

                # Update last LED time
                self.last_led_time = time.time()

            time.sleep(0.02)  # Update every 20ms


    def get_trials(self):
        'returns the list of trials that were recorded'
        return self.trials

'''
    def condition_trial_initiation(self, t, tstart, response_window, tlick):
        return t-(tstart + self.response_window) > self.inter_trial_interval and t-tlick > self.quiet_window
    
    def condition_lick(self, tlick, tstart, response_window):
        return 0 < tlick - tstart < self.response_window
    
    
    # to use the condition - just an example
    if condition_trial_duration(self, t, tstart, response_window, tlick):
        print('main condition is met, we can start a new trial')
'''   



