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
from collections import deque
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPalette
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
        self.ITI_min = 3 # default ITI min
        self.ITI_max = 9 # default ITI
        self.ITI = round(random.uniform(self.ITI_min, self.ITI_max),1) #Random ITI between 3-9 sec with ms precision
        self.RW = 3 # Response window in seconds
        self.threshold_left = 20
        self.threshold_right = 20
        self.valve_opening = 0.2  # Reward duration   
        self.WW = 1 # waiting window
        
        # Counters
        self.total_trials = 0
        self.total_licks = 0
        self.licks_left = 0
        self.licks_right = 0
        self.correct_trials = 0
        self.incorrect_trials = 0
        self.early_licks = 0
        self.omissions = 0
        self.trial_duration = 0
        self.sound_5KHz = 0
        self.sound_10KHz = 0
        self.autom_rewards = 0
        self.catch_trials = 0
        
        # Booleans
        self.trialstarted = False
        self.running = False
        self.first_trial = True
        self.next_trial_ready = False
        self.early_lick_counted = False
        self.sound_played = False
        self.omission_counted = False
        
        # Time variables
        self.tstart = None # start of the task
        self.ttrial = None # start of the trial
        self.t = None # current time
        self.tlick_l = None # last lick left spout
        self.tlick_r = None # last lick right spout
        self.tlick = None # time of 1st lick within response window
        self.RW_start = None
        self.current_time = None
        self.tend = None # end of the trial
        self.next_trial_eligible = False
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        self.first_lick = None
        
        # Debiasing variables 
        self.decision_history = [] # Stores last N trial outcomes
        self.min_trials_debias = 15 # Number of trials for debiasing
        self.decision_SD = 0.5 # standart deviation for Gaussian sampling
        self.correct_spout = None 
        self.selected_side = None
        self.bias_value = None
        self.debias_value = None
        
        # Trial monitor
        self.monitor_history = deque(maxlen=15)

    def start (self):
        print ('Spout Sampling task starting')
        
        # Turn the LEDS ON initially
        pump_l.on()
        pump_r.on()
        
        self.gui_controls.performance_plot.reset_plot() # Plot main tab
        self.gui_controls.performance_plot_ov.reset_plot() # Plot overview tab
        
        self.running = True
        self.tstart = time.time() # record the start time
        
        # Start main loop in a separate thread
        self.print_thread = threading.Thread(target=self.main, daemon=True)
        self.print_thread.start()   
        
        
    def stop(self):
        print("Stopping Spout Sampling Task...")
        
        self.running = False
        self.trialstarted = False
        
        if self.print_thread.is_alive():
            self.print_thread.join()
        pump_l.on()
        led_blue.off()
        
    
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
    
    def debias(self):
        """ 
        Adjusts trial assignment based on recent lick history to reinforce the weaker spout.
        """
        
        recent_trials = self.decision_history[-self.min_trials_debias:]  # Last N trials
        
        if not recent_trials:
            self.bias_value = 0.5 
            self.gui_controls.ui.box_Bias.setText(f"{self.bias_value:.1f}")
            return random.choice(["left", "right"])  

        # Count left and right licks
        left_licks = sum(1 for t in recent_trials if t == "L")
        right_licks = sum(1 for t in recent_trials if t == "R")
        total_licks = left_licks + right_licks

        if total_licks == 0:
            self.bias_value = 0.5 # Keep it neutral
            self.gui_controls.ui.box_Bias.setText(f"{self.bias_value:.1f}")
            return random.choice(["left", "right"])  

        # Compute bias based on lick history (proportion of right licks)
        self.bias_value = right_licks / total_licks

        # Apply Gaussian sampling to introduce slight randomness
        self.debias_val = random.gauss(self.bias_value, self.decision_SD)

        # Assign trials to reinforce the underrepresented spout
        self.selected_side = "right" if self.debias_val < 0.5 else "left"  

        # Update GUI with bias value
        self.gui_controls.ui.box_Bias.setText(f"{self.bias_value:.1f}")

        return self.selected_side
  
    
    
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
            
    
     
    def start_trial(self):
        
        """ Initiates a trial, runs LED in paralledl, and logs trial start"""
        
        with self.lock:
            
            if self.trialstarted:
                return
            
            self.trialstarted = True
            self.total_trials +=1
            self.gui_controls.update_total_trials(self.total_trials)
            self.ttrial = time.time() # Update trial start time
            self.first_lick = None # Reset first lick at the start of each trial
            self.early_lick_counted = False # For saving data
            self.sound_played = False # For saving data
            self.omission_counted = False # For saving data
            self.data_saved = False
            self.plot_updated = False
            
            # Randomly select the a cue sound  and apply debiasing when needed
            self.correct_spout = self.debias()  # Apply debiasing

            self.current_tone = "5KHz" if self.correct_spout == self.spout_5KHz else "10KHz"
            print(
                f' trial:{self.total_trials}  current_tone:{self.current_tone} - correct_spout:{self.correct_spout}')
         
            # Update gui with trial type
            self.gui_controls.ui.box_CurrentTrial.setText(f"Tone: {self.current_tone}  |  Spout: {self.correct_spout}")
            self.gui_controls.ui.OV_box_CurrentTrial.setText(f"Tone: {self.current_tone}  |  Spout: {self.correct_spout}")
            
            # Update Sound Counters
            if self.current_tone == '5KHz':
                self.sound_5KHz +=1
                self.gui_controls.update_sound_5KHz(self.sound_5KHz)
            elif self.current_tone == '10KHz':
                self.sound_10KHz +=1
                self.gui_controls.update_sound_10KHz(self.sound_10KHz)
            
            # Turn LED on
            threading.Thread(target=self.blue_led_on, daemon=True).start()
            
            
            if self.detect_licks_during_waiting_window():  # If a lick happens, abort trial
                print("Trial aborted due to early lick.")
                self.early_licks += 1
                self.early_lick_counted = True
                self.gui_controls.update_early_licks(self.early_licks)
                self.trialstarted = False  # Reset trial state
                threading.Thread(target=self.blue_led_off, daemon=True).start()
                self.tend= time.time()
                self.trial_duration = (self.tend-self.ttrial)
                self.gui_controls.update_trial_duration(self.trial_duration)
                self.schedule_next_trial()
                # Save trial data
                self.save_data()
                return  # Exit trial 
           
            # Play sound  
            self.play_sound(self.current_tone)
            self.sound_played = True
            
            autom_rewards = self.gui_controls.ui.chk_AutomaticRewards.isChecked()
            
            if autom_rewards:
                print(f"Automatic reward given at {self.correct_spout}")
                threading.Thread(target=self.reward, args=(self.correct_spout,)).start()
                self.trialstarted = False
                threading.Thread(target=self.blue_led_off, daemon=True).start()
                self.autom_rewards += 1
                self.gui_controls.update_autom_rewards(self.autom_rewards)
                self.tend = time.time()
                self.trial_duration = (self.tend-self.ttrial)
                self.gui_controls.update_trial_duration(self.trial_duration)
                self.schedule_next_trial()
                # Save trial data
                self.save_data()
                
            if not autom_rewards:            # **If Automatic Reward is NOT checked, proceed with standard response window**
                self.RW_start = time.time()  # Start response window
            
                # Wait for response window to finish if no lick happens
                threading.Thread(target=self.wait_for_response, daemon=True).start()
            
    
    def play_sound(self, frequency):
        
        if frequency == "5KHz":
            tone_5KHz()  
        elif frequency == "10KHz":
            tone_10KHz()
        elif frequency == "white_noise":
            white_noise()

        #threading.Thread(target=play, daemon=True).start()

        
    def blue_led_on(self):
        led_blue.on()
        
    
    def blue_led_off(self):
        led_blue.off()
        
    
    def detect_licks_during_waiting_window(self):
        """ Detects licks during the waiting window (WW) and aborts the trial if necessary. """
        
        WW_start = time.time()  # Mark the WW start time
        
        ignore_licks = self.gui_controls.ui.chk_IgnoreLicksWW.isChecked() # Check if Ignore Licks during WW option is checked in the gui
        
        while time.time() - WW_start < self.WW:  # Wait for WW duration
            p1 = list(self.piezo_reader.piezo_adder1)  # Left spout
            p2 = list(self.piezo_reader.piezo_adder2)  # Right spout
            
            # Check if a lick is detected
            if not ignore_licks:
                if p1 and p1[-1] > self.threshold_left:
                    return True  # Abort trial
        
                if p2 and p2[-1] > self.threshold_right:
                    return True  # Abort trial
            
            time.sleep(0.001)  # Small delay to prevent CPU overload
        
        return False  # No licks detected, trial can proceed    
    
    
    def schedule_next_trial(self):
        self.next_trial_ready = True
        print("Next trial is now allowed after ITI.")
    
        self.ITI = round(random.uniform(self.ITI_min, self.ITI_max),1)
    
        # Start the next trial after ITI delay
        threading.Timer(self.ITI, self.check_and_start_next_trial).start()
        
    
    def check_and_start_next_trial(self):
        """ Starts the next trial if conditions allow it """
        if self.next_trial_ready and not self.trialstarted:
            print("Starting next trial automatically.")
            self.start_trial()
    

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
                    self.tlick_l = time.time()
                    elapsed_left = self.tlick_l - self.RW_start
        
                    if self.first_lick is None and (0 < elapsed_left < self.RW):
                        self.first_lick = 'left'
                        self.tlick = self.tlick_l
                        self.decision_history.append("L")  # Store in history
                        self.decision_history = self.decision_history[-self.min_trials_debias:] # Keep last 15 trials
                            
                        if self.correct_spout == self.first_lick:
        
                            # Deliver reward in a separate thread
                            threading.Thread(target=self.reward, args=('left',)).start() 
            
                            self.correct_trials += 1
                            self.gui_controls.update_correct_trials(self.correct_trials)
                                
                                
                        else:
                            if not self.gui_controls.ui.chk_NoPunishment.isChecked():
                                self.play_sound('white_noise')
                                print('wrong spout')
                            else:
                                print('wrong spout - punishment skipped')
                            self.incorrect_trials +=1
                            self.gui_controls.update_incorrect_trials(self.incorrect_trials)
                            
                        
                        self.total_licks += 1
                        self.licks_left += 1
                        self.gui_controls.update_total_licks(self.total_licks)
                        self.gui_controls.update_licks_left(self.licks_left)
                        self.timer_3.cancel()
                        self.trialstarted = False
                        threading.Thread(target=self.blue_led_off, daemon=True).start()
                        self.tend = time.time()
                        self.trial_duration = (self.tend-self.ttrial)
                        self.gui_controls.update_trial_duration(self.trial_duration)
                        self.next_trial_eligible = True
                        # Save trial data
                        self.save_data()
                        return
                
        
        # Right piezo        
        if p2:
            latest_value2 = p2[-1]
        
            if latest_value2 > self.threshold_right:
                with self.lock:
                    self.tlick_r = time.time()
                    elapsed_right = self.tlick_r - self.RW_start
        
                    if self.first_lick is None and (0 < elapsed_right < self.RW):
                        self.first_lick = 'right'
                        self.tlick = self.tlick_r
                        self.decision_history.append("R")  # Store in history
                        self.decision_history = self.decision_history[-self.min_trials_debias:] # Keep last 15 trials
                            
                        if self.correct_spout == self.first_lick:
        
                            # Deliver reward in a separate thread
                            threading.Thread(target=self.reward, args=('right',)).start()
            
                            self.correct_trials += 1
                            self.gui_controls.update_correct_trials(self.correct_trials)
                            
                        else:
                            if not self.gui_controls.ui.chk_NoPunishment.isChecked():
                                self.play_sound('white_noise')
                                print('wrong spout')
                            else:
                                print('wrong spout - punishment skipped')
                            self.incorrect_trials +=1
                            self.gui_controls.update_incorrect_trials(self.incorrect_trials)
                            
                        
                        self.total_licks += 1
                        self.licks_right += 1
                        self.gui_controls.update_total_licks(self.total_licks)
                        self.gui_controls.update_licks_right(self.licks_right)
                        self.timer_3.cancel()
                        self.trialstarted = False
                        threading.Thread(target=self.blue_led_off, daemon=True).start()
                        self.tend = time.time()
                        self.trial_duration = (self.tend-self.ttrial)
                        self.gui_controls.update_trial_duration(self.trial_duration)
                        self.next_trial_eligible = True
                        # Save trial data
                        self.save_data()
                        return
                   

    def omission_callback(self):
        print('No licks detected - aborting trial')
        self.trialstarted = False
        threading.Thread(target=self.blue_led_off, daemon=True).start()
        self.tend = time.time()
        self.trial_duration = (self.tend-self.ttrial)
        self.gui_controls.update_trial_duration(self.trial_duration)
        self.omissions += 1
        self.omission_counted = True
        self.gui_controls.update_omissions(self.omissions)
        self.next_trial_eligible = True
        # Save trial data
        self.save_data()
      
    
    def wait_for_response(self):
        self.timer_3 = threading.Timer(self.RW, self.omission_callback)
        self.timer_3.start()
        
    
    def reward(self, side):
        """Delivers a reward without blocking the main loop."""
    
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
    
    
    def main(self):
        while self.running:
            
            if self.first_trial:
                print(f"ITI duration: {self.ITI} seconds")  # Print ITI value for debugging
                if self.check_animal_quiet():
                    self.start_trial()
                    self.first_trial = False
                    self.ITI = round(random.uniform(self.ITI_min, self.ITI_max),1)
                else:
                    pass
                
            if self.next_trial_eligible == True and ((time.time() - (self.tend)) >= self.ITI) and not self.trialstarted:
                print(f"ITI duration: {self.ITI} seconds")  # Print ITI value for debugging
                if self.check_animal_quiet():
                    self.start_trial()
                    self.next_trial_eligible = False
                    self.ITI = round(random.uniform(self.ITI_min, self.ITI_max),1)
             
            self.detect_licks()
            
    
    def save_data(self):
        """ Saves trial data, ensuring missing variables are filled with NaN while maintaining structure."""
        
        # Prevent duplicate calls
        if hasattr(self, 'data_saved') and self.data_saved:
            return
        self.data_saved = True  # Mark data as saved to avoid duplicate calls
        
        # Update plot
        self.gui_controls.update_performance_plot(self.total_trials, self.correct_trials, self.incorrect_trials)
        
        # Determine if a reward was given
        was_rewarded = ((getattr(self, 'first_lick', None) and getattr(self, 'correct_spout', None) == getattr(self, 'first_lick', None) and not getattr(self, 'catch_trial_counted', False)) or
                        self.gui_controls.ui.chk_AutomaticRewards.isChecked())
    
        # Determine if punishment was given
        was_punished = (getattr(self, 'first_lick', None) and getattr(self, 'correct_spout', None) != getattr(self, 'first_lick', None) and not getattr(self, 'catch_trial_counted', False))
    
        # Determine if omission happened
        was_omission = getattr(self, 'omission_counted', False) and not getattr(self, 'first_lick', None)
    
        # Ensure punishment and omission never happen together
        if was_punished:
            was_omission = 0
    
        # Define trial data, using hasattr() to check for missing variables
        trial_data = [
            np.nan if not hasattr(self, 'total_trials') else self.total_trials,  # trial number
            np.nan if not hasattr(self, 'ttrial') else self.ttrial,  # trial start
            np.nan if not hasattr(self, 'tend') else self.tend,  # trial end
            np.nan if not hasattr(self, 'trial_duration') else self.trial_duration,  # trial duration
            np.nan if not hasattr(self, 'ITI') else self.ITI,  # ITI
            np.nan if not hasattr(self, 'current_block') else self.current_block,  # block
            np.nan if not hasattr(self, 'early_lick_counted') else (1 if self.early_lick_counted else 0),  # early licks
            np.nan if not hasattr(self, 'sound_played') else (1 if self.sound_played else 0),  # stim
            np.nan if not hasattr(self, 'current_tone') else (1 if self.current_tone == '5KHz' else 0),  # 5KHz
            np.nan if not hasattr(self, 'current_tone') else (1 if self.current_tone == '10KHz' else 0),  # 10KHz
            np.nan if not hasattr(self, 'first_lick') else (1 if self.first_lick else 0),  # lick
            np.nan if not hasattr(self, 'first_lick') else (1 if self.first_lick == 'left' else 0),  # left spout
            np.nan if not hasattr(self, 'first_lick') else (1 if self.first_lick == 'right' else 0),  # right spout
            np.nan if not hasattr(self, 'tlick') else (self.tlick if self.first_lick else np.nan),  # lick_time
            np.nan if not hasattr(self, 'first_lick') else (1 if was_rewarded else 0),  # reward
            np.nan if not hasattr(self, 'first_lick') else (1 if was_punished else 0),  # punishment
            np.nan if not hasattr(self, 'first_lick') else (1 if was_omission else 0),  # omission
            np.nan if not hasattr(self, 'RW') else self.RW,
            np.nan if not hasattr(self, 'QW') else self.QW,
            np.nan if not hasattr(self, 'WW') else self.WW,
            np.nan if not hasattr(self, 'valve_opening') else self.valve_opening,
            np.nan if not hasattr(self, 'ITI_min') else self.ITI_min,
            np.nan if not hasattr(self, 'ITI_max') else self.ITI_max,
            np.nan if not hasattr(self, 'threshold_left') else self.threshold_left,
            np.nan if not hasattr(self, 'threshold_right') else self.threshold_right,
            1 if self.gui_controls.ui.chk_AutomaticRewards.isChecked() else np.nan,
            1 if self.gui_controls.ui.chk_NoPunishment.isChecked() else np.nan,
            1 if self.gui_controls.ui.chk_IgnoreLicksWW.isChecked() else np.nan,
            np.nan if not hasattr(self, 'catch_trial_counted') else (1 if self.catch_trial_counted else 0),  # catch trials
            np.nan if not hasattr(self, 'is_distractor_trial') else (1 if self.is_distractor_trial else 0),  # Distractor trial flag
            np.nan if not hasattr(self, 'distractor_led') else (1 if self.distractor_led == "left" else 0),  # Distractor on left
            np.nan if not hasattr(self, 'distractor_led') else (1 if self.distractor_led == "right" else 0),  # Distractor on right
            np.nan if not hasattr(self, 'tstart') else self.tstart  # session start
        ]
    
        # Append data to the CSV file
        with open(self.csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(trial_data)
            
        # **Convert block type for display**
        block_type_display = {
            "sound": "S",
            "action-left": "AL",
            "action-right": "AR"
        }.get(self.current_block, "")  # If undefined, show empty string ""
    
        # **Extract Trial History Info & Update GUI**
        trial_outcome = "correct" if trial_data[14] == 1 else "incorrect" if trial_data[15] == 1 else "omission"
    
        trial_data_gui = {
            "block_type": block_type_display,  # Use converted block type (empty if undefined)
            "outcome": trial_outcome,  # Correct, Incorrect, Omission
            "trial_number": self.total_trials  # Trial ID
        }
        
        if isinstance(trial_data_gui, dict):  # Ensure only valid dictionaries are stored
            self.monitor_history.append(trial_data_gui) 
        else:
            print("Warning: Invalid trial data format detected:", trial_data_gui)
    
        # **Update the GUI**
        self.update_trial_history()
        
        
    def update_trial_history(self):
        """ Updates the GUI labels for trial history using a single outcome label per trial """
    
        for i, trial in enumerate(self.monitor_history):
            col = i + 1  # QLabel names are lbl_O1 to lbl_O15 (one per trial)
            
            # **Update Block Type (S, AL, AR, or Empty)**
            lbl_block = getattr(self.gui_controls.ui, f"lbl_B{col}", None)
            if lbl_block:
                lbl_block.setText(trial["block_type"])
    
            # **Find the Outcome Label**
            lbl_outcome = getattr(self.gui_controls.ui, f"lbl_O{col}", None)
    
            # **Reset previous color**
            if lbl_outcome:
                lbl_outcome.setStyleSheet("")  # Clear previous color
    
                # **Assign color based on outcome**
                if trial["outcome"] == "correct":
                    lbl_outcome.setStyleSheet("background-color: #0DE20D;")
                elif trial["outcome"] == "incorrect":
                    lbl_outcome.setStyleSheet("background-color: red;")
                else:
                    lbl_outcome.setStyleSheet("background-color: gray;")
                    
            # **Update Trial Number**
            lbl_T = getattr(self.gui_controls.ui, f"lbl_T{col}", None)
            if lbl_T:
                lbl_T.setText(str(trial["trial_number"])) 
