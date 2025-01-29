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
        self.task_data = []
        
        self.gui_controls = gui_controls
        self.piezo_reader = gui_controls.piezo_reader        
        self.QW = 3 # Quiet window in seconds
        self.ITI = 2 # Inter-trial interval in seconds
        self.RW = 2 # Response window in seconds
        self.total_licks = 0
        self.licks_left = 0
        self.licks_right = 0
        self.first_lick = None # first lick of each trial
        self.tlick = None # Last lick registered - will be used to check conditions to initiate next trial
        self.trials = [] # list to store trial data
        self.animal_quiet = False
        
        # Counters for licks
        self.threshold_left = 20
        self.threshold_right = 20
        self.valve_opening = 1
        
        # Boolean
        self.trialstarted = False
        
        # Loop
        self.running = False
        
        # Initialize time variables
        self.tstart = None # start of the task
        self.ttrial = None # start of the trial
        self.tlick_l = None # last lick left spout
        self.tlick_r = None # last lick right spout
        self.tlast_lick = None # Last lick in either spouts
        self.t = None # current time
        
        # Lock for thread-safe access to shared variables
        self.lock = threading.Lock()
        
        # Call .csv function
        self.save_data()
        

    def start (self):
        print ('Spout Sampling task starting')
        
        # Turn the LEDS ON initially
        pump_l.on()
        pump_r.on()
        
        # Reset counters
        self.total_trials = 0
        self.total_licks = 0 
        self.licks_left = 0 
        self.licks_right = 0 
        
        # Update GUI display
        self.gui_controls.update_total_licks(0)
        self.gui_controls.update_licks_left(0)
        self.gui_controls.update_licks_right(0)
        
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
     
       
    def trial_has_started(self):
        if self.trialstarted:
            print('trial has started')
            self.trialstarted=False
        
        
    def check_animal_quiet(self):
        p1 = self.piezo_reader.piezo_adder1
        p2 = self.piezo_reader.piezo_adder2
        
        required_samples = self.QW*60 # Serial runs in 60 Hz 
        
        # Wait until there is enough data to check the criteria
        while len(p1) < required_samples or len(p2) < required_samples:
            print('Waiting for enough data to check quiet period..')
            # refresh data
            p1 = self.piezo_reader.piezo_adder1
            p2 = self.piezo_reader.piezo_adder2
            
        # Now that there is enough data, check for licks in the last QW seconds        
        first_idx_l = len(p1)-required_samples
        first_idx_r = len(p2)-required_samples
        
        quiet_left = max(p1[first_idx_l:]) < self.threshold_left
        quiet_right = max(p2[first_idx_r:]) < self.threshold_right
        
        if quiet_left and quiet_right:
            self.animal_quiet = True
            return True
        else:
            print('Licks detected during Quiet Window')
        
    
    
    def main(self):
        
        while self.running:
            self.t = time.time() - self.tstart # update current time based on the elapsed time

            if (self.ttrial is None or (self.t - (self.ttrial + self.RW) > self.ITI)) and self.check_animal_quiet():
                
                with self.lock:
                    self.trialstarted = True
                    self.trial_has_started()
                    
                    # Reset first lick tracking
                    self.first_lick = None
                    
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
                    with self.lock:
                        self.tlick_l = self.t
                        print('threshold exceeded left')
                        
                        elapsed_left = self.tlick_l - self.ttrial
                            
                        if 0 < elapsed_left < self.RW and self.first_lick is None:
                            
                            self.first_lick = 'left' # Mark left as the first lick
                            self.tlick = self.tlick_l # Save the time of the rewarded lick
                            print(f'{self.tlick}')
                            
                            print('Lick left within respnse window')
                            
                            pump_l.off()
                            time.sleep(self.valve_opening)
                            pump_l.on()
                            
                            print('reward delivered - left')
                            
                            self.total_licks += 1 # Implement total licks
                            self.licks_left +=1 # Implement licks left
                        
                            self.gui_controls.update_total_licks(self.total_licks) # Update the total trials in the GUI
                            self.gui_controls.update_licks_left(self.licks_left) # Update licks left in the GUI                            
                            
                            
            if self.piezo_reader.piezo_adder2:
                latest_value2 = self.piezo_reader.piezo_adder2[-1]

                if latest_value2 > self.threshold_right: 
                    with self.lock:
                        self.tlick_r = self.t
                        print('threshold exceeded right')
                        
                        elapsed_right = self.tlick_r - self.ttrial
                        
                        if 0 < elapsed_right < self.RW and self.first_lick is None:
                            
                            self.first_lick = 'right' # Mark right as the first lick
                            self.tlick = self.tlick_r # save the time of the rewarded lick
                            print(f'{self.tlick}')
                            
                            print('lick right within response window')
                            
                            pump_r.off()
                            time.sleep(self.valve_opening)
                            pump_r.on()
                            
                            print('reward delivered - right')
                        
                            self.total_licks += 1 # Implement total licks
                            self.licks_right +=1 # Implement licks right
                        
                            self.gui_controls.update_total_licks(self.total_licks) # Update the total trials in the GUI
                            self.gui_controls.update_licks_right(self.licks_right) # Update licks right in the GUI     



    def save_data(self):
        """Saves the trial data to a fixed CSV file."""
        # Ensure the directory exists
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Create the full file path
        file_path = os.path.join(self.save_dir, self.file_name)
        
        # Write the data to the CSV file
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(['Trial Number', 'Time (s)', 'Lick', 'Lick Left', 'Lick Right', 'Lick timestamp',
                             'RW', 'QW', 'ITI', 'Threshold Left', 'Threshold Right'])
            # Write the trial data
            writer.writerows(self.trials)
        
        print(f"Trials saved to {file_path}")


