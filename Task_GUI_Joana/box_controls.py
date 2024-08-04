# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 09:45:07 2024

@author: JoanaCatarino

-File with commands/buttons defined for each rig
-This is a descriptove file that is then called into the taskController.py to make the rig work throught actions made on 
the gui

"""
import sys
import asyncio
import websockets
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer, QDate, Slot
from ui_form import Ui_TaskGui
from threading import Thread
from qasync import asyncSlot
from qasync import QEventLoop, QApplication
from server import Server

# Import different functions/classes
from animal_id_generator import animal_id
from chronometer_generator import Chronometer
from date_updater import DateUpdater
from file_writer import write_task_start_file

# Import task classes
from task_test_rig import TestRig
from task_free_licking import free_licking
from task_spout_sampling import SpoutSampling
from task_twochoice_auditory import TwoChoiceAuditoryTask
from task_adaptive_sensorimotor import AdaptiveSensorimotorTask
from task_adaptive_sensorimotor_distractor import AdaptiveSensorimotorTaskDistractor


class BoxControls:
    
    def __init__(self, ui, send_command_sync, update_time_slot):
        self.ui = ui
        self.send_command_sync = send_command_sync
        self.update_time_slot = update_time_slot
        self.current_task = None
        
        # Initialize components
        self._setup_controls()
        self._setup_timer_and_chronometer()
        self._populate_animal_id_dropdown()
        self._connect_buttons()

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
        # self.ui.Box1_Reward_right.clicked.connect(lambda: self.send_command_sync('reward_right'))
        # self.ui.Box1_Reward_left.clicked.connect(lambda: self.send_command_sync('reward_left'))

    def _setup_timer_and_chronometer(self):
        # Create and configure a DateUpdater
        self.date_updater = DateUpdater(self.ui.Box1_Date, font_size=10)
        
        # Initialize Chronometer
        self.Box1_Chronometer = Chronometer()
        self.Box1_Chronometer.timeChanged.connect(self.update_time_slot)
        
        self.OV1_Chronometer = Chronometer() # Chronometer for Box1 - Overview tab
        self.OV1_Chronometer.timeChanged.connect(self.update_time_slot_ov1)

    def _populate_animal_id_dropdown(self):
        # Populate the dropdown menu for Animal_ID
        font_size = 10  # Font size of the items in the dropdown menu
        animal_id(self.ui.Box1_Animal_ID)

    def _connect_buttons(self):
        # Connect Start and Stop buttons
        self.ui.Box1_Start.clicked.connect(self.execute_task)
        self.ui.Box1_Stop.clicked.connect(self.stop_task)

    def execute_task(self):
        # Stop any currently running task
        self.stop_task()
        
        selected_task = self.ui.Box1_Task.currentText()
        
        # Create file with data unless the selected task is 'Test rig'
        if selected_task != 'Test rig':
            write_task_start_file(self.ui.Box1_Date, self.ui.Box1_Animal_ID)
        
        if selected_task == 'Test rig':
            self.current_task = TestRig(self.ui)
            self.enable_controls()
        elif selected_task == 'Free Licking':
            print ('Free Licking starting')
            self.send_command_sync('free_licking')
        elif selected_task == 'Spout Sampling':
            self.current_task = SpoutSampling()
        elif selected_task == 'Two-Choice Auditory Task':
            self.current_task = TwoChoiceAuditoryTask()
        elif selected_task == 'Adaptive Sensorimotor Task':
            self.current_task = AdaptiveSensorimotorTask()
        elif selected_task == 'Adaptive Sensorimotor Task w/ Distractor':
            self.current_task = AdaptiveSensorimotorTaskDistractor()
            
        if self.current_task:
            self.current_task.start()
            self.Box1_Chronometer.start()
            self.OV1_Chronometer.start() # start overview chronometer for Box1
            
        else:
            self.disable_controls()

    def stop_task(self):
        if self.current_task and hasattr(self.current_task, 'stop'):
            self.current_task.stop()
            self.current_task = None
        
        # Stop the chronometer 
        self.Box1_Chronometer.stop()
        self.OV1_Chronometer.stop() # stop overview chronometer for Box1

        # Disable test rig controls
        self.disable_controls()

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

# Define function to have the chonometer with the hour, minute and second as the text (for overview tab only)
    @Slot(str)
    def update_time_slot_ov1(self, time_str):
        self.ui.OV1_Chronometer.setText(time_str)

        # Check if the time is 1 hour (format expected: "hh:mm:ss")
        hours, minutes, seconds = map(int, time_str.split(':'))
        if hours >= 1:
            self.ui.OV_Box1.setStyleSheet("background-color: yellow;") # Makes the background color of the overview box 1 yellow if the
                                                                       # animal has been performing the task for 1h