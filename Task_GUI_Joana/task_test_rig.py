# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:32:26 2024

@author: JoanaCatarino
"""
from sound_generator import tone_10KHz, tone_5KHz, white_noise

class TestRig:
    def __init__(self, ui):
        self.ui = ui

    def start(self):
        print('Test rig starting')
        self.ui.Box1_10Tone.clicked.connect(tone_10KHz)
        self.ui.Box1_5Tone.clicked.connect(tone_5KHz)
        self.ui.Box1_Punishment.clicked.connect(white_noise)

        def stop():
            print('Test rig stopping')
            self.ui.Box1_10Tone.clicked.disconnect(tone_10KHz)
            self.ui.Box1_5Tone.clicked.disconnect(tone_5KHz)
            self.ui.Box1_Punishment.clicked.disconnect(white_noise)

        self.stop = stop
        
        
# Add tests for:
    # Blue led (trial start cue)
    # White led - left spout (distractor)
    # White led - right spout (distractor)
    # water reward - flush water when the spout is touched - when the button is clicked 
                    # this function gets activated