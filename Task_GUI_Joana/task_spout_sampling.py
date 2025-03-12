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
import random
from PyQt5.QtCore import QTimer
from piezo_reader import PiezoReader
from file_writer import create_data_file
from gpio_map import *

class SpoutSamplingTask:
    
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

        # Experiment parameters
        self.QW = 3 # Quiet window in seconds
        self.ITI_min = 2 # default ITI min
        self.ITI_max = 2 # default ITI max
        self.ITI = round(random.uniform(self.ITI_min, self.ITI_max),1) #Random ITI between 3-9 sec with ms precision
        self.RW = 2 # Response window in seconds
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
        
        # Booleans
        self.trialstarted = False
        self.running = False
        self.first_trial = True
        self.next_trial_eligible = False
        self.is_rewarded = False
        
        # Time variables
        self.tstart = None # start of the task
        self.ttrial = None # start of the trial
        self.t = None # current time
        self.tlick_l = None # last lick left spout
        self.tlick_r = None # last lick right spout
        self.tlick = None # time of 1st lick within response window
        self.tend = None # end of trial
        self.trial_duration = None # trial duration
        self.RW_start = None
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        self.first_lick = None
        
        # Alternating reward spout rule
        self.trial_counter = 0
        self.current_reward_spout = random.choice(['left', 'right']) # Chooses randomly which side starts as rewarded
        

    def start (self):
        print ('Spout Sampling task starting')
        
        # Print which side is starting
        print(f"Starting session with reward on **{self.current_reward_spout.upper()}** spout.")

        
        # Turn the LEDS ON initially
        pump_l.on()
        pump_r.on()
        
        self.gui_controls.lick_plot.reset_plot() # Plot main tab
        self.gui_controls.lick_plot_ov.reset_plot() # Plot overview tab
        
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
            self.gui_controls.update_total_trials(self.total_trials)
            self.ttrial = time.time() # Update trial start time
            self.first_lick = None # Reset first lick at the start of each trial
            self.is_rewarded = False
            
            self.gui_controls.ui.box_CurrentTrial.setText(f"Current rewarded spout: {self.current_reward_spout}")
            self.gui_controls.ui.OV_box_CurrentTrial.setText(f"Current rewarded spout: {self.current_reward_spout}")
            
            print(f'Trial: {self.total_trials}')
            
            self.RW_start = time.time()  # Start response window
            
            # Wait for response window to finish if no lick happens
            threading.Thread(target=self.wait_for_response, daemon=True).start()
        
    
    def led_indicator(self, RW):
        
        """ Turn on LED during trial duration without blocking main loop"""
        
        led_white_l.on()
        time.sleep(self.RW) # This should actually be changed to the duration of the full trial
        led_white_l.off()
        
        
    def wait_for_response(self):
        self.timer_3 = threading.Timer(self.RW, self.noresponse_callback)
        self.timer_3.start()
        
    
    def noresponse_callback(self):
        print('No licks detected - aborting trial')
        self.trialstarted = False
        self.tend = time.time()
        self.trial_duration = (self.tend-self.ttrial)
        self.gui_controls.update_trial_duration(self.trial_duration)
        self.next_trial_eligible = True
        # Update live stair plot
        self.gui_controls.update_performance_plot(self.total_trials, self.correct_trials, self.incorrect_trials)
        # Save trial data
        self.save_data()
        
        
    def detect_licks(self):
    
        """Checks for licks and delivers rewards in parallel."""

        # Ensure piezo data is updated before checking
        p1 = list(self.piezo_reader.piezo_adder1)
        p2 = list(self.piezo_reader.piezo_adder2)
    
        # Small delay to prevent CPU overload and stabilize readings
        time.sleep(0.001)
        
        # Determine the correct side for reward in this trial
        correct_spout = self.current_reward_spout
    
        # Left piezo
        if p1:
            latest_value1 = p1[-1]
    
            if latest_value1 > self.threshold_left:
                with self.lock:
                    self.tlick_l = time.time() # Update last left lick time
                    elapsed_left = self.tlick_l - self.ttrial
    
                    if self.first_lick is None and (0 < elapsed_left < self.RW):
                        self.first_lick = 'left'
                        self.tlick = self.tlick_l
    
                        if correct_spout == self.first_lick: # Only reward if correct
                            # Deliver reward in a separate thread
                            threading.Thread(target=self.reward, args=('left',)).start()
        
                            self.total_licks += 1
                            self.licks_left += 1
                            self.correct_trials +=1
                            self.gui_controls.update_total_licks(self.total_licks)
                            self.gui_controls.update_licks_left(self.licks_left)
                            self.gui_controls.update_correct_trials(self.correct_trials)
                            
                            self.is_rewarded = True
                            
                            
                        else:
                            print ('Lick left but reward is right')
                            self.incorrect_trials +=1
                            self.gui_controls.update_incorrect_trials(self.incorrect_trials)
                            
                        self.timer_3.cancel()    
                        self.trialstarted = False
                        self.tend = time.time()
                        self.trial_duration = (self.tend-self.ttrial)
                        self.gui_controls.update_trial_duration(self.trial_duration)
                        self.next_trial_eligible = True
                        
                        # Update live stair plot
                        self.gui_controls.update_lick_plot(self.tlick, self.total_licks, self.licks_left, self.licks_right)
                    
                        # Save trial data
                        self.save_data()
                        return
    
        # Right piezo        
        if p2:
            latest_value2 = p2[-1]
    
            if latest_value2 > self.threshold_right:
                with self.lock:
                    self.tlick_r = time.time()
                    elapsed_right = self.tlick_r - self.ttrial
    
                    if self.first_lick is None and (0 < elapsed_right < self.RW):
                        self.first_lick = 'right'
                        self.tlick = self.tlick_r
    
                        if correct_spout == self.first_lick:
                            # Deliver reward in a separate thread
                            threading.Thread(target=self.reward, args=('right',)).start()
                            
                            self.total_licks += 1
                            self.licks_right += 1
                            self.correct_trials +=1
                            self.gui_controls.update_total_licks(self.total_licks)
                            self.gui_controls.update_licks_right(self.licks_right)
                            self.gui_controls.update_correct_trials(self.correct_trials)
                            
                            self.is_rewarded = True
                            
                        else:
                            print('Lick right but reward is left')
                            self.incorrect_trials +=1
                            self.gui_controls.update_incorrect_trials(self.incorrect_trials)
                    
                        self.timer_3.cancel()    
                        self.trialstarted = False
                        self.tend = time.time()
                        self.trial_duration = (self.tend-self.ttrial)
                        self.gui_controls.update_trial_duration(self.trial_duration)
                        self.next_trial_eligible = True
                        
                        # Update live stair plot
                        self.gui_controls.update_lick_plot(self.tlick, self.total_licks, self.licks_left, self.licks_right)
                        
                        # Save trial data
                        self.save_data()
                        return
        
    
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
    
        # Implement trial counter
        self.trial_counter +=1

        # Switch rewarded spout after every 3 trials
        if self.trial_counter >=3:
            self.trial_counter = 0 # reset counter
            self.current_reward_spout = 'left' if self.current_reward_spout == 'right' else 'right'
            print (f'Switching reward spout to {self.current_reward_spout} for next 3 trials')
            
        
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
        """ Saves trial data, ensuring missing variables are filled with NaN while maintaining structure. """
    
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
            np.nan if not hasattr(self, 'first_lick') else (1 if is_rewarded else 0),  # reward
            np.nan if not hasattr(self, 'is_punished') else (1 if is_punished else 0),  # punishment
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
    
