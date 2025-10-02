# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 14:18:42 2025

@author: JoanaCatarino

Protocol for optotagging units after task
"""

import threading
import time
import os
os.environ.setdefault("GPIOZERO_PIN_FACTORY", "lgpio")  # Pi 5 friendly backend


from gpio_map import *
from time import sleep
from form_updt import Ui_TaskGui

class OptoProtocol10ms:
   
    def __init__(self, ui, gui_controls=None):
        
        self.ui = ui
        self.gui_controls = gui_controls
        # Example of how you'd mirror your connections:
        # self.piezo_reader = gui_controls.piezo_reader if gui_controls else None

        self.running = False
        self.print_thread = None
        self.start()
    
    def start(self):
        print('Optotagging protocol 10ms starting')

        # Turn the PUMPs ON initially (kept exactly like your example)
        pump_l.on()
        pump_r.on()

        # Ensure laser is LOW to start
        laser.off()

        self.running = True
        # Start main loop in a separate thread
        self.print_thread = threading.Thread(target=self.main, daemon=True)
        self.print_thread.start()

    def stop(self):
        print("Stopping Passive Optotagging Protocol 10ms...")
        self.running = False
        # Follow your pattern: pumps ON in stop as well
        pump_l.on()
        pump_r.on()
        laser.off()

    def _pulse_train(self, device, width_s: float, n: int, period_s: float = 1.0, label: str = ""):
        """
        Manually generate n pulses at 1/period_s Hz.
        Stops cleanly between pulses if self.running goes False.
        """
        if not (0.0 <= width_s <= period_s) or period_s <= 0:
            raise ValueError("Invalid timing: ensure 0 <= width_s <= period_s and period_s > 0.")

        off_s = period_s - width_s
        
        for i in range(n):
            if not self.running:
                break

            if label:
                print(f"{label}: pulse {i+1}/{n}")

            # HIGH phase
            device.on()
            time.sleep(width_s)

            # LOW phase
            device.off()

            if not self.running:
                break

            time.sleep(off_s)

        # Leave LOW after block
        device.off()

    def run_sequence_10ms(self):
        # 100 pulses, 10 ms ON @ 1 Hz
        self._pulse_train(laser, width_s=0.010, n=100, period_s=1.0, label="10 ms block")

        if not self.running:
            return
        
        print("Sequence of laser pulses is finished!")
       
        # Stop protocol once all pulses were played (mirrors your example)
        self.stop()

    def main(self):
        while self.running:
            self.run_sequence_10ms()
            
            