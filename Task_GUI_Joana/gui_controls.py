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

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow
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
from file_writer import write_task_start_file
from stylesheet import stylesheet
from camera import start_camera, stop_camera, update_frame
from piezo import LivePlotWidget
from gpio_map import *

# Import task classes
from task_test_rig import TestRig
from task_free_licking import FreeLickingTask
from task_spout_sampling import SpoutSamplingTask
from task_twochoice_auditory import TwoChoiceAuditoryTask
from task_adaptive_sensorimotor import AdaptiveSensorimotorTask
from task_adaptive_sensorimotor_distractor import AdaptiveSensorimotorTaskDistractor


class GuiControls:
    def __init__(self, ui, updateTime_slot, task_instance, test_rig):
        self.ui = ui
        self.updateTime_slot = updateTime_slot
        self.task_instance = task_instance # store reference to FreeLickingTask instance
        self.test_rig = test_rig

        style = stylesheet(self.ui) # to call the function with buttons' stylesheet
        self.current_task = None # set the initial task value

        # initialize components defined by functions:
        self.populate_ddm_animalID() # dropdown menu with animal IDs
        self.populate_ddm_box() # dropdown menu with box numbers
        self.OV_animalID() # txt with animal ID in overview tab
        self.OV_box() # txt with box number in the overview tab
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
        self.setup_serial_connection() # Set up the serial port
        self.setup_piezo_plots() # Set up the piezo plot


        # Initialize the timer to update piezo plots
        self.piezo_timer = QTimer()
        self.piezo_timer.timeout.connect(self.update_piezo_plots)
        self.piezo_timer.setInterval(20)  # Refresh every 20 ms


    # Set up the serial connection
    def setup_serial_connection(self):
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # Adjust port if necessary
        # Parameters for the data processing
        self.packet_size = 6  # Each data packet is 6 bytes
        self.max_data_points = 600 # keep the most recent 600 points
        self.piezo_adder1 = []
        self.piezo_adder2 = []
        self.buffer = bytearray()

    def read_serial_data(self):
        """Reads data from the serial port and updates the buffer."""
        try:
            # Read a chunk of data
            bytes_to_read = self.packet_size * 10
            self.buffer.extend(self.ser.read(bytes_to_read))
            #print("Reading serial...")

            # Process packets in the buffer
            while len(self.buffer) >= self.packet_size:
                # Check for start and end bytes in each packet
                if self.buffer[0] == 0x7F and self.buffer[5] == 0x80:
                    # Extract data for piezo sensors
                    self.piezo_adder1.append(self.buffer[1])
                    self.piezo_adder2.append(self.buffer[3])

                    # Trim data lists to maintain max data points
                    if len(self.piezo_adder1) > self.max_data_points:
                        self.piezo_adder1.pop(0)
                    if len(self.piezo_adder2) > self.max_data_points:
                        self.piezo_adder2.pop(0)

                    # Remove the processed packet from the buffer
                    self.buffer = self.buffer[self.packet_size:]
                else:
                    # Remove one byte if packet format is incorrect
                    self.buffer.pop(0)
        except serial.SerialException as e:
            print(f"Serial error: {e}")


    #Piezo funcitons
    def setup_piezo_plots(self):

        # Place live plots into GUI layout
        plt_layout1 = QVBoxLayout(self.ui.plt_LickTrace_Left)
        self.live_plot1 = LivePlotWidget(self.max_data_points, parent=self.ui.plt_LickTrace_Left)
        self.live_plot1.setFixedSize(450, 220)
        plt_layout1.addWidget(self.live_plot1)
        self.ui.plt_LickTrace_Left.setLayout(plt_layout1)

        plt_layout2 = QVBoxLayout(self.ui.plt_LickTrace_Right)
        self.live_plot2 = LivePlotWidget(self.max_data_points, parent=self.ui.plt_LickTrace_Right)
        self.live_plot2.setFixedSize(450, 220)
        plt_layout2.addWidget(self.live_plot2)
        self.ui.plt_LickTrace_Right.setLayout(plt_layout2)


    def update_piezo_plots(self):

        # read serial data
        self.read_serial_data()
        # Update each piezo plot with new data
        self.live_plot1.update_plot(self.piezo_adder1)  # Update Right Piezo Plot
        self.live_plot2.update_plot(self.piezo_adder2)  # Update Left Piezo Plot


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
        self.ui.btn_Update.clicked.connect(self.update_variables)

    def connect_text_changes(self):
        # Check for inputs received in the QLineEdits
        self.ui.txt_QuietWindow.textChanged.connect(self.check_update_state)
        self.ui.txt_ResponseWindow.textChanged.connect(self.check_update_state)
        self.ui.txt_TrialDuration.textChanged.connect(self.check_update_state)
        self.ui.txt_ValveOpening.textChanged.connect(self.check_update_state)

    def update_variables(self):
        # Get the value from the Gui's QLineEdit for quiet window in the free licking script
        try:
            new_qw_value = float(self.ui.txt_QuietWindow.text())
            
            if new_qw_value >= 0:
                 # Check if the task instance is a Free licking task and update it
                 if isinstance(self.task_instance, FreeLickingTask):
                    self.task_instance.update_variables(new_qw_value)
                    print(f'Updated QW to {new_qw_value}_gui print')
                 else:
                    print('invalid input')
                    
        except ValueError:
            print('invalid input: please enter valid number')


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

        # Ensure QLineWidgets remain editable when task starts
        self.ui.txt_QuietWindow.setReadOnly(False)

        # Stop any currently running task
        if self.current_task and hasattr(self.current_task, 'stop'):
            self.stop_task()

        # Ensure the camera is stopped and restarted
        self.stop_camera()
        self.start_camera()

        # Ensure piezo are stopped and Start the piezo update timer
        self.piezo_timer.stop()
        self.piezo_timer.start()

        # Read the selected task from the dropdown menu
        selected_task = self.ui.ddm_Task.currentText()

        # Create file with data unless the selected task is 'Test rig'
        if selected_task != 'Test rig':
            write_task_start_file(self.ui.txt_Date, self.ui.ddm_Animal_ID, self.ui.ddm_Task, self.ui.ddm_Box)


        if selected_task == 'Test rig':


            # run test rig
            self.current_task = TestRig(self.ui)
            self.enable_controls()

        elif selected_task == 'Free Licking':

            self.current_task = FreeLickingTask()
            self.current_task.start_fl()

        elif selected_task == 'Spout Sampling':
            self.current_task = SpoutSamplingTask()

        elif selected_task == 'Two-Choice Auditory Task':
            self.current_task = TwoChoiceAuditoryTask()

        elif selected_task == 'Adaptive Sensorimotor Task':
            self.current_task = AdaptiveSensorimotorTask()

        elif selected_task == 'Adaptive Sensorimotor Task w/ Distractor':
            self.current_task = AdaptiveSensorimotorTaskDistractor()

        if isinstance(self.current_task, threading.Thread):
            #If the current task is a thread, we don't need to call start
            pass
        elif self.current_task:
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

        # Stop the piezo update timer
        if self.piezo_timer.isActive():
            self.piezo_timer.stop()

        # Disable test rig controls
        self.disable_controls()

        # Update start/stop button states
        self.update_button_states()


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