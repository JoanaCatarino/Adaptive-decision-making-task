# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:49:53 2024

@author: JoanaCatarino

Working on this file like it is the free licking script but to be moved to the correct file in the future

"""
import threading
import time
from gpio_map import *

class SpoutSamplingTask:
    
    def __init__(self, gui_controls): 
    
        self.quiet_window = 3 # seconds
        self.inter_trial_interval = 0.5 # seconds
        self.response_window = 1 # second
        
        self.running = False
        
        # Initialize time variables
        self.tstart = None # start of the trial
        self.tlick = None # last lick
        self.t = None # current time
        

    def start (self):
        print ('Spout Sampling task starting')
        
        # Turn the LEDS ON initially
        pump_l.on()
        pump_r.on()
        
        self.running = True
        self.tstart = time.time() # record the start time
        self.print_thread = threading.Thread(target=self.tests, daemon=True)
        self.print_thread.start()        
        
        while self.running:
            self.t = time.time() - self.tstart # update current time based on the elapsed time
            time.sleep (0.02) # update time every 20ms
        
    def stop(self):
        """Stops the Free Licking task."""
        print("Stopping Free Licking Task...")
        
        self.running = False
        
        if self.print_thread.is_alive():
            self.print_thread.join()
        pump_l.on() 
        
        
    def tests(self):
        while self.running:
            print(f't:{self.t} sec')
            time.sleep(0.02) # print every 20ms


'''
    def condition_trial_initiation(self, t, tstart, response_window, tlick):
        return t-(tstart + self.response_window) > self.inter_trial_interval and t-tlick > self.quiet_window
    
    def condition_lick(self, tlick, tstart, response_window):
        return 0 < tlick - tstart < self.response_window
    
    
    # to use the condition - just an example
    if condition_trial_duration(self, t, tstart, response_window, tlick):
        print('main condition is met, we can start a new trial')
'''   



