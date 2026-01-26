# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:51:07 2024

@author: JoanaCatarino

 -- Two-Choice Auditory Task Blocks --
 
- Second training stage
- The goal of this task is to make the animals familiar to the association between spouts and tones
- Here animals need to do 10, 5 or 3 corretc licks on the spout associated to the tone to change to another tone type. 

New version - jan 2026 
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


class TwoChoiceAuditoryTask_Blocks:
    
    def __init__(self, gui_controls, csv_file_path): 
    
        # Directory to save file with trials data
        self.csv_file_path = csv_file_path
        self.save_dir = os.path.dirname(csv_file_path)
        os.makedirs(self.save_dir, exist_ok=True)
        self.file_path = csv_file_path # use the csv file name
        
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
        self.ITI_max = 6 # default ITI
        self.ITI = round(random.uniform(self.ITI_min, self.ITI_max),1) #Random ITI between 3-6 sec with ms precision
        self.RW = 3 # Response window in seconds
        self.threshold_left = 1
        self.threshold_right = 1
        self.valve_opening = 0.08  # Reward duration   
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
        self.sound_8KHz = 0
        self.sound_16KHz = 0
      
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
        self.tlick = None # time of 1st lick within response window
        self.RW_start = None
        self.early_lick_time = None # time of early lick that aborted trial
        self.stim_time = None # time sound is played
        self.reward_time = None # time reward is delivered
        self.punishment_time = None #time punishment is delivered
        self.tend = None # end of the trial
        self.trial_duration = None # trial duration
        self.next_trial_eligible = False
        self.timer_3 = None 
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        self.first_lick = None
        self.correct_spout = None
        self.trial_saved = False 
        
        # Block variables
        self.block_size = 10 # added for blocks
        self.current_block_side = None # added for blocks
        self.correct_in_block = 0 # added for blocks
        
        # Trial monitor
        self.monitor_history = deque(maxlen=15)

    def start (self):
        print ('Two-Choice Auditory task with Blocks starting')
        
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
        print("Stopping Two-Choice Auditory task with Blocks...")
        
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
        pump_r.on()
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
    
    
    
    def choose_next_trial_blockwise(self): # added for blocks
        """ 
        Selects next trial using blocks of n correct trials (n= self.block_size)

        """
        if self.current_block_side is None:
            self.current_block_side = random.choice(["left", "right"]) # Choose block side randomly for the start of the task
            self.correct_in_block = 0
            print(f"[BLOCK INIT] Starting block: {self.current_block_side}")

        
        if self.correct_in_block >= self.block_size:
            
            self.current_block_side = "right" if self.current_block_side == "left" else "left"
            self.correct_in_block = 0
            print(f"[BLOCK SWITCH] Switched to: {self.current_block_side}")
            
        print(f"[BLOCK STATUS] Trial {self.total_trials+1} - Block: {self.current_block_side} | CorrectInBlock: {self.correct_in_block}")
        
        return self.current_block_side
        
        
    
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
            
            self.trial_saved = False 
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
            
            # Select Cue according to block
            self.correct_spout = self.choose_next_trial_blockwise()   # added for blocks

            self.current_tone = "8KHz" if self.correct_spout == self.spout_8KHz else "16KHz"
            print(
                f' trial:{self.total_trials}  current_tone:{self.current_tone} - correct_spout:{self.correct_spout}')
         
            # Update gui with trial type
            self.gui_controls.ui.box_CurrentTrial.setText(f"Tone: {self.current_tone}  |  Spout: {self.correct_spout}")
            self.gui_controls.ui.OV_box_CurrentTrial.setText(f"Tone: {self.current_tone}  |  Spout: {self.correct_spout}")
            
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
                if not self.trial_saved: 
                    self.save_data()
                    self.trial_saved = True
                return  # Exit trial 
           
            # Play sound  
            self.play_sound(self.current_tone)
            self.sound_played = True
            
            # Start response window
            self.RW_start = time.time() 
             
            # Wait for response window to finish if no lick happens
            threading.Thread(target=self.wait_for_response, daemon=True).start()
            
    
    def play_sound(self, frequency):
        
        if frequency == "8KHz":
            tone_8KHz() 
            self.stim_time = time.time()
        elif frequency == "16KHz":
            tone_16KHz()
            self.stim_time = time.time()
        elif frequency == "white_noise":
            white_noise()
            self.punishment_time = time.time()
            

    def blue_led_on(self):
        led_blue.on()
        
    
    def blue_led_off(self):
        led_blue.off()
        
    
    def detect_licks_during_waiting_window(self):
        """ Detects licks during the waiting window (WW) and aborts the trial if necessary. """
        
        WW_start = time.time()  # Mark the WW start time
        self.early_lick_time = None # reset early lick time stamp
        
        ignore_licks = self.gui_controls.ui.chk_IgnoreLicksWW.isChecked() # Check if Ignore Licks during WW option is checked in the gui
        
        while time.time() - WW_start < self.WW:  # Wait for WW duration
            p1 = np.array(self.piezo_reader.piezo_adder1,dtype=np.uint16)
            p2 = np.array(self.piezo_reader.piezo_adder2,dtype=np.uint16)
            
            # Check if a lick is detected
            if not ignore_licks:
                if p1.size and p1[-1] > self.threshold_left:
                    self.early_lick_time = time.time()
                    return True  # Abort trial
        
                if p2.size and p2[-1] > self.threshold_right:
                    self.early_lick_time = time.time()
                    return True  # Abort trial
            
            time.sleep(0.001)  # Small delay to prevent CPU overload
        
        return False  # No licks detected, trial can proceed    
    
    
    def schedule_next_trial(self):
        self.next_trial_ready = True
        print("Next trial is now allowed after ITI.")
    
        self.ITI = round(random.uniform(self.ITI_min, self.ITI_max),1)
        print(self.ITI) #Troubleshoot
        
        # Start the next trial after ITI delay
        threading.Timer(self.ITI, self.check_and_start_next_trial).start()
        
    
    def check_and_start_next_trial(self):
        """ Starts the next trial if conditions allow it """
        if self.next_trial_ready and not self.trialstarted:
            if self.check_animal_quiet(): # troubleshoot
                print("Starting next trial")    
                self.start_trial()
    

    def detect_licks(self):
        """Detect any lick (amplitude-independent) during the response window and handle outcome."""
        # Read buffers (60 Hz stream)
        p1 = np.array(self.piezo_reader.piezo_adder1, dtype=np.uint16)  # left
        p2 = np.array(self.piezo_reader.piezo_adder2, dtype=np.uint16)  # right
    
        time.sleep(0.001)  # keep CPU cool
    
        # Helper: timestamp of first non-zero sample in a buffer; None if none
        def first_nonzero_time(buf):
            if buf.size == 0 or buf.max() == 0:
                return None
            first_idx = np.flatnonzero(buf > 0)[0]
            # Reconstruct wall-clock time for that sample (latest at end; 60 Hz)
            return time.time() - (1/60.0) * (len(buf) - first_idx)
    
        t_left  = first_nonzero_time(p1)
        t_right = first_nonzero_time(p2)
    
        # Need a started RW
        if self.RW_start is None:
            return
    
        in_rw_left  = (t_left  is not None) and (self.RW_start < t_left  < self.RW_start + self.RW)
        in_rw_right = (t_right is not None) and (self.RW_start < t_right < self.RW_start + self.RW)
    
        # Nothing yet or already handled first lick
        if not (in_rw_left or in_rw_right) or self.first_lick is not None:
            return
    
        # Choose earliest side if both present
        if in_rw_left and in_rw_right:
            side, tlick = (('left', t_left) if t_left <= t_right else ('right', t_right))
        elif in_rw_left:
            side, tlick = 'left', t_left
        else:
            side, tlick = 'right', t_right
    
        with self.lock:
            if self.first_lick is not None:
                return
    
            self.first_lick = side
            self.tlick = tlick
    
            # Outcome (reward vs punishment)
            if self.correct_spout == side:
                threading.Thread(target=self.reward, args=(side,)).start()
                self.correct_trials += 1
                self.correct_in_block += 1  # block progress
                self.gui_controls.update_correct_trials(self.correct_trials)
            else:
                if not self.gui_controls.ui.chk_NoPunishment.isChecked():
                    self.play_sound('white_noise')
                    print('wrong spout')
                else:
                    print('wrong spout - punishment skipped')
                self.incorrect_trials += 1
                self.gui_controls.update_incorrect_trials(self.incorrect_trials)
    
            # Counters & UI
            self.total_licks += 1
            if side == 'left':
                self.licks_left += 1
                self.gui_controls.update_licks_left(self.licks_left)
            else:
                self.licks_right += 1
                self.gui_controls.update_licks_right(self.licks_right)
            self.gui_controls.update_total_licks(self.total_licks)
    
            # Wrap up trial
            if self.timer_3 and self.timer_3.is_alive():
                self.timer_3.cancel()
            self.trialstarted = False
            threading.Thread(target=self.blue_led_off, daemon=True).start()
            self.tend = time.time()
            self.trial_duration = (self.tend - self.ttrial)
            self.gui_controls.update_trial_duration(self.trial_duration)
            self.next_trial_eligible = True
    
            # Save once
            if not self.trial_saved:
                self.save_data()
                self.trial_saved = True

                  
    def omission_callback(self):
        with self.lock:
            if not self.trialstarted or self.first_lick is not None: # Added this 15/05/2025
                return
        
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
            if not self.trial_saved: # Added this 15/05/2025
                self.save_data()
                self.trial_saved=True
      
    
    def wait_for_response(self):
        self.timer_3 = threading.Timer(self.RW, self.omission_callback)
        self.timer_3.start()
        
    
    def reward(self, side):
        """Delivers a reward without blocking the main loop."""
    
        if side == 'left':
            pump_l.off()
            time.sleep(self.valve_opening)
            pump_l.on()
            self.reward_time = time.time()
            print('Reward delivered - left')
            
        elif side == 'right':
            pump_r.off()
            time.sleep(self.valve_opening)
            pump_r.on()
            self.reward_time = time.time()
            print('Reward delivered - right')
    
    
    def main(self):
        while self.running:
            
            if self.first_trial:
                print(f"ITI duration: {self.ITI} seconds")  # Print ITI value for debugging
                if self.check_animal_quiet():
                    self.trial_saved = False 
                    self.start_trial()
                    self.first_trial = False
                    self.ITI = round(random.uniform(self.ITI_min, self.ITI_max),1)
                else:
                    pass
                
            if self.next_trial_eligible == True and ((time.time() - (self.tend)) >= self.ITI) and not self.trialstarted:
                print(f"ITI duration: {self.ITI} seconds")  # Print ITI value for debugging
                if self.check_animal_quiet():
                    self.trial_saved = False 
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
        was_rewarded = ((getattr(self, 'first_lick', None) and getattr(self, 'correct_spout', None) == getattr(self, 'first_lick', None))
    
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
            np.nan if not hasattr(self, 'RW_start') else self.RW_start, # Response window start
            np.nan if not hasattr(self, 'tend') else self.tend,  # trial end
            np.nan if not hasattr(self, 'trial_duration') else self.trial_duration,  # trial duration
            np.nan if not hasattr(self, 'ITI') else self.ITI,  # ITI
            np.nan if not hasattr(self, 'current_block') else self.current_block,  # block
            np.nan if not hasattr(self, 'early_lick_counted') else (1 if self.early_lick_counted else 0),  # early licks
            np.nan if not hasattr(self, 'early_lick_time') else self.early_lick_time,  # early licks time
            np.nan if not hasattr(self, 'sound_played') else (1 if self.sound_played else 0),  # stim
            np.nan if not hasattr(self, 'current_tone') else (1 if self.current_tone == '8KHz' else 0),  # 5KHz
            np.nan if not hasattr(self, 'current_tone') else (1 if self.current_tone == '16KHz' else 0),  # 16KHz
            np.nan if not hasattr(self, 'stim_time') else self.stim_time, # time sound was played
            np.nan if not hasattr(self, 'first_lick') else (1 if self.first_lick else 0),  # lick
            np.nan if not hasattr(self, 'first_lick') else (1 if self.first_lick == 'left' else 0),  # left spout
            np.nan if not hasattr(self, 'first_lick') else (1 if self.first_lick == 'right' else 0),  # right spout
            np.nan if not hasattr(self, 'tlick') else (self.tlick if self.first_lick else np.nan),  # lick_time
            np.nan if not hasattr(self, 'first_lick') else (1 if was_rewarded else 0),  # reward
            np.nan if not hasattr(self, 'first_lick') else (1 if was_punished else 0),  # punishment
            np.nan if not hasattr(self, 'first_lick') else (1 if was_omission else 0),  # omission
            np.nan if not hasattr(self, 'reward_time') else self.reward_time, # time reward was delivered
            np.nan if not hasattr(self, 'punishment_time') else self.punishment_time, # time punishment was delivered
            np.nan if not hasattr(self, 'RW') else self.RW,
            np.nan if not hasattr(self, 'QW') else self.QW,
            np.nan if not hasattr(self, 'WW') else self.WW,
            np.nan if not hasattr(self, 'valve_opening') else self.valve_opening,
            np.nan if not hasattr(self, 'ITI_min') else self.ITI_min,
            np.nan if not hasattr(self, 'ITI_max') else self.ITI_max,
            np.nan if not hasattr(self, 'threshold_left') else self.threshold_left,
            np.nan if not hasattr(self, 'threshold_right') else self.threshold_right,
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
        }.get(getattr(self, 'current_block', ""), "")  # If undefined, show empty string ""
    
        # **Extract Trial History Info & Update GUI**
        trial_outcome = "correct" if trial_data[17] == 1 else "incorrect" if trial_data[18] == 1 else "omission"
    
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