# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:55:09 2024

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
from sound_generator import tone_16KHz, tone_8KHz, white_noise
from pathlib import Path


class AdaptiveSensorimotorTask:
    
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
        self.assignment_file = Path.home() / 'spout_tone' / 'spout_tone_generator.csv'
        self.spout_8KHz = None
        self.spout_16KHz = None
        self.load_spout_tone_mapping()

        # Experiment parameters
        self.QW = 3 # Quiet window in seconds
        self.ITI_min = 3 # default ITI min
        self.ITI_max = 6 # default ITI max
        self.ITI = round(random.uniform(self.ITI_min, self.ITI_max),1) #Random ITI between 3-6 sec with ms precision
        self.RW = 3 # Response window in seconds
        self.threshold_left = 1
        self.threshold_right = 1
        self.valve_opening = 0.08  # Reward duration   
        self.WW = 1 # waiting window
        
        # Block parameters
        self.current_block = 'sound'  # Always start with sound block
        self.trials_in_block = 0
        self.trial_limit = random.randint(40, 60)  # Random minimal trial count per block - should be 40-60
        print(f'First block, #trials = {self.trial_limit}')
        
        # Alternation controller
        # After the first sound block, choose action-left or action-right randomly.
        # Then alternate that action side on every subsequent action block, always interleaved with sound.
        self.next_action_side = random.choice(['left', 'right'])
        
        # History for accuracy check (only current block, only valid trials, last 20)
        self.trial_history = deque(maxlen=20)
        self.block_valid_trials = 0
        
        # Block counters
        self.sound_block_count = 0
        self.action_left_block_count = 0
        self.action_right_block_count = 0
        self.last_block = None  # Track last block to prevent duplicate counting
        
        # Sliding window for block switching (last 20 trials) # Should be last 20 trials
        self.recent_correct_trials = 0
        self.recent_total_trials = 0
        
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
        self.sound_8KHz = 0
        self.sound_16KHz = 0
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
        self.catch_trial_counted = False
        self.data_saved = False
        self.plot_updated = False
        
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
        self.trial_saved = False # added 15/05/2025
        
        # Catch trials (blue light but no sound cue)
        self.catch_trials_fraction = 0.1 # 10% of the trials will be catch trials
        self.is_catch_trial = False
        
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
        print ('Adaptive Sensorimotor Task starting')
        
        # Turn the LEDS ON initially
        pump_l.on()
        pump_r.on()
        
        self.gui_controls.performance_plot.reset_plot() # Plot main tab
        self.gui_controls.performance_plot_ov.reset_plot() # Plot overview tab
        
        self.running = True
        self.tstart = time.time() # record the start time
        
        self.sound_block_count +=1 # Count the first block
        self.gui_controls.update_sound_blocks(self.sound_block_count)
        self.last_block = 'sound'
        
        # Start main loop in a separate thread
        self.print_thread = threading.Thread(target=self.main, daemon=True)
        self.print_thread.start()   
        
        
    def stop(self):
        print("Stopping Adaptive Sensorimotor Task...")
        
        self.running = False
        self.trialstarted = False
        
        if self.print_thread.is_alive():
            self.print_thread.join()
            
        if self.trialstarted and not self.trial_saved:  #Added all this part 15/05/2025
            self.tend = time.time()
            self.trial_duration = self.tend - self.ttrial
            self.gui_controls.update_trial_duration(self.trial_duration)
            self.save_data()
            self.trial_saved = True
            print("Saved trial during manual stop.")
        
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
                    self.spout_8KHz = row['8KHz']
                    self.spout_16KHz = row['16KHz']
    
                    print(f"Loaded mapping: 8KHz -> {self.spout_8KHz}, 16KHz -> {self.spout_16KHz}")
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
    
             
    def should_switch_block(self):
        """
        Return True if BOTH:
          - we have at least 20 valid trials in the current block, and
          - the last 20 valid trials are ≥ 85% correct.
        Valid = lick-based trials (correct or incorrect). Catch & omissions excluded.
        """        
        valid_trials = [t for t in self.trial_history if t is not None]
        
        if len(valid_trials) < 20:
            return False
        accuracy = (sum(valid_trials[-20:]) / 20.0) * 100.0
        return accuracy >= 85.0
    
    def eligible_to_switch(self):
        """Return True only if minimum trial count reached AND accuracy rule holds."""
        return (self.trials_in_block >= self.trial_limit) and self.should_switch_block()

    def maybe_switch_block(self):
        """Evaluate and switch block if eligibility is satisfied."""
        if self.eligible_to_switch():
            self.switch_block()
            
        print(f"[maybe_switch_block] block_valid_trials={self.block_valid_trials}")


    def switch_block(self):
        # Switch between sound and action blocks only if criteria is met (85% correct)
        # Block type selection should have a set structure. Session always starts with Sounds and after that Action-right or left are randomly
            #picked. From that moment on, the structure is fixed: either S-AR-S-AL-S-AR-S-AL or S-AL-S-AR-S-AL-S-AR
        # Clear accuracy window for the new block and set a new trial limit (40-60)

        if self.current_block == "sound":
            # Enter action block on the planned side
            side = self.next_action_side
            self.current_block = f"action-{side}"
            # Toggle for the next time we leave sound
            self.next_action_side = "right" if side == "left" else "left"
        else:
            # From any action block, go back to sound
            self.current_block = "sound"
            # When entering sound, later we'll go to the toggled action side
        
        # Reset block-scoped state
        self.trials_in_block = 0
        self.block_valid_trials = 0
        self.trial_history.clear()  # reset valid-trial history for the new block
        self.trial_limit = random.randint(40, 60)  # new minimum trials for the new block
        print(f"New block '{self.current_block}' with min trials: {self.trial_limit}")
        
        # Reset debiasing history when a new sound block starts
        if self.current_block == "sound":
            self.decision_history = []
        
        # Update block counters only once per block switch
        if self.current_block != self.last_block:
            if self.current_block == "sound":
                self.sound_block_count += 1
                self.gui_controls.update_sound_blocks(self.sound_block_count)
            elif self.current_block == "action-left":
                self.action_left_block_count += 1
                self.gui_controls.update_action_l_blocks(self.action_left_block_count)
            elif self.current_block == "action-right":
                self.action_right_block_count += 1
                self.gui_controls.update_action_r_blocks(self.action_right_block_count)
            self.last_block = self.current_block  # Prevent duplicate counting
        
        print(f"Switching to {self.current_block} block")
        print(f"Block counts - Sound: {self.sound_block_count}, Action-Left: {self.action_left_block_count}, Action-Right: {self.action_right_block_count}")

    
    def start_trial(self):
        
        """ Initiates a trial, runs LED in paralledl, and logs trial start"""
        
        with self.lock:
            if self.trialstarted:
                return
            
            self.trial_saved = False # Added 15/05/2025
            self.trialstarted = True
            self.total_trials +=1
            self.gui_controls.update_total_trials(self.total_trials)
            self.trials_in_block +=1
            self.ttrial = time.time() # Update trial start time
            self.first_lick = None # Reset first lick at the start of each trial
            self.early_lick_counted = False # For saving data
            self.sound_played = False # For saving data
            self.omission_counted = False # For saving data
            self.catch_trial_counted = False
            self.data_saved = False
            self.plot_updated = False
            
            self.is_catch_trial = random.random() < self.catch_trials_fraction
            
            # Determine trial type
            if self.is_catch_trial:
                print(f'Trial {self.total_trials} - Catch trial')
                self.current_tone = None
                self.correct_spout = None
                self.catch_trial_counted = True
                self.catch_trials +=1
                self.gui_controls.update_catch_trials(self.catch_trials)
                self.gui_controls.ui.box_CurrentTrial.setText('Catch Trial')
                self.gui_controls.ui.OV_box_CurrentTrial.setText('Catch Trial')
            else:
                if self.current_block == "sound":
                    # Randomly select the a cue sound  and apply debiasing when needed
                    self.correct_spout = self.debias()  # Apply debiasing
                    self.current_tone = "8KHz" if self.correct_spout == self.spout_8KHz else "16KHz"
                    
                elif self.current_block == "action-left":
                    self.current_tone = random.choice(["8KHz", "16KHz"])  # Play sound, but it's ignored
                    self.correct_spout = "left"  # Always reward left, punish right
                
                elif self.current_block == "action-right":
                    self.current_tone = random.choice(["8KHz", "16KHz"])  # Play sound, but it's ignored
                    self.correct_spout = "right"  # Always reward right, punish left
                
                print(f"Trial {self.total_trials} | Block: {self.current_block} | Tone: {self.current_tone} | Correct spout: {self.correct_spout}")
                self.gui_controls.ui.box_CurrentTrial.setText(f"Block: {self.current_block}  |  {self.current_tone}  -  {self.correct_spout}")
                self.gui_controls.ui.OV_box_CurrentTrial.setText(f"Block: {self.current_block}  |  {self.current_tone}  -  {self.correct_spout}")
        
            # Update Sound Counters
            if self.current_tone == '8KHz':
                self.sound_8KHz +=1
                self.gui_controls.update_sound_8KHz(self.sound_8KHz)
            elif self.current_tone == '16KHz':
                self.sound_16KHz +=1
                self.gui_controls.update_sound_16KHz(self.sound_16KHz)
                
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
                if not self.trial_saved: # Added 15/05/2025
                    self.save_data()
                    self.trial_saved = True
                    
                # Evaluate possible switch even after early-lick abort (eligibility might already be met)
                self.maybe_switch_block()
                return  # Exit trial 
                
           
            # Play sound  
            self.play_sound(self.current_tone)
            
            # Start response window
            self.RW_start = time.time() 
             
            # Wait for response window to finish if no lick happens
            threading.Thread(target=self.wait_for_response, daemon=True).start()
                
            # Check for block switch
            if self.trials_in_block >= self.trial_limit:
                self.switch_block()
         
    
    def play_sound(self, frequency):
        
        if self.is_catch_trial:
            print('Catch trial: no sound played')
            return
        
        if frequency == "8KHz":
            tone_8KHz() 
            self.sound_played = True
        elif frequency == "16KHz":
            tone_16KHz()
            self.sound_played = True
        elif frequency == "white_noise":
            white_noise()

    def blue_led_on(self):
        led_blue.on()
        
    def blue_led_off(self):
        led_blue.off()
        
    
    def detect_licks_during_waiting_window(self):
        """ Detects licks during the waiting window (WW) and aborts the trial if necessary. """
        
        WW_start = time.time()  # Mark the WW start time
        
        while time.time() - WW_start < self.WW:  # Wait for WW duration
            p1 = list(self.piezo_reader.piezo_adder1)  # Left spout
            p2 = list(self.piezo_reader.piezo_adder2)  # Right spout
            
            # Check if a lick is detected
            if p1 and p1[-1] > self.threshold_left:
                print("Lick detected during WW! Aborting trial.")
                return True  # Abort trial
    
            if p2 and p2[-1] > self.threshold_right:
                print("Lick detected during WW! Aborting trial.")
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
        
        trial_result = None  # Default to None (omission)
        
        # Catch trial: Record licks without giving reward or punishment
        if self.is_catch_trial:
            if p1 and p1[-1] > self.threshold_left:
                
                with self.lock:
                    self.tlick_l = time.time()
                    elapsed_left = self.tlick_l - self.RW_start
                    
                    if self.first_lick is None and (0 < elapsed_left < self.RW):
                        self.first_lick = 'left'
                        self.tlick = self.tlick_l 
                        self.decision_history.append("L")  # Store in history
                        self.decision_history = self.decision_history[-self.min_trials_debias:] # Keep last 15 trials
                        print(f"Catch trial: Lick detected on LEFT spout")
                        
                        self.total_licks += 1
                        self.licks_left += 1
                        
                        # Update GUI values
                        self.gui_controls.update_total_licks(self.total_licks)
                        self.gui_controls.update_licks_left(self.licks_left)
        
                        # End trial 
                        self.timer_3.cancel()
                        self.trialstarted = False
                        threading.Thread(target=self.blue_led_off, daemon=True).start()
                        self.tend = time.time()
                        self.trial_duration = self.tend - self.ttrial
                        self.gui_controls.update_trial_duration(self.trial_duration)
                        self.is_catch_trial = False
                        self.next_trial_eligible = True
                        # Save trial data
                        if not self.trial_saved: # Added 15/05/2025
                            self.save_data()
                            self.trial_saved=True
                        
                        # Catch doesn't affect accuracy; still can check switch eligibility
                        self.maybe_switch_block()
                        return  # Exit function to prevent normal trial execution
                        
                        

            if p2 and p2[-1] > self.threshold_right:
                with self.lock:
                    self.tlick_r = time.time()
                    elapsed_right = self.tlick_r - self.RW_start
                    
                    if self.first_lick is None and (0 < elapsed_right < self.RW):
                        self.first_lick = 'right'
                        self.tlick = self.tlick_r  
                        self.decision_history.append("R")  # Store in history
                        self.decision_history = self.decision_history[-self.min_trials_debias:] # Keep last 15 trials
                        print(f"Catch trial: Lick detected on RIGHT spout at {self.tlick_r}, but no reward/punishment given.")
    
                        self.total_licks += 1
                        self.licks_right += 1
                
                        # Update GUI values
                        self.gui_controls.update_total_licks(self.total_licks)
                        self.gui_controls.update_licks_right(self.licks_right)
        
                        # End trial 
                        self.timer_3.cancel()
                        self.trialstarted = False
                        threading.Thread(target=self.blue_led_off, daemon=True).start()
                        self.tend = time.time()
                        self.trial_duration = self.tend - self.ttrial
                        self.gui_controls.update_trial_duration(self.trial_duration)
                        self.is_catch_trial = False
                        self.next_trial_eligible = True
                        # Save trial data
                        if not self.trial_saved: # Added 15/05/2025
                            self.save_data()
                            self.trial_saved=True
                        # Catch doesn't affect accuracy; still can check switch eligibility
                        self.maybe_switch_block()
                        return  # Exit function to prevent normal trial execution
                    
        
        # For normal trials
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
                            self.trial_history.append(1)  # Valid trial: correct
                            self.block_valid_trials += 1
                            self.gui_controls.update_correct_trials(self.correct_trials)
                                
                        else:
                            self.play_sound('white_noise')
                            print('wrong spout')
                            self.incorrect_trials +=1
                            self.trial_history.append(0)  #Valid trial: Incorrect
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
                        if not self.trial_saved: # Added 15/05/2025
                            self.save_data()
                            self.trial_saved=True
                            
                        # Evaluate block switch (needs both: min trials reached AND ≥85% on last 20 valid)
                        self.maybe_switch_block()
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
                            self.trial_history.append(1)  #Valid trial: Correct
                            self.block_valid_trials += 1
                            self.gui_controls.update_correct_trials(self.correct_trials)
                            
                        else:
                            self.play_sound('white_noise')
                            print('wrong spout')
                            self.incorrect_trials +=1
                            self.trial_history.append(0)  #Valid trial: Incorrect
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
                        if not self.trial_saved: # Added 15/05/2025
                            self.save_data()
                            self.trial_saved=True
                            
                        # Evaluate block switch (needs both: min trials reached AND ≥85% on last 20 valid)
                        self.maybe_switch_block()
                        return
                   

    def omission_callback(self):
        print('No licks detected - aborting trial')
        self.trialstarted = False
        threading.Thread(target=self.blue_led_off, daemon=True).start()
        self.tend = time.time()
        self.trial_duration = (self.tend-self.ttrial)
        self.gui_controls.update_trial_duration(self.trial_duration)
        self.omission_counted = True
        
        if not self.first_lick:
            self.omissions += 1
            self.gui_controls.update_omissions(self.omissions)
        
        self.is_catch_trial = False
        self.next_trial_eligible = True
        # Save trial data
        if not self.trial_saved: # Added this 15/05/2025
            self.save_data()
            self.trial_saved=True
            
        # Omissions don't affect accuracy, but we can still be eligible already
        self.maybe_switch_block()
        
       
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
                    self.trial_saved = False # Added this 15/05/2025
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
        """ Saves trial data, ensuring missing variables are filled with NaN while maintaining structure. """
        
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
            #np.nan if not hasattr(self, 'block_size') else self.trial_limit,  #Min number of trials per block
            np.nan if not hasattr(self, 'early_lick_counted') else (1 if self.early_lick_counted else 0),  # early licks
            np.nan if not hasattr(self, 'sound_played') else (1 if self.sound_played else 0),  # stim
            np.nan if not hasattr(self, 'current_tone') else (1 if self.current_tone == '8KHz' else 0),  # 8KHz
            np.nan if not hasattr(self, 'current_tone') else (1 if self.current_tone == '16KHz' else 0),  # 16KHz
            np.nan if not hasattr(self, 'first_lick') else (1 if self.first_lick else 0),  # lick
            np.nan if not hasattr(self, 'first_lick') else (1 if self.first_lick == 'left' else 0),  # left spout
            np.nan if not hasattr(self, 'first_lick') else (1 if self.first_lick == 'right' else 0),  # right spout
            np.nan if not hasattr(self, 'tlick') else (self.tlick if self.first_lick else np.nan),  # lick_time
            np.nan if not hasattr(self, 'first_lick') else (1 if was_rewarded else 0),  # reward
            np.nan if not hasattr(self, 'first_lick') else (1 if was_punished else 0),  # punishment
            np.nan if not hasattr(self, 'first_lick') else (1 if was_omission else 0),  # omission
            #np.nan if not hasattr(self, 'RW_start') else self.RW_start, # timestamp for response window start
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