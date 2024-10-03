# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:32:26 2024

@author: JoanaCatarino

Test rig script
- Start this task should enable the buttons that allow to test different rig components
- All the functions connected to commands related to sound (tones and white noise) should be directly imported 
from the sound_generator file. 
- Functions to test LEDs (blue and white) are generated here
- Functions to flush water are generated here with some components imported from file x
"""
class TestRig:
    def start (self):
        print ('Test Rig starting')
        def stop():
            print ('Test Rig stopping')
        self.stop = stop