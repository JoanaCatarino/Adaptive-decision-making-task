# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 09:45:07 2024

@author: JoanaCatarino

-File with commands/buttons defined for each rig
-This is a descriptove file that is then called into the taskController.py to make the rig work throught actions made on 
the gui

"""
    
class BoxControls:
    
    def __init__(self, ui, send_command_sync):
        self.ui = ui
        self.send_command_sync = send_command_sync
        self._setup_controls()

    def _setup_controls(self):
        # Initially disable all buttons
        self.disable_controls()
        
        # Connect buttons to commands
        self.ui.Box1_BlueLED.clicked.connect(lambda: self.send_command_sync('led_blue'))
        self.ui.Box1_WhiteLED_Left.clicked.connect(lambda: self.send_command_sync('led_white_l'))
        self.ui.Box1_WhiteLED_Right.clicked.connect(lambda: self.send_command_sync('led_white_r'))
        self.ui.Box1_10Tone.clicked.connect(lambda: self.send_command_sync('tone_10khz'))
        self.ui.Box1_5Tone.clicked.connect(lambda: self.send_command_sync('tone_5khz'))
        self.ui.Box1_Punishment.clicked.connect(lambda: self.send_command_sync('white_noise'))
        # Uncomment if needed
        # self.ui.Box1_Reward_right.clicked.connect(lambda: self.send_command_sync('reward_right'))
        # self.ui.Box1_Reward_left.clicked.connect(lambda: self.send_command_sync('reward_left'))

    def enable_controls(self):
        self.ui.Box1_BlueLED.setEnabled(True)
        self.ui.Box1_WhiteLED_Left.setEnabled(True)
        self.ui.Box1_WhiteLED_Right.setEnabled(True)
        self.ui.Box1_10Tone.setEnabled(True)
        self.ui.Box1_5Tone.setEnabled(True)
        self.ui.Box1_Reward_left.setEnabled(True)
        self.ui.Box1_Reward_right.setEnabled(True)
        self.ui.Box1_Punishment.setEnabled(True)

    def disable_controls(self):
        self.ui.Box1_BlueLED.setEnabled(False)
        self.ui.Box1_WhiteLED_Left.setEnabled(False)
        self.ui.Box1_WhiteLED_Right.setEnabled(False)
        self.ui.Box1_10Tone.setEnabled(False)
        self.ui.Box1_5Tone.setEnabled(False)
        self.ui.Box1_Reward_left.setEnabled(False)
        self.ui.Box1_Reward_right.setEnabled(False)
        self.ui.Box1_Punishment.setEnabled(False)
