# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 10:49:15 2025

@author: JoanaCatarino
"""
"""
-- Free Pressing task --
- The goal of this task is to make the animals familiarized with levers and the reward type they give (sucrose water)
- In this task animals should receive a reward when they press either of the levers
- Criterion: After 100 licks a Quiet window of 3000 ms is introduced - never on the first session 

Important
- when pump is set to ON it is actually OFF and when it is set to OFF it is pumping water
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

class FreePressingTask:
    
    def __init__(self, gui_controls, csv_file_path): 
        # Directory to save file with trials data
        self.csv_file_path = csv_file_path
        self.save_dir = os.path.dirname(csv_file_path)
        os.makedirs(self.save_dir, exist_ok=True)
        self.file_path = csv_file_path
        self.trials = []
        
        # Connection to GUI
        self.gui_controls = gui_controls
        self.piezo_reader = gui_controls.piezo_reader  

        # Experiment parameters
        self.QW = 0
        self.ITI_min = 0.1
        self.ITI_max = 0.1
        self.ITI = round(random.uniform(self.ITI_min, self.ITI_max), 1)
        self.RW = 3
        self.threshold_left = 1
        self.threshold_right = 1
        self.valve_opening = 0.08
        
        # Counters
        self.total_trials = 0
        self.total_licks = 0
        self.licks_left = 0
        self.licks_right = 0
        
        # Booleans
        self.trialstarted = False
        self.running = False
        self.first_trial = True
        self.next_trial_eligible = False
        self.is_rewarded = False
        
        # Time variables (use perf_counter for monotonic timing)
        self.tstart = None
        self.ttrial = None
        self.t = None
        self.tlick_l = None
        self.tlick_r = None
        self.tlick = None
        self.tend = None
        self.trial_duration = None
        self.RW_start = None
        
        # Thread safety
        self.lock = threading.Lock()
        self.first_lick = None

        # Tiny edge-latch counters to detect the first threshold crossing
        self._run_left = 0
        self._run_right = 0

        self.timer_3 = None  # set later

    def start (self):
        print ('Free Pressing task starting')
        pump_l.on()
        
        self.gui_controls.lick_plot.reset_plot()
        self.gui_controls.lick_plot_ov.reset_plot()
        
        self.running = True
        self.tstart = time.perf_counter()
        
        # Start main loop in a separate thread
        self.print_thread = threading.Thread(target=self.main, daemon=True)
        self.print_thread.start()   
        
    def stop(self):
        print("Stopping Free Pressing Task...")
        self.running = False
        try:
            if self.timer_3 is not None:
                self.timer_3.cancel()
        except Exception:
            pass
        if hasattr(self, "print_thread") and self.print_thread.is_alive():
            self.print_thread.join()
        pump_l.on() 

    def check_animal_quiet(self):
        """ Continuously checks for a quiet period before starting a trial, unless QW = 0 """
        if self.QW == 0:
            return True
        
        required_samples = self.QW * 60  # Serial runs at 60 Hz frames   
        while True:
            if not self.running:
                return False
            
            p1 = np.array(self.piezo_reader.piezo_adder1, dtype=np.int16)
            p2 = np.array(self.piezo_reader.piezo_adder2, dtype=np.int16)
        
            if len(p1) >= required_samples and len(p2) >= required_samples:
                quiet_left  = max(p1[-required_samples:]) < self.threshold_left
                quiet_right = max(p2[-required_samples:]) < self.threshold_right
                if quiet_left and quiet_right:
                    return True
                else:
                    print('Licks detected during Quiet Window')
            else:
                print('Waiting for enough data to check quiet window')
            time.sleep(0.05)
    
    def start_trial(self):
        """ Initiates a trial and logs start """
        with self.lock:
            self.trialstarted = True
            self.total_trials += 1
            self.gui_controls.update_total_trials(self.total_trials)
            self.ttrial = time.perf_counter()
            self.first_lick = None
            self.is_rewarded = False
            self._run_left = 0
            self._run_right = 0
            print(f'Trial: {self.total_trials}')
            threading.Thread(target=self.wait_for_response, daemon=True).start()
            
    def wait_for_response(self):
        self.timer_3 = threading.Timer(self.RW, self.noresponse_callback)
        self.timer_3.start()
        
    def noresponse_callback(self):
        with self.lock:
            # If a lick already claimed the trial, bail
            if not self.trialstarted or self.first_lick is not None:
                return
            print('No licks detected - aborting trial')
            self.trialstarted = False
            self.tend = time.perf_counter()
            self.trial_duration = (self.tend - self.ttrial)
            self.gui_controls.update_trial_duration(self.trial_duration)
            self.next_trial_eligible = True
            self.gui_controls.update_lick_plot(self.total_trials, self.total_licks, self.licks_left, self.licks_right)
            self.save_data() 
        
    def detect_licks(self):
        """Checks for licks and delivers rewards in parallel."""
        # The serial reader MUST be running elsewhere (thread or QTimer) to keep these fresh.
        p1 = list(self.piezo_reader.piezo_adder1)
        p2 = list(self.piezo_reader.piezo_adder2)
        time.sleep(0.001)  # tiny breather

        # Left piezo (edge latch: trigger on first sample > threshold)
        if p1:
            v1 = p1[-1]
            self._run_left = self._run_left + 1 if v1 > self.threshold_left else 0
            if self._run_left == 1:  # first crossing
                with self.lock:
                    if not self.trialstarted or self.first_lick is not None:
                        pass
                    else:
                        self.tlick_l = time.perf_counter()
                        elapsed_left = self.tlick_l - self.ttrial
                        if 0 <= elapsed_left < self.RW:
                            self.first_lick = 'left'
                            self.tlick = self.tlick_l
                            threading.Thread(target=self.reward).start()
                            self.total_licks += 1
                            self.licks_left += 1
                            self.gui_controls.update_total_licks(self.total_licks)
                            self.gui_controls.update_licks_left(self.licks_left)
                            self.is_rewarded = True
                            try:
                                if self.timer_3 is not None:
                                    self.timer_3.cancel()
                            except Exception:
                                pass
                            self.trialstarted = False
                            self.tend = time.perf_counter()
                            self.trial_duration = (self.tend - self.ttrial)
                            self.gui_controls.update_trial_duration(self.trial_duration)
                            self.next_trial_eligible = True
                            self.gui_controls.update_lick_plot(self.total_trials, self.total_licks, self.licks_left, self.licks_right)
                            self.save_data()
                            return

        # Right piezo (edge latch)
        if p2:
            v2 = p2[-1]
            self._run_right = self._run_right + 1 if v2 > self.threshold_right else 0
            if self._run_right == 1:
                with self.lock:
                    if not self.trialstarted or self.first_lick is not None:
                        pass
                    else:
                        self.tlick_r = time.perf_counter()
                        elapsed_right = self.tlick_r - self.ttrial
                        if 0 <= elapsed_right < self.RW:
                            self.first_lick = 'right'
                            self.tlick = self.tlick_r
                            threading.Thread(target=self.reward).start()
                            self.total_licks += 1
                            self.licks_right += 1
                            self.gui_controls.update_total_licks(self.total_licks)
                            self.gui_controls.update_licks_right(self.licks_right)
                            self.is_rewarded = True
                            try:
                                if self.timer_3 is not None:
                                    self.timer_3.cancel()
                            except Exception:
                                pass
                            self.trialstarted = False
                            self.tend = time.perf_counter()
                            self.trial_duration = (self.tend - self.ttrial)
                            self.gui_controls.update_trial_duration(self.trial_duration)
                            self.next_trial_eligible = True
                            self.gui_controls.update_lick_plot(self.total_trials, self.total_licks, self.licks_left, self.licks_right)
                            self.save_data()
                            return
    
    def reward(self):
        """Delivers a reward without blocking the main loop."""
        pump_l.off()
        time.sleep(self.valve_opening)
        pump_l.on()
        print('Reward delivered')
            
    def main(self):
        while self.running:
            if self.first_trial:
                print(f"ITI duration: {self.ITI} seconds")
                if self.check_animal_quiet():
                    self.start_trial()
                    self.first_trial = False
                    self.ITI = round(random.uniform(self.ITI_min, self.ITI_max), 1)
            if self.next_trial_eligible and ((time.perf_counter() - self.tend) >= self.ITI) and not self.trialstarted:
                print(f"ITI duration: {self.ITI} seconds")
                if self.check_animal_quiet():
                    self.start_trial()
                    self.next_trial_eligible = False
                    self.ITI = round(random.uniform(self.ITI_min, self.ITI_max), 1)
            self.detect_licks()
            
    

       
