#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:48:11 2024

@author: joanacatarino

File that compiles all the buttons and actions for each button of the gui.
This should be written in a generalized way so that it can be applied to the different boxes without
having to re-write the all code.

"""

 
class BoxControls:
    def __init__(self, ui, send_command_sync, box_number, execute_task_callback, stop_task_callback, update_time_callback):
        self.ui = ui
        self.send_command_sync = send_command_sync
        self.box_number = box_number
        self.execute_task_callback = execute_task_callback
        self.stop_task_callback = stop_task_callback
        self.update_time_callback = update_time_callback
        self.controls = self._initialize_controls()
        self.chronometer = None
        self._setup_controls()
        self._setup_animal_id()
        self._setup_chronometer()
        self._setup_task_buttons()

    def _initialize_controls(self):
        # Initialize control attributes dynamically based on box number
        return {
            "BlueLED": getattr(self.ui, f'Box{self.box_number}_BlueLED'),
            "WhiteLED_Left": getattr(self.ui, f'Box{self.box_number}_WhiteLED_Left'),
            "WhiteLED_Right": getattr(self.ui, f'Box{self.box_number}_WhiteLED_Right'),
            "10Tone": getattr(self.ui, f'Box{self.box_number}_10Tone'),
            "5Tone": getattr(self.ui, f'Box{self.box_number}_5Tone'),
            "Reward_left": getattr(self.ui, f'Box{self.box_number}_Reward_left'),
            "Reward_right": getattr(self.ui, f'Box{self.box_number}_Reward_right'),
            "Punishment": getattr(self.ui, f'Box{self.box_number}_Punishment'),
            "Start": getattr(self.ui, f'Box{self.box_number}_Start'),
            "Stop": getattr(self.ui, f'Box{self.box_number}_Stop'),
            "Task": getattr(self.ui, f'Box{self.box_number}_Task'),
            "AnimalID": getattr(self.ui, f'Box{self.box_number}_Animal_ID'),
            "Date": getattr(self.ui, f'Box{self.box_number}_Date'),
            "ChronometerDisplay": getattr(self.ui, f'Box{self.box_number}_Chronometer')
        }

    def _setup_controls(self):
        # Initially disable all controls
        self.disable_controls()
        
        # Connect buttons to commands
        self.controls["BlueLED"].clicked.connect(lambda: self.send_command_sync('led_blue'))
        self.controls["WhiteLED_Left"].clicked.connect(lambda: self.send_command_sync('led_white_l'))
        self.controls["WhiteLED_Right"].clicked.connect(lambda: self.send_command_sync('led_white_r'))
        self.controls["10Tone"].clicked.connect(lambda: self.send_command_sync('tone_10khz'))
        self.controls["5Tone"].clicked.connect(lambda: self.send_command_sync('tone_5khz'))
        self.controls["Punishment"].clicked.connect(lambda: self.send_command_sync('white_noise'))

    def _setup_animal_id(self):
        # Setup the Animal ID dropdown
        animal_id(self.controls["AnimalID"])

    def _setup_chronometer(self):
        # Initialize the chronometer
        self.chronometer = Chronometer()
        self.chronometer.timeChanged.connect(self.update_time_callback)

    def _setup_task_buttons(self):
        # Connect Start and Stop buttons
        self.controls["Start"].clicked.connect(self.execute_task_callback)
        self.controls["Stop"].clicked.connect(self.stop_task_callback)

    def enable_controls(self):
        for control in self.controls.values():
            control.setEnabled(True)

    def disable_controls(self):
        for control in self.controls.values():
            control.setEnabled(False)


