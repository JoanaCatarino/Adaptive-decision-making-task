# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 15:09:03 2024

@author: JoanaCatarino
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSlot, QTimer, QDate
from form_updt import Ui_TaskGui

# Import different functions/classes
from animal_id_generator import animal_id
from task_generator import task
from date_updater import DateUpdater
from chronometer_generator import Chronometer

# Import task classes
from task_test_rig import TestRig
from task_free_licking import FreeLickingTask
from task_spout_sampling import SpoutSamplingTask
from task_twochoice_auditory import TwoChoiceAuditoryTask
from task_adaptive_sensorimotor import AdaptiveSensorimotorTask
from task_adaptive_sensorimotor_distractor import AdaptiveSensorimotorTaskDistractor


class GuiControls:
    
    def __init__(self, ui, updateTime_slot):
        self.ui = ui
        self.updateTime_slot = updateTime_slot
        
        # initialize components:
        self.populate_ddm_animalID() # dropdown menu with animal IDs
        self.OV_animalID() # txt with animal ID in overview tab
        self.populate_ddm_task() # dropdown menu with different task names
        self.setup_date() # Date
        self.setup_chronometer() # Chronometer
        self.connect_buttons() # Start and Stop buttons
        
        
        # Connect dropdown menu with animal ID in box tab to the animal ID txt in the overview tab
        self.ui.ddm_Animal_ID.currentIndexChanged.connect(self.OV_animalID)
 
        
    def populate_ddm_animalID(self):
        # Populate the dropdown menu for Animal_ID
        font_size = 8 
        animal_id(self.ui.ddm_Animal_ID)  
        
    def OV_animalID(self):
        selected_animal = self.ui.ddm_Animal_ID.currentText() # Covert string to integer
    
        # Check if the selected value is numeric (integer or float)
        if selected_animal.replace('.', '', 1).isdigit():  # Checks for integers and floats
            if '.' in selected_animal:
                selected_animal = float(selected_animal)  # Convert to float if it has a decimal point
            else:
                selected_animal = int(selected_animal)  # Convert to integer if no decimal point
                
        # Update the txt, whether it's a string or a number
        self.ui.OV_txt_AnimalID.setText(f'{selected_animal}')
        
        
    def populate_ddm_task(self):
        font_size = 8
        task(self.ui.ddm_Task, font_size=8)
        
        
    def setup_date(self):
        # Create and configure a DateUpdater
        self.date_updater = DateUpdater(self.ui.txt_Date, font_size=9)

        
    def setup_chronometer(self):
        # Initialize Chronometer
        self.txt_Chronometer = Chronometer() # Chronometer for general box tab
        self.txt_Chronometer.timeChanged.connect(self.updateTime_slot)
        
        self.OV_box_Chronometer = Chronometer() # Chronometer Overview tab
        self.OV_box_Chronometer.timeChanged.connect(self.updateTime_slot)
        

    def _connect_buttons(self):
        # Connect Start and Stop buttons + update button
        self.ui.btn_Start.clicked.connect(self.execute_task)
        self.ui.btn_Stop.clicked.connect(self.stop_task)
        #self.ui.Box1_Update.clicked.connect(self.print_variables)
   
    def execute_task(self):
        # Stop any currently running task
        self.stop_task()
        
        selected_task = self.ui.ddm_Task.currentText()
        
        # Create file with data unless the selected task is 'Test rig'
        #if selected_task != 'Test rig':
           # write_task_start_file(self.ui.Box1_Date, self.ui.Box1_Animal_ID, self.ui.Box1_Task, self.ui.Boxes)
        
        if selected_task == 'Test rig':
            self.current_task = TestRig(self.ui)
            self.enable_controls()
        elif selected_task == 'Free Licking':
            self.current_task == FreeLickingTask()
        elif selected_task == 'Spout Sampling':
            self.current_task = SpoutSamplingTask()
        elif selected_task == 'Two-Choice Auditory Task':
            self.current_task = TwoChoiceAuditoryTask()
        elif selected_task == 'Adaptive Sensorimotor Task':
            self.current_task = AdaptiveSensorimotorTask()
        elif selected_task == 'Adaptive Sensorimotor Task w/ Distractor':
            self.current_task = AdaptiveSensorimotorTaskDistractor()
            
        if self.current_task:
            self.current_task.start()
            self.txt_Chronometer.start()
            self.OV_box_Chronometer.start() # start overview chronometer for Box1
            
        else:
            self.disable_controls()
            
            
        # Update QLineEdit states based on the selected task
        #self.update_qlineedit_states()
        
        # Update start/stop button states
        #self.update_button_states()

    def stop_task(self):
        if self.current_task and hasattr(self.current_task, 'stop'):
            self.current_task.stop()
            self.current_task = None
        
        # Stop the chronometer 
        self.txt_Chronometer.stop()
        self.OV_box_Chronometer.stop() # stop overview chronometer for Box1

        # Disable test rig controls
        #self.disable_controls()
        
        # Update start/stop button states
        #self.update_button_states()