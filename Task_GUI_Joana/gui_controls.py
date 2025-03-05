# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 15:09:03 2024

@author: JoanaCatarino
"""
import matplotlib
matplotlib.use('Qt5Agg')

import sys
import cv2
import threading
import serial
import time

import asyncio

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow, QSizePolicy
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtCore import pyqtSlot, QTimer, QDate, Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from qasync import QEventLoop, asyncSlot  # Import qasync for async integration
from form_updt import Ui_TaskGui

# Import different functions/classes
from animal_id_generator import animal_id
from box_generator import box
from task_generator import task
from date_updater import DateUpdater
from chronometer_generator import Chronometer
from file_writer import create_data_file
from stylesheet import stylesheet
from camera import start_camera, stop_camera, update_frame
from piezo_plot import LivePlotWidget
from performance_plot import PlotLicks
from performance_plot_advanced import PlotPerformance
from piezo_reader import PiezoReader
from gpio_map import *

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
        self.current_task = None # set the initial task value

        # initialize components defined by functions:
        self.populate_ddm_animalID() # dropdown menu with animal IDs
        self.populate_ddm_box() # dropdown menu with box numbers
        self.OV_animalID() # txt with animal ID in overview tab
        self.OV_box() # txt with box number in the overview tab
        self.OV_task() # txt with task protocol name in the overview tab
        self.populate_ddm_task() # dropdown menu with different task names
        self.setup_date() # Date
        self.setup_chronometer() # Chronometer
        self.connect_buttons() # Start, Stop and Update buttons
        self.disable_controls() # Disable all the controls for the test rig 'task' - Can only be activated when task is selected
        self.connect_text_changes() # inputs received in the QLineEdits
        self.check_update_state()
        self.camera_timer = QTimer()
        self.cap = cv2.VideoCapture() # initializing cam without open
        stylesheet(self.ui)
        
        # Connect dropdown menu with animal ID in box tab to the animal ID txt in the overview tab
        self.ui.ddm_Animal_ID.currentIndexChanged.connect(self.OV_animalID)
        # Connect dropdown menu with box number to the box txt in the overview tab
        self.ui.ddm_Box.currentIndexChanged.connect(self.OV_box)
        # Connect dropdown menu with task protocol to the task txt in the overview tab
        self.ui.ddm_Task.currentIndexChanged.connect(self.OV_task)
        # Initialize button states (to enable/disable start and stop buttons)
        self.update_button_states()
        # Initialize validators for QLineEdit widgets - to only accept numbers as input
        self.setup_validators()
        # Connect the task combobox to the method for enabling/disabling QLineEdits
        self.ui.ddm_Task.currentIndexChanged.connect(self.update_qlineedit_states)
        # Connect dropdown menu changes to check start button state method (so that you need to select animal info before starting the task)
        self.ui.ddm_Animal_ID.currentIndexChanged.connect(self.check_start_button_state)
        self.ui.ddm_Task.currentIndexChanged.connect(self.check_start_button_state)
        self.ui.ddm_Box.currentIndexChanged.connect(self.check_start_button_state)
        # Initial buttom state check
        self.check_start_button_state

        # Initialize funtions related to piezo
        self.piezo_reader = PiezoReader() # Initialize piezo reader
        self.setup_piezo_plots() # Set up the piezo plot
        self.piezo_timer = QTimer()
        self.piezo_timer.timeout.connect(self.update_piezo_plots)
        self.piezo_timer.setInterval(20)  # Refresh every 20 ms
        
        # Initialize performance plot dynamically
        self.ui.ddm_Task.currentIndexChanged.connect(self.setup_plots)

        
    #Piezo functions
    def setup_piezo_plots(self):

        # Place live plots into GUI layout
        plt_layout1 = QVBoxLayout(self.ui.plt_LickTrace_Left)
        plt_layout1.setContentsMargins(0, 0, 0, 0)
        plt_layout1.setSpacing(0)
        self.live_plot1 = LivePlotWidget(self.piezo_reader.max_data_points, color= '#955C66', parent=self.ui.plt_LickTrace_Left)
        self.live_plot1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plt_layout1.addWidget(self.live_plot1)
        self.ui.plt_LickTrace_Left.setLayout(plt_layout1)

        plt_layout2 = QVBoxLayout(self.ui.plt_LickTrace_Right)
        plt_layout2.setContentsMargins(0, 0, 0, 0)
        plt_layout2.setSpacing(0)
        self.live_plot2 = LivePlotWidget(self.piezo_reader.max_data_points, color= '#4E8070', parent=self.ui.plt_LickTrace_Right)
        self.live_plot2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plt_layout2.addWidget(self.live_plot2)
        self.ui.plt_LickTrace_Right.setLayout(plt_layout2)

    def update_piezo_plots(self):
        # read serial data
        self.piezo_reader.read_serial_data()
        # Update each piezo plot with new data
        self.live_plot1.update_plot(self.piezo_reader.piezo_adder1)  # Update Left Piezo Plot
        self.live_plot2.update_plot(self.piezo_reader.piezo_adder2)  # Update Right Piezo Plot
        
    def setup_plots(self):
        
        # Map task to corresponding plot types
        plot_map = {
            'Free Licking': PlotLicks,
            'Spout Sampling': PlotLicks,
            'Two-Choice Auditory Task': PlotPerformance,
            'Adaptive Sensorimotor Task': PlotPerformance,
            'Adaptive Sensorimotor Task w/ Distractor': PlotPerformance}
        
        # Get the selected task
        selected_task = self.ui.ddm_Task.currentText()

        # Get the appropriate plot class or None if the task doesn't require a plot
        PlotClass = plot_map.get(selected_task)

        # **Clear existing layouts before adding new plots**
        #self.clear_layout(self.ui.plt_AnimalPerformance.layout())
        #self.clear_layout(self.ui.OV_plt_AnimalPerformance.layout())
        
        if PlotClass:
            # **Main tab plot**
            plt_layout1 = QVBoxLayout()
            self.current_plot = PlotClass(parent=self.ui.plt_AnimalPerformance)
            self.current_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            plt_layout1.addWidget(self.current_plot)
            self.ui.plt_AnimalPerformance.setLayout(plt_layout1)
    
            # **Overview tab plot**
            plt_layout2 = QVBoxLayout()
            self.current_plot_ov = PlotClass(parent=self.ui.OV_plt_AnimalPerformance)
            self.current_plot_ov.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            plt_layout2.addWidget(self.current_plot_ov)
            self.ui.OV_plt_AnimalPerformance.setLayout(plt_layout2)
            
            
    def clear_layout(self, layout):
        """Removes all widgets from a layout to prevent overlapping plots."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()  # Properly delete the widget to free memory
        
    
    def update_plot(self, *args):
        """Update the currently displayed plot dynamically with the correct arguments."""
        if self.current_plot and hasattr(self.current_plot, 'update_plot'):
            self.current_plot.update_plot(*args)
    
        if self.current_plot_ov and hasattr(self.current_plot_ov, 'update_plot'):
            self.current_plot_ov.update_plot(*args)
            
    def reset_plot(self):
        """Reset the currently displayed plot dynamically."""
        if self.current_plot and hasattr(self.current_plot, 'reset_plot'):
            self.current_plot.reset_plot()
    
        if self.current_plot_ov and hasattr(self.current_plot_ov, 'reset_plot'):
            self.current_plot_ov.reset_plot()
        

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

    def populate_ddm_box(self):
        # populate the dropdown menu for box
        font_size = 8
        box(self.ui.ddm_Box)

    def OV_box(self):
        selected_box = self.ui.ddm_Box.currentText()

        if selected_box.replace('.', '', 1).isdigit():
            if '.' in selected_box:
                selected_box = float(selected_box)
            else:
                selected_box = int(selected_box)

        self.ui.OV_txt_Box.setText(f'{selected_box}')

    def populate_ddm_task(self):
        font_size = 8
        task(self.ui.ddm_Task, font_size=8)
        
   
    def OV_task(self):
        selected_task = self.ui.ddm_Task.currentText()
        self.ui.OV_txt_Task.setText(f'{selected_task}')


    def setup_date(self):
        # Create and configure a DateUpdater
        self.date_updater = DateUpdater(self.ui.txt_Date, font_size=9)


    def setup_chronometer(self):
        # Initialize Chronometer
        self.txt_Chronometer = Chronometer() # Chronometer for general box tab
        self.txt_Chronometer.timeChanged.connect(self.updateTime_slot)

        self.OV_box_Chronometer = Chronometer() # Chronometer Overview tab
        self.OV_box_Chronometer.timeChanged.connect(self.updateTime_slot)


    def start_camera(self):
        start_camera(self.cap, self.camera_timer, self.update_frame)

    def stop_camera(self):
        stop_camera(self.cap, self.ui.plt_Camera, self.ui.OV_plt_Camera)

    def update_frame(self):
        update_frame(self.cap, self.ui.plt_Camera, self.ui.OV_plt_Camera)


    def check_start_button_state(self):
        # Check if all dropdown menus have a selected value
        animal_selected = self.ui.ddm_Animal_ID.currentText() != ''
        task_selected = self.ui.ddm_Task.currentText() != ''
        box_selected = self.ui.ddm_Box.currentText() != ''

        # Enable the Start button only if all dropdown menus have something selected
        self.ui.btn_Start.setEnabled(animal_selected and task_selected and box_selected)


    def connect_buttons(self):
        # Connect Start and Stop buttons + update button
        self.ui.btn_Start.clicked.connect(self.execute_task)
        self.ui.btn_Stop.clicked.connect(self.stop_task)
        #self.ui.btn_Update.clicked.connect(self.print_variables)
        self.ui.btn_Update.clicked.connect(self.update_task_params)

    def connect_text_changes(self):
        # Check for inputs received in the QLineEdits
        self.ui.txt_QuietWindow.textChanged.connect(self.check_update_state)
        self.ui.txt_ResponseWindow.textChanged.connect(self.check_update_state)
        self.ui.txt_ITImin.textChanged.connect(self.check_update_state)
        self.ui.txt_ITImax.textChanged.connect(self.check_update_state)
        self.ui.txt_ValveOpening.textChanged.connect(self.check_update_state)
        self.ui.txt_ThresholdLeft.textChanged.connect(self.check_update_state)
        self.ui.txt_ThresholdRight.textChanged.connect(self.check_update_state)

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
        self.ui.txt_ITImin.setValidator(self.float_validator)
        self.ui.txt_ITImax.setValidator(self.float_validator)
        self.ui.txt_ValveOpening.setValidator(self.float_validator)
        self.ui.txt_ThresholdLeft.setValidator(self.float_validator)
        self.ui.txt_ThresholdRight.setValidator(self.float_validator)


    def check_update_state(self):
        # Enable or disable the update button based on the QLineEdit content
        
        if (
            self.ui.txt_QuietWindow.text().strip()
            or self.ui.txt_ResponseWindow.text().strip()
            or self.ui.txt_ITImin.text().strip()
            or self.ui.txt_ITImax.text().strip()
            or self.ui.txt_ValveOpening.text().strip()
            or self.ui.txt_ThresholdLeft.text().strip()
            or self.ui.txt_ThresholdRight.text().strip()
            ):
            
            self.ui.btn_Update.setEnabled(True)
        else:
            self.ui.btn_Update.setEnabled(False)


    def update_qlineedit_states(self):
        # Enable or disable QLineEdits based on the selected task
        selected_task = self.ui.ddm_Task.currentText()
        enable = selected_task not in ('','Test rig') # Make the QLineEdits be disabled when no task is selected or when test rig is selected
        self.ui.txt_QuietWindow.setEnabled(enable)
        self.ui.txt_ResponseWindow.setEnabled(enable)
        self.ui.txt_ITImin.setEnabled(enable)
        self.ui.txt_ITImax.setEnabled(enable)
        self.ui.txt_ValveOpening.setEnabled(enable)
        self.ui.chk_AutomaticRewards.setEnabled(enable)
        self.ui.chk_NoPunishment.setEnabled(enable)
        self.ui.chk_IgnoreLicksWW.setEnabled(enable)

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
        if self.current_task and hasattr(self.current_task, 'stop'):
            self.stop_task()

        # Ensure the camera is stopped and restarted
        #self.stop_camera()
        #self.start_camera()

        # Ensure piezo are stopped and Start the piezo update timer
        self.piezo_timer.stop()
        self.piezo_timer.start()

        # Read the selected task from the dropdown menu
        selected_task = self.ui.ddm_Task.currentText()

        # Create file with data unless the selected task is 'Test rig'
        if selected_task != 'Test rig':
             csv_file_path, _ = create_data_file(self.ui.txt_Date, self.ui.ddm_Animal_ID, self.ui.ddm_Task, self.ui.ddm_Box)


        if selected_task == 'Test rig':

            # run test rig
            self.current_task = TestRig(self.ui)
            self.enable_controls()

        elif selected_task == 'Free Licking':
            self.current_task = FreeLickingTask(self, csv_file_path)

        elif selected_task == 'Spout Sampling':
            self.current_task = SpoutSamplingTask(self, csv_file_path) 

        elif selected_task == 'Two-Choice Auditory Task':
            self.current_task = TwoChoiceAuditoryTask(self, csv_file_path)

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
        #self.stop_camera()

        # Stop the piezo update timer
        if self.piezo_timer.isActive():
            self.piezo_timer.stop()

        # Disable test rig controls
        self.disable_controls()

        # Update start/stop button states
        self.update_button_states()


    def update_total_licks(self, total_licks):
        # Update the QLabel with the total trials count
        self.ui.box_TotalLicks.setText(f'{total_licks}')
        self.ui.OV_box_TotalLicks.setText(f'{total_licks}')
        
    def update_licks_left(self, licks_left):
        self.ui.box_LicksLeft.setText(f'{licks_left}')
        
    def update_licks_right(self, licks_right):
        self.ui.box_LicksRight.setText(f'{licks_right}')
        
    def update_total_trials(self, total_trials):
        self.ui.box_TotalTrials.setText(f'{total_trials}')
        self.ui.OV_box_TotalTrials.setText(f'{total_trials}') 
        
    def update_correct_trials(self, correct_trials):
        self.ui.box_CorrectTrials.setText(f'{correct_trials}')
        self.ui.OV_box_CorrectTrials.setText(f'{correct_trials}')     
        
    def update_incorrect_trials(self, incorrect_trials):
        self.ui.box_IncorrectTrials.setText(f'{incorrect_trials}')
        self.ui.OV_box_IncorrectTrials.setText(f'{incorrect_trials}')     
        
    def update_early_licks(self, early_licks):
        self.ui.box_EarlyLicks.setText(f'{early_licks}')
      
    def update_omissions(self, omissions):
        self.ui.box_Omissions.setText(f'{omissions}')
        self.ui.OV_box_Omissions.setText(f'{omissions}') 
        
    def update_trial_duration(self, trial_duration):
        self.ui.box_TrialDuration.setText(f'{trial_duration:.2f}')
        
    def update_sound_5KHz(self, sound_5KHz):
        self.ui.box_5KHzTrials.setText(f'{sound_5KHz}')
        
    def update_sound_10KHz(self, sound_10KHz):
        self.ui.box_10KHzTrials.setText(f'{sound_10KHz}')
        
    def update_autom_rewards(self, autom_rewards):
        self.ui.box_AutomRewards.setText(f'{autom_rewards}')

    
    def update_task_params(self):
        
        # Input new variables in the Gui and update them real time in the current task
        
            try:
                # Get the values from the GUI
                quiet_window = self.ui.txt_QuietWindow.text()
                response_window = self.ui.txt_ResponseWindow.text()
                ITImin = self.ui.txt_ITImin.text()
                ITImax = self.ui.txt_ITImax.text()
                valve_opening = self.ui.txt_ValveOpening.text()  # For led_on_duration/pump
                threshold_left = self.ui.txt_ThresholdLeft.text()  # For left piezo threshold
                threshold_right = self.ui.txt_ThresholdRight.text()  # For right piezo threshold
        
                # Validate and convert inputs to floats
                new_quiet_window = float(quiet_window) if quiet_window else None
                new_response_window = float(response_window) if response_window else None
                new_ITImin = float(ITImin) if ITImin else None
                new_ITImax = float(ITImax) if ITImax else None
                new_valve_opening = float(valve_opening) if valve_opening else None
                new_threshold_left = float(threshold_left) if threshold_left else None
                new_threshold_right = float(threshold_right) if threshold_right else None
        
                # Ensure there's a running task and it's of the correct type
                if self.current_task and isinstance(self.current_task, (FreeLickingTask, SpoutSamplingTask, TwoChoiceAuditoryTask, AdaptiveSensorimotorTask, AdaptiveSensorimotorTaskDistractor)):
                    # Update quiet window
                    if new_quiet_window is not None:
                        self.current_task.QW = new_quiet_window
                        print(f"Quiet window: {new_quiet_window} s")
                        self.ui.btn_Update.setEnabled(False)
                    
                    # Update response window
                    if new_response_window is not None:
                        self.current_task.RW = new_response_window
                        print(f"Response window: {new_response_window} s")
                        self.ui.btn_Update.setEnabled(False)
                        
                    # Update ITI interval - min value
                    if new_ITImin is not None:
                        self.current_task.ITI_min = new_ITImin
                        print(f"ITImin: {new_ITImin}")
                        self.ui.btn_Update.setEnabled(False)
                        
                    # Update ITI interval - min value
                    if new_ITImax is not None:
                        self.current_task.ITI_max = new_ITImax
                        print(f"ITImin: {new_ITImax}")
                        self.ui.btn_Update.setEnabled(False)
                  
                    # Update valve opening
                    if new_valve_opening is not None:
                        self.current_task.valve_opening = new_valve_opening
                        print(f"Valve opening: {new_valve_opening} s")
                        self.ui.btn_Update.setEnabled(False)
                    
                    # Update threshold_left
                    if new_threshold_left is not None: 
                        self.current_task.threshold_left = new_threshold_left
                        print(f"Threshold left piezo: {new_threshold_left}")
                        self.ui.btn_Update.setEnabled(False)
                    
                    # Update threshold_right
                    if new_threshold_right is not None:
                        self.current_task.threshold_right = new_threshold_right
                        print(f"Threshold right piezo: {new_threshold_right}")
                        self.ui.btn_Update.setEnabled(False)
                else:
                    print("No active Task or invalid task type.")
            except ValueError:
                print("Invalid input for one or more parameters. Please enter valid numbers.")
    
