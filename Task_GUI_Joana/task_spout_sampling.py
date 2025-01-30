# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:49:53 2024

@author: JoanaCatarino

Working on this file like it is the free licking script but to be moved to the correct file in the future

"""
import threading
import numpy as np
import time
import csv
import os
from PyQt5.QtCore import QTimer
from piezo_reader import PiezoReader
from gpio_map import *

class SpoutSamplingTask:
    
    def __init__(self, gui_controls): 
    
        # Directory to save file with trials data
        self.save_dir = "/home/rasppi-ephys/test_dir"
        self.file_name = 'trials.csv' # set the desired file name
        self.trials = [] # list to store trial data
        
        # Connection to GUI
        self.gui_controls = gui_controls
        self.piezo_reader = gui_controls.piezo_reader        
        
        # Experiment parameters
        self.QW = 3 # Quiet window in seconds
        self.ITI = 2 # Inter-trial interval in seconds
        self.RW = 2 # Response window in seconds
        self.threshold_left = 1
        self.threshold_right = 1
        self.valve_opening = 1  # Reward duration   
        
        # Counters
        self.total_trials = 0
        self.total_licks = 0
        self.licks_left = 0
        self.licks_right = 0
        
        # Booleans
        self.trialstarted = False
        self.running = False
        
        # Time variables
        self.tstart = None # start of the task
        self.ttrial = None # start of the trial
        self.t = None # current time
        self.tlick_l = None # last lick left spout
        self.tlick_r = None # last lick right spout
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        # Ensure save directory exists
        os.makedirs(self.save_dir, exist_ok=True)
        self.create_trial_csv()
        
        self.first_lick = None
        

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
        
        # Start main loop in a separate thread
        self.print_thread = threading.Thread(target=self.main, daemon=True)
        self.print_thread.start()   
        
        
    def stop(self):
        print("Stopping Spout Sampling Task...")
        
        self.running = False
        
        if self.print_thread.is_alive():
            self.print_thread.join()
        pump_l.on() 
        
        self.save_trials_to_csv()
        
    
    def check_animal_quiet(self):
        
        """ Continuously checks for a quiet period before starting a trial """
        
        required_samples = self.QW*60 # Serial runs in 60 Hz   
        
        while True:
            p1 = np.array(self.piezo_reader.piezo_adder1,dtype=np.uint16)
            p2 = np.array(self.piezo_reader.piezo_adder2,dtype=np.uint16)
        
        
            if len(p1) >= required_samples and len(p2) >= required_samples:
                quiet_left = max(p1[-required_samples:]) < self.threshold_left
                quiet_right = max(p2[-required_samples:]) < self.threshold_right
               
                if quiet_left and quiet_right:
                    return True # Animal was quiet
                else:
                    print('Licks detected during Quiet Window')
                    
            else:
                print('Waiting for enough data to check quiet window')
            
            time.sleep(0.1) # prevents excessive CPU usage
    
     
    def start_trial(self):
        
        """ Initiates a trial, runs LED in paralledl, and logs trial start"""
        
        with self.lock:
            self.trialstarted = True
            trial_number= self.total_trials +1
            self.ttrial = self.t # Update trial start time
            self.first_lick = None # Reset first lick at the start of each trial
            
            # Start LED in a separate thread
            threading.Thread(target=self.led_indicator, args=(self.RW,)).start()
            
            print(f"LED ON at t: {self.t:.2f} sec (Trial: {trial_number})")
            
            self.total_trials = trial_number
            self.gui_controls.update_total_trials(self.total_trials)
            
    
    def led_indicator(self, RW):
        
        """ Turn on LED during trial duration without blocking main loop"""
        
        led_white_l.on()
        time.sleep(self.RW) # This should actually be changed to the duration of the full trial
        led_white_l.off()
        
        
    def detect_licks(self):
    
        """Checks for licks and delivers rewards in parallel."""

        # Ensure piezo data is updated before checking
        p1 = list(self.piezo_reader.piezo_adder1)
        p2 = list(self.piezo_reader.piezo_adder2)
    
        # Small delay to prevent CPU overload and stabilize readings
        time.sleep(0.001)
    
        # Left piezo
        if p1:
            latest_value1 = p1[-1]
    
            if latest_value1 > self.threshold_left:
                with self.lock:
                    self.tlick_l = self.t
                    elapsed_left = self.tlick_l - self.ttrial
                    print('Threshold exceeded left')
    
                    if self.first_lick is None and (0 < elapsed_left < self.RW):
                        self.first_lick = 'left'
    
                        # Deliver reward in a separate thread
                        threading.Thread(target=self.reward, args=('left',)).start()
    
                        self.total_licks += 1
                        self.licks_left += 1
                        self.gui_controls.update_total_licks(self.total_licks)
                        self.gui_controls.update_licks_left(self.licks_left)
    
        # Right piezo        
        if p2:
            latest_value2 = p2[-1]
    
            if latest_value2 > self.threshold_right:
                with self.lock:
                    self.tlick_r = self.t
                    elapsed_right = self.tlick_r - self.ttrial
                    print('Threshold exceeded right')
    
                    if self.first_lick is None and (0 < elapsed_right < self.RW):
                        self.first_lick = 'right'
    
                        # Deliver reward in a separate thread
                        threading.Thread(target=self.reward, args=('right',)).start()
    
                        self.total_licks += 1
                        self.licks_right += 1
                        self.gui_controls.update_total_licks(self.total_licks)
                        self.gui_controls.update_licks_right(self.licks_right)
    
    
    def reward(self, side):
        
        """Delivers a reward without blocking the main loop."""
        
        print(f"Delivering reward - {side}")
    
        # Ensure pump action executes properly with a short delay
        time.sleep(0.01)
    
        if side == 'left':
            pump_l.off()
            time.sleep(self.valve_opening)
            pump_l.on()
            print('Reward delivered - left')
            
        elif side == 'right':
            pump_r.off()
            time.sleep(self.valve_opening)
            pump_r.on()
            print('Reward delivered - right')
    
        # Small delay to ensure execution before another lick
        #time.sleep(0.01)
    
        
    def main(self):
        
        while self.running:
            self.t = time.time() - self.tstart # update current time based on the elapsed time
            
           
            # Start a new trial if enough time has passed since the last trial and all conditions are met
            if (self.ttrial is None or (self.t - (self.ttrial + self.RW) > self.ITI)):
                if self.check_animal_quiet():
                    self.start_trial()
                    
            # Run lick detection continuously
            self.detect_licks()
                
                
  

    def save_trials_to_csv(self):
        """Saves the trial data to a fixed CSV file."""
        file_path = os.path.join(self.save_dir, self.file_name)
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Trial Number", "Time (s)"])
            writer.writerows(self.trials)
        print(f"Trials saved to {file_path}")

    def create_trial_csv(self):
        """Creates a CSV file for logging trial data if it doesn't exist."""
        file_path = os.path.join(self.save_dir, self.file_name)
        if not os.path.exists(file_path):
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Trial Number", "Time (s)"])
                
                
                
'''
    def condition_trial_initiation(self, t, tstart, response_window, tlick):
        return t-(tstart + self.response_window) > self.inter_trial_interval and t-tlick > self.quiet_window
    
    def condition_lick(self, tlick, tstart, response_window):
        return 0 < tlick - tstart < self.response_window
    
    
    # to use the condition - just an example
    if condition_trial_duration(self, t, tstart, response_window, tlick):
        print('main condition is met, we can start a new trial')
        
    
    
    def trial_has_started(self):
        if self.trialstarted:
            print('trial has started')
            self.trialstarted=False
        
        
    def check_animal_quiet(self):
        #p1 = self.piezo_reader.piezo_adder1
        #p2 = self.piezo_reader.piezo_adder2
        
        required_samples = self.QW*60 # Serial runs in 60 Hz        
        p1 = np.array(self.piezo_reader.piezo_adder1,dtype=np.uint16)
        p2 = np.array(self.piezo_reader.piezo_adder2,dtype=np.uint16)
        
        
        # Wait until there is enough data to check the criteria
        while len(p1) < required_samples or len(p2) < required_samples:
            print('Waiting for enough data to check quiet period..')
            # refresh data
            p1 = np.array(self.piezo_reader.piezo_adder1,dtype=np.uint16)
            p2 = np.array(self.piezo_reader.piezo_adder2,dtype=np.uint16)
            
        # Now that there is enough data, check for licks in the last QW seconds        
        first_idx = len(p1)-required_samples
        #first_idx_r = len(p2)-required_samples
        
        quiet_left = max(p1[first_idx:]) < self.threshold_left
        quiet_right = max(p2[first_idx:]) < self.threshold_right
               
        loc_max1 = np.argwhere(p1 == max(p1))[-1]
        loc_max2 = np.argwhere(p2 == max(p2))[-1]
        
        if quiet_left and quiet_right:
            self.animal_quiet = True
            return True, None, None
        else:
            print('Licks detected during Quiet Window')
            return False, loc_max1, loc_max2
                
        
        
        
'''   



