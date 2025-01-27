# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:49:53 2024

@author: JoanaCatarino

Working on this file like it is the free licking script but to be moved to the correct file in the future

"""
import threading
import time
import csv
import os
from PyQt5.QtCore import QTimer
from piezo_reader import PiezoReader
from gpio_map import *

class SpoutSamplingTask:
    
    def __init__(self, gui_controls): 
    
        # Direcory to save file with trials data
        self.save_dir = "/home/rasppi-ephys/test_dir"
        self.file_name = 'trials.csv' # set the desired file name
        
        self.gui_controls = gui_controls
        self.piezo_reader = gui_controls.piezo_reader        
        self.quiet_window = 3 # seconds
        self.ITI = 2 # seconds
        self.response_window = 1 # second
        self.total_trials = 0
        self.trials = [] # list to store trial data
        
        self.threshold_left = 0
        self.open_valve = 0.5
        
        # Boolean
        self.trialstarted = False
        
        self.running = False
        
        # Initialize time variables
        self.tstart = None # start of the task
        self.ttrial = None # start of the trial
        self.tlick_l = None # last lick left spout
        self.tlick_r = None # last lick right spout
        self.t = None # current time
        
        

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
        #self.ttrial = self.tstart
        self.print_thread = threading.Thread(target=self.main, daemon=True)
        self.print_thread.start()        
        
    def stop(self):
        """Stops the Spout Sampling task."""
        print("Stopping Spout Sampling Task...")
        
        self.running = False
        
        if self.print_thread.is_alive():
            self.print_thread.join()
        pump_l.on() 
        
        self.save_trials_to_csv()
     
             
    def main(self):
        
        while self.running:
            self.t = time.time() - self.tstart # update current time based on the elapsed time
            
            # Check if enough time has passed since the last LED shine
            if self.ttrial is None or (self.t - (self.ttrial + self.response_window) > self.ITI):
                
                self.trialstarted = True
                self.trial_has_started()
                
                led_white_l.on()  
                print(f"LED ON at t: {self.t:.2f} sec (Trial:{self.total_trials + 1})")
                time.sleep(1)  # Keep LED ON for 0.2 seconds
                led_white_l.off()                 
                
                self.total_trials +=1
                self.gui_controls.update_total_trials(self.total_trials)
                self.trials.append((self.total_trials, self.t)) #save trials and time in a list
                
                # Update last LED time
                self.ttrial = self.t
                
            if self.piezo_reader.piezo_adder1:
                latest_value1 = self.piezo_reader.piezo_adder1[-1]
                
                if latest_value1 > self.threshold_left:
                    self.tlick_l = self.t
                    print('threshold exceeded')
                    
                        
                    if 0 < (self.tlick_l - self.ttrial) < self.response_window:
                        print('Lick within respnse window')
                        pump_l.off()
                        time.sleep(self.open_valve)
                        pump_l.on()
                        print('reward delivered')

        


    def trial_has_started(self):
        if self.trialstarted:
            print('trial has started')
            self.trialstarted=False


    def save_trials_to_csv(self):
        """Saves the trial data to a fixed CSV file."""
        # Ensure the directory exists
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Create the full file path
        file_path = os.path.join(self.save_dir, self.file_name)
        
        # Write the data to the CSV file
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(["Trial Number", "Time (s)"])
            # Write the trial data
            writer.writerows(self.trials)
        
        print(f"Trials saved to {file_path}")

'''
    def condition_trial_initiation(self, t, tstart, response_window, tlick):
        return t-(tstart + self.response_window) > self.inter_trial_interval and t-tlick > self.quiet_window
    
    def condition_lick(self, tlick, tstart, response_window):
        return 0 < tlick - tstart < self.response_window
    
    
    # to use the condition - just an example
    if condition_trial_duration(self, t, tstart, response_window, tlick):
        print('main condition is met, we can start a new trial')
'''   



