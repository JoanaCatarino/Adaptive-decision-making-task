# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 09:47:31 2025

@author: JoanaCatarino


Passive protocol for recording of sounds

Total duration: 5.4 min

30 x 8KHz sound spaced by 5sec
interval of 10 sec between sounds
30 x 16KHz sound spaced by 5sec

"""
import threading
import time
from gpio_map import *
from gpiozero import LED
from time import sleep
from sound_generator import tone_16KHz, tone_8KHz
from form_updt import Ui_TaskGui

class PassiveSoundRecordings:
   
    def __init__(self, ui):
        self.ui = ui
        self.start()
        
        # Connection to GUI
        self.gui_controls = gui_controls
        self.piezo_reader = gui_controls.piezo_reader
        
        
    def start (self):
        print ('Passive Protocol with Sounds starting')
        
        # Turn the LEDS ON initially
        pump_l.on()
        pump_r.on()
    
        self.running = True
        
        # Start main loop in a separate thread
        self.print_thread = threading.Thread(target=self.main, daemon=True)
        self.print_thread.start()   
    
    
    def stop(self):
        print("Stopping Adaptive Sensorimotor Task...")
        
        self.running = False
            
        pump_l.on()    
         
     
    def play_sound(self, frequency):
        if frequency == "8KHz":
            tone_8KHz()   # Your function for 8KHz sound
        elif frequency == "16KHz":
            tone_16KHz()  # Your function for 16KHz sound
            
         
    def run_sequence(self):
        # Play 8KHz 30 times, 5 sec apart
        for i in range(30):
            print(f"Playing 8KHz sound {i+1}/30")
            self.play_sound("8KHz")
            time.sleep(5)  # wait 5 sec before next sound
       
        # Wait 10 sec before switching to 16KHz
        print("Waiting 10 seconds before 16KHz sequence...")
        time.sleep(10)
    
        # Play 16KHz 30 times, 5 sec apart
        for i in range(30):
            print(f"Playing 16KHz sound {i+1}/30")
            self.play_sound("16KHz")
            time.sleep(5)
            
        print("Sequence of sounds is finished!")
             
        self.stop() # Stop protocol once all the sequence of sounds was played
              
         
         
    def main(self):
    
        while self.running:
            self.run_sequence()