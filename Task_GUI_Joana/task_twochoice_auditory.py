# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:51:07 2024

@author: JoanaCatarino
"""

import threading
import numpy as np
import time
import csv
import os
import random
from PyQt5.QtCore import QTimer
from piezo_reader import PiezoReader
from file_writer import create_data_file
from gpio_map import *
from sound_generator import tone_10KHz, tone_5KHz, white_noise


class TwoChoiceAuditoryTask:
    
    def __init__(self, gui_controls, csv_file_path): 
    
        # Directory to save file with trials data
        self.csv_file_path = csv_file_path
        self.save_dir = os.path.dirname(csv_file_path)
        os.makedirs(self.save_dir, exist_ok=True)
        self.file_path = csv_file_path # use the csv file name
        self.trials = [] # list to store trial data
        
        # Connection to GUI
        self.gui_controls = gui_controls
        self.piezo_reader = gui_controls.piezo_reader
        
        # Get the selected Animal ID from the GUI dropdown
        self.animal_id = str(self.gui_controls.ui.ddm_Animal_ID.currentText()).strip()
        
        # Load the animal-specific spout-tone mapping
        self.assignment_file = '/home/rasppi-ephys/spout_tone/spout_tone_generator.csv'
        self.spout_5KHz = None
        self.spout_10KHz = None
        self.load_spout_tone_mapping()

        # Experiment parameters
        self.QW = 3 # Quiet window in seconds
        self.ITI = 0.1 # Inter-trial interval in seconds
        self.RW = 1 # Response window in seconds
        self.threshold_left = 20
        self.threshold_right = 20
        self.valve_opening = 0.2  # Reward duration   
        
        # Counters
        self.total_trials = 0
        self.total_licks = 0
        self.licks_left = 0
        self.licks_right = 0
        self.correct_trials = 0
        self.incorrect_trials = 0
        self.early_licks = 0
        self.omissions = 0
        
        # Booleans
        self.trialstarted = False
        self.running = False
        
        # Time variables
        self.tstart = None # start of the task
        self.ttrial = None # start of the trial
        self.t = None # current time
        self.tlick_l = None # last lick left spout
        self.tlick_r = None # last lick right spout
        self.tlick = None # time of 1st lick within response window
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
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
        self.correct_trials = 0
        self.incorrect_trials = 0
        self.early_licks = 0
        self.omissions = 0
        
        # Update GUI display
        self.gui_controls.update_total_licks(0)
        self.gui_controls.update_licks_left(0)
        self.gui_controls.update_licks_right(0)
        self.gui_controls.update_correct_trials(0)
        self.gui_controls.update_incorrect_trials(0)
        self.gui_controls.update_early_licks(0)
        self.gui_controls.update_omissions(0)
        
        # Reset the performance plot
        self.gui_controls.lick_plot.reset_plot() # plot main tab
        self.gui_controls.lick_plot_ov.reset_plot() # plot overview tab
        
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
        
    
    def load_spout_tone_mapping(self):
        """ Reads the CSV file and assigns the correct spout for each frequency based on the animal ID. """
        
        if not os.path.isfile(self.assignment_file):
            print(f"Error: Assignment file not found at {self.assignment_file}")
            return False  
    
        with open(self.assignment_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                row = {key.strip(): value.strip() for key, value in row.items()}  # Clean all spaces
                
                if row['Animal'] == self.animal_id:  
                    self.spout_5KHz = row['5KHz']
                    self.spout_10KHz = row['10KHz']
    
                    print(f"Loaded mapping: 5KHz -> {self.spout_5KHz}, 10KHz -> {self.spout_10KHz}")
                    return True  
    
        print(f"Warning: No mapping found for Animal {self.animal_id}. Check the CSV file.")
        return False 
    
    
    def check_animal_quiet(self):
        
        """ Continuously checks for a quiet period before starting a trial, unless QW = 0 """
        
        if self.QW == 0:
            return True
        
        required_samples = self.QW*60 # Serial runs in 60 Hz   
        
        while True:
            if not self.running:
                return False
            
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
            self.total_trials +=1
            self.ttrial = self.t # Update trial start time
            self.first_lick = None # Reset first lick at the start of each trial
            
            # Randomly select the a cue sound for this trial (either 5KHz or 10KHz) and retrieve correct spout
            self.current_tone = random.choice(['5KHz', '10KHz'])
            self.correct_spout = self.spout_5KHz if self.current_tone == "5KHz" else self.spout_10KHz
            print(f'current tone:{self.current_tone} - correct spout:{self.correct_spout}')
            
            # Play sound
            self.sound_cue(self.current_tone)
            print(f'Trial {self.total_trials}: Playing {self.current_tone} tone - correct spout:{self.correct_spout}.')
            
            
            # Start LED in a separate thread
            threading.Thread(target=self.led_indicator, args=(self.RW,)).start() # to be deleted in the real task
            print(f"LED ON at t: {self.t:.2f} sec (Trial: {self.total_trials})")
            
            # Start monitoring licks within response window
            self.check_licks_in_RW()
                
            self.trialstarted = False
            
            # Initialize trial data
            trial_data = {
                'trial_number': self.total_trials,
                'trial_time': self.ttrial,
                'lick': 0,
                'left_spout': 0,
                'right_spout': 0,
                'lick_time': None,
                'RW': self.RW,
                'QW': self.QW,
                'ITI': self.ITI,
                'Threshold_left': self.threshold_left,
                'Threshold_right': self.threshold_right}
            
            self.trials.append(trial_data) # Store trial data
            
            self.gui_controls.update_total_trials(self.total_trials)
            
            # Append trial data to csv file
            self.append_trial_to_csv(trial_data)
            
    
    def sound_cue(self, frequency):
        if frequency == '5KHz':
            tone_5KHz()
        elif frequency == '10KHz':
            tone_10KHz()
    
    
    def led_indicator(self, RW):
        
        """ Turn on LED during trial duration without blocking main loop"""
        
        led_white_l.on()
        time.sleep(self.RW) # This should actually be changed to the duration of the full trial
        led_white_l.off()
     
        
    def check_licks_in_RW(self):
        """Monitors licks within the response window (RW) and logs omissions if no lick occurs."""
        
        start_time = time.time()
        lick_detected = False
    
        while (time.time() - start_time) < self.RW:
            p1 = list(self.piezo_reader.piezo_adder1)  # Left spout data
            p2 = list(self.piezo_reader.piezo_adder2)  # Right spout data
    
            # Check for left spout lick
            if p1 and p1[-1] > self.threshold_left:
                with self.lock:
                    self.tlick_l = self.t
                    elapsed_left = self.tlick_l - self.ttrial
    
                    if self.first_lick is None and elapsed_left > 0:
                        self.first_lick = 'left'
                        self.tlick = self.tlick_l
                        lick_detected = True
    
                        if self.correct_spout == 'left':
                            threading.Thread(target=self.reward, args=('left',)).start()
                            self.update_trial_data(1, left_spout=1)
                        else:
                            threading.Thread(target=self.white_noise, daemon=True).start()
                            print('Wrong spout')
                            self.incorrect_trials += 1
                            self.gui_controls.update_incorrect_trials(self.incorrect_trials)
                            
                        break
    
            # Check for right spout lick
            if p2 and p2[-1] > self.threshold_right:
                with self.lock:
                    self.tlick_r = self.t
                    elapsed_right = self.tlick_r - self.ttrial
    
                    if self.first_lick is None and elapsed_right > 0:
                        self.first_lick = 'right'
                        self.tlick = self.tlick_r
                        lick_detected = True
    
                        if self.correct_spout == 'right':
                            threading.Thread(target=self.reward, args=('right',)).start()
                            self.update_trial_data(1, right_spout=1)
                        else:
                            threading.Thread(target=self.white_noise, daemon=True).start()
                            print('Wrong spout')
                            self.incorrect_trials += 1
                            self.gui_controls.update_incorrect_trials(self.incorrect_trials)
                            
                        break
    
            time.sleep(0.001)  # Reduce CPU load

        # If no lick occurred, log omission
        if not lick_detected:
            print('Omission')
            self.omissions += 1
            self.gui_controls.update_omissions(self.omissions)
   
    
    def reward(self, side):
        """Delivers a reward without blocking the main loop."""

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
    
      
    
    def white_noise(self):
        white_noise()
    
    
    def main(self):
        
        while self.running:
            self.t = time.time() - self.tstart # update current time based on the elapsed time
            
           
            # Start a new trial if enough time has passed since the last trial and all conditions are met
            if (self.ttrial is None or (self.t - (self.ttrial + self.RW) > self.ITI)):
                if self.check_animal_quiet():
                    self.start_trial()
                    
            
            
            
    def append_trial_to_csv(self, trial_data):
        """ Append trial data to the CSV file. """
        file_exists = os.path.isfile(self.file_path)
        
        # Replace None or empty values with NaN
        trial_data = {key: (value if value is not None else np.nan) for key, value in trial_data.items()}
        
        with open(self.file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=trial_data.keys())
            if not file_exists:
                writer.writeheader()  # Write header only if file does not exist
            writer.writerow(trial_data)  # Append trial data
                
                
    def set_thresholds(self, left, right):
        """Sets the thresholds for the piezo adders and updates the GUI."""
        self.threshold_left = left
        self.threshold_right = right
        
        # Update the GUI thresholds
        self.gui_controls.update_thresholds(self.threshold_left, self.threshold_right)
   
   