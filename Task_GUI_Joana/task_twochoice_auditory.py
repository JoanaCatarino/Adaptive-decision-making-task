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
        
        # Path to the csv file containing sound-spout assignments
        self.assignment_file = '/home/rasppi-ephys/spout_tone/spout_tone_generator.csv'
        
        # Default values in case mapping fails
        self.spout_5KHz = None
        self.spout_10KHz = None
        
        if self.load_spout_tone_mapping():
            print(f' For animal {self.animal_id}, mapping loaded is 5KHz:{self.spout_5KHz}, 10KHz:{self.spout_10KHz}')
        else:
            print('No spout-tone assignment found')

        # Experiment parameters
        self.QW = 3 # Quiet window in seconds
        self.ITI = 0.1 # Inter-trial interval in seconds
        self.RW = 1.5 # Response window in seconds
        self.threshold_left = 20
        self.threshold_right = 20
        self.valve_opening = 0.2  # Reward duration   
        self.WW = 1 # Waiting Window - animals can't lick in order to receive the cue
        
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
        
        # Update GUI display
        self.gui_controls.update_total_licks(0)
        self.gui_controls.update_licks_left(0)
        self.gui_controls.update_licks_right(0)
        
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
        
        """ Initiates a trial following the correct structure """
        
        with self.lock:
            self.trialstarted = True
            trial_number= self.total_trials +1
            self.ttrial = self.t # Update trial start time
            self.first_lick = None # Reset first lick at the start of each trial
            
            # Randomly select the a cue sound for this trial (either 5KHz or 10KHz)
            self.current_tone = random.choice(['5KHz', '10KHz'])
            
            # Determine the correct response spout for this tone
            self.correct_spout = self.spout_5KHz if self.current_tone == "5KHz" else self.spout_10KHz
            
            print(f'Trial {trial_number} started')

            # 1. Start light thread
            self.light_thread = threading.Thread(target=self.manage_light)
            self.light_thread.start()
            
            # 2. Waiting Window - No licking allowed
            time.sleep(0.001) # small delay to ensure light turns on before checking
            if self.detect_licks_during_waiting_window():
                print(f'Trial{trial_number} aborted: licks in waiting window')
                self.light_off()
                return # abort trial and reset
            
            # 3. Play the sound cue and open response window
            print(f'Trial {trial_number}: Playing {self.current_tone} tone.')
            self.play_sound(self.current_tone)
            self.detect_licks()
            
            # 4. Determine Trial outcome
            if self.first_lick:
                if self.first_lick == self.correct_spout:
                    print(f'Trial {trial_number}: Correct choice! Delivering reward')
                    self.reward(self.first_lick)
                else:
                    print(f'Trial {trial_number}: Incorrect choice! Delivering punishment')
                    self.play_sound('white_noise') # Punishment
                    
            self.light_off() # Turn off the light
            print(f'Trial {trial_number} ended')
            self.trialstarted = False
                       
            
            # Initialize trial data
            trial_data = {
                'trial_number': trial_number,
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
            
            self.total_trials = trial_number
            self.gui_controls.update_total_trials(self.total_trials)
            
            # Append trial data to csv file
            self.append_trial_to_csv(trial_data)
            
    
    def manage_light(self):
        led_blue.on()
        while self.trialstarted:
        time.sleep(0.001)
        led_blue.off()
        
    
    def light_off(self):
        self.trialstarted = False
        time.sleep(0.001)
        led_blue.off()
        
        
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
                        self.tlick = self.tlick_l
    
                        if self.correct_spout == 'Left':
                            threading.Thread(target=self.reward, args=('left',)).start()
                        
                            # Update trial data
                            self.trials[-1]['lick'] = 1
                            self.trials[-1]['left_spout'] = 1
                            self.trials[-1]['lick_time'] = self.tlick
                        
                            self.append_trial_to_csv(self.trials[-1])
    
                            self.total_licks += 1
                            self.licks_left += 1
                            self.gui_controls.update_total_licks(self.total_licks)
                            self.gui_controls.update_licks_left(self.licks_left)
                        else:
                            print(f'Incorrect choice: licked left, but correct was {self.correct_spout}')
                        
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
                        self.tlick = self.tlick_r
    
                        if self.correct_spout == 'Right':
                            threading.Thread(target=self.reward, args=('right',)).start()
                            
                            # Update trial data
                            self.trials[-1]['lick'] = 1
                            self.trials[-1]['right_spout'] = 1
                            self.trials[-1]['lick_time'] = self.tlick
                            
                            self.append_trial_to_csv(self.trials[-1])
        
                            self.total_licks += 1
                            self.licks_right += 1
                            self.gui_controls.update_total_licks(self.total_licks)
                            self.gui_controls.update_licks_right(self.licks_right)
                        else:
                            print(f'Incorrect choice: licked right, but correct was {self.correct_spout}')
                        
                        
    
    def reward(self, side):
        
        """Delivers a reward without blocking the main loop."""
        
        print(f"Delivering reward - {side}")
    
        # Ensure pump action executes properly with a short delay
        #time.sleep(0.01)
    
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
    

    def play_sound(self, frequency):
        """Plays a sound cue (5KHz or 10KHz) using the predefined tone functions."""
        
        if frequency == "5KHz":
            print("Playing 5KHz tone...")
            tone_5KHz()  # Calls your function
        elif frequency == "10KHz":
            print("Playing 10KHz tone...")
            tone_10KHz()  # Calls your function
        elif frequency == 'white_noise':
            white_noise()
            
        
    def main(self):
        
        while self.running:
            self.t = time.time() - self.tstart # update current time based on the elapsed time
            
           
            # Start a new trial if enough time has passed since the last trial and all conditions are met
            if (self.ttrial is None or (self.t - (self.ttrial + self.RW) > self.ITI)):
                if self.check_animal_quiet():
                    self.start_trial()
                    
            # Run lick detection continuously
            self.detect_licks()
            
            
            
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
    



       
