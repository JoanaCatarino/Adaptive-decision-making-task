# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 15:09:03 2024

@author: JoanaCatarino
"""

import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtCore import pyqtSlot, QTimer, QDate
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from form_updt import Ui_TaskGui


# Import different functions/classes
from animal_id_generator import animal_id
from task_generator import task
from date_updater import DateUpdater
from chronometer_generator import Chronometer
from file_writer import write_task_start_file
from stylesheet import stylesheet

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
        style = stylesheet(self.ui) # to call the function with buttons' stylesheet
        self.current_task = None
        
        # initialize components defined by functions:
        self.populate_ddm_animalID() # dropdown menu with animal IDs
        self.OV_animalID() # txt with animal ID in overview tab
        self.populate_ddm_task() # dropdown menu with different task names
        self.setup_date() # Date
        self.setup_chronometer() # Chronometer
        self.connect_buttons() # Start and Stop buttons
        self.disable_controls() # Disable all the controls for the test rig 'task' - Can only be activated when task is selected
        self.connect_text_changes() # inputs received in the QLineEdits
        self.check_update_state()
        stylesheet(self.ui)
        
    
        # Connect dropdown menu with animal ID in box tab to the animal ID txt in the overview tab
        self.ui.ddm_Animal_ID.currentIndexChanged.connect(self.OV_animalID)

        # Initialize button states (to enable/disable start and stop buttons)
        self.update_button_states()
        
        # Initialize validators for QLineEdit widgets - to only accept numbers as input
        self.setup_validators()
        
        # Connect the task combobox to the method for enabling/disabling QLineEdits
        self.ui.ddm_Task.currentIndexChanged.connect(self.update_qlineedit_states)
        
        
        # Camera attributes
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_frame)
        self.cap = None # Video capture object
        
    
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
        

    def connect_buttons(self):
        # Connect Start and Stop buttons + update button
        self.ui.btn_Start.clicked.connect(self.execute_task)
        self.ui.btn_Stop.clicked.connect(self.stop_task)
        self.ui.btn_Update.clicked.connect(self.print_variables)
  
        
    def connect_text_changes(self):
        # Check for inputs received in the QLineEdits
        self.ui.txt_QuietWindow.textChanged.connect(self.check_update_state)
        self.ui.txt_ResponseWindow.textChanged.connect(self.check_update_state)
        self.ui.txt_TrialDuration.textChanged.connect(self.check_update_state)
        self.ui.txt_ValveOpening.textChanged.connect(self.check_update_state)          
    
    
    def update_button_states(self):
        # Update the enabled/disabled state of the Start and Stop buttons
        if self.current_task:
            self.ui.btn_Start.setEnabled(False) # Disable start if task is running
            self.ui.btn_Stop.setEnabled(True)   # Enable stop if a task is running
        else:
            self.ui.btn_Start.setEnabled(True)  # Enable start if no task is running
            self.ui.btn_Stop.setEnabled(False)  # Disable stop if no task is running     
            
   
    def setup_validators(self):
        # Create validators
        self.int_validator = QIntValidator()
        self.float_validator = QDoubleValidator()
        
        #Set validators to QLineEdit widgets - To only accept numbers as input
        self.ui.txt_QuietWindow.setValidator(self.float_validator)
        self.ui.txt_ResponseWindow.setValidator(self.float_validator)
        self.ui.txt_TrialDuration.setValidator(self.float_validator)
        self.ui.txt_ValveOpening.setValidator(self.float_validator)
        
    
    def check_update_state(self):
        # Enable or disable the update button based on the QLineEdit content
        quiet_window = self.ui.txt_QuietWindow.text().strip()
        response_window = self.ui.txt_ResponseWindow.text().strip()
        trial_duration = self.ui.txt_TrialDuration.text().strip()
        valve_opening = self.ui.txt_ValveOpening.text().strip()
        
        if quiet_window or response_window or trial_duration or valve_opening:
            self.ui.btn_Update.setEnabled(True)
        else:
            self.ui.btn_Update.setEnabled(False)
            
            
    def update_qlineedit_states(self):
        # Enable or disable QLineEdits based on the selected task
        selected_task = self.ui.ddm_Task.currentText()
        enable = selected_task not in ('','Test rig') # Make the QLineEdits be disabled when no task is selected or when test rig is selected
        self.ui.txt_QuietWindow.setEnabled(enable)
        self.ui.txt_ResponseWindow.setEnabled(enable)
        self.ui.txt_TrialDuration.setEnabled(enable)
        self.ui.txt_ValveOpening.setEnabled(enable)
        self.ui.chk_AssociationTrials.setEnabled(enable)
            
        
    # set enable and disable functions for the test rig controls
    def enable_controls(self):
        self.ui.chk_BlueLED.setEnabled(True)
        self.ui.chk_WhiteLED_Left.setEnabled(True)
        self.ui.chk_WhiteLED_Right.setEnabled(True)
        self.ui.chk_10Tone.setEnabled(True)
        self.ui.chk_5Tone.setEnabled(True)
        self.ui.chk_Reward_left.setEnabled(True)
        self.ui.chk_Reward_right.setEnabled(True)
        self.ui.chk_Punishment.setEnabled(True)

    def disable_controls(self):
        self.ui.chk_BlueLED.setEnabled(False)
        self.ui.chk_WhiteLED_Left.setEnabled(False)
        self.ui.chk_WhiteLED_Right.setEnabled(False)
        self.ui.chk_10Tone.setEnabled(False)
        self.ui.chk_5Tone.setEnabled(False)
        self.ui.chk_Reward_left.setEnabled(False)
        self.ui.chk_Reward_right.setEnabled(False)
        self.ui.chk_Punishment.setEnabled(False)       
        
   
    def execute_task(self):
        # Stop any currently running task
        self.stop_task()
        
        self.start_camera()
        
        
        selected_task = self.ui.ddm_Task.currentText()
        
        # Create file with data unless the selected task is 'Test rig'
        if selected_task != 'Test rig':
            write_task_start_file(self.ui.txt_Date, self.ui.ddm_Animal_ID, self.ui.ddm_Task)
        
        if selected_task == 'Test rig':
            self.current_task = TestRig(self.ui)
            self.enable_controls()
        elif selected_task == 'Free Licking':
            self.current_task = FreeLickingTask()
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
        self.update_qlineedit_states()
        
        # Update start/stop button states
        self.update_button_states()

    def stop_task(self):
       
        if self.current_task and hasattr(self.current_task, 'stop'):
            self.current_task.stop()
            self.current_task = None
        
        # Stop the chronometer 
        self.txt_Chronometer.stop()
        self.OV_box_Chronometer.stop() # stop overview chronometer for Box1

        # Stop the camera
        self.stop_camera()

        # Disable test rig controls
        self.disable_controls()
        
        # Update start/stop button states
        self.update_button_states()


    def start_camera(self):
        # Open the video capture
        self.cap = cv2.VideoCapture(0)  # 0 for the default USB camera
        if not self.cap.isOpened():
            print("Error: Camera not accessible")
            return

        # Start the timer to capture frames
        self.camera_timer.start(30)  # Capture a frame every 30ms (~33fps)

    def stop_camera(self):
        # Stop the timer and release the camera
        self.camera_timer.stop()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def update_frame(self):
        # Capture a frame from the camera
        ret, frame = self.cap.read()
        if ret:
            # Convert the frame to RGB format (as OpenCV uses BGR)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to QImage
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            qimg = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Set the image to the QLabel and scale it to fit
            pixmap = QPixmap.fromImage(qimg)
            self.ui.plt_Camera.setPixmap(pixmap.scaled(self.ui.plt_Camera.size(), aspectRatioMode=Qt.ignoreAspectRatio))  # 1 is Qt.KeepAspectRatio


    # Test to use the Update button to print the value of the variables in real-time 
    def print_variables(self):
        # Get the text from each QLineEdit widget in the gui
        quiet_window = self.ui.txt_QuietWindow.text()
        response_window = self.ui.txt_ResponseWindow.text()
        trial_duration = self.ui.txt_TrialDuration.text()
        valve_opening = self.ui.txt_ValveOpening.text()
        
        # Check if it os not empty and print it (only if it is not)
        if quiet_window:
            print(f'Quiet Window = {quiet_window}')
        if response_window:
            print(f'Response Window = {response_window}')
        if trial_duration:
            print(f'Trial Duration = {trial_duration}')
        if valve_opening:
            print(f'Valve Opening = {valve_opening}')
            
        # Disable the Update button after the operation
        self.ui.btn_Update.setEnabled(False)