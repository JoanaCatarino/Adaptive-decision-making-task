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

class GuiControls:
    
    def __init__(self, ui, updateTime_slot):
        self.ui = ui
        self.updateTime_slot = updateTime_slot
        
        # initialize components:
        self.populate_ddm_animalID() # dropdown menu with animal IDs
        self.populate_ddm_task() # dropdown menu with different task names
        self.setup_date() # Date
        
        
    def populate_ddm_animalID(self):
        # Populate the dropdown menu for Animal_ID
        font_size = 8 
        animal_id(self.ui.ddm_Animal_ID)  
        
        
    def populate_ddm_task(self):
        font_size = 8
        task(self.ui.ddm_Task, font_size=8)
        
        
    def setup_date(self):
        # Create and configure a DateUpdater
        self.date_updater = DateUpdater(self.ui.txt_Date, font_size=9)

        
    def setup_chronometer(self):
        # Initialize Chronometer
        self.ui.txt_Chronometer = Chronometer() # Chronometer for general box tab
        self.ui.txt_Chronometer.timeChanged.connect(self.updateTime_slot)
        
        self.ui.OV_txt_Chronometer = Chronometer() # Chronometer Overview tab
        self.ui.OV_txt_Chronometer.timeChanged.connect(self.updateTime_slot_ov)
        



    # Define function to have the chonometer with the hour, minute and second as the text
    @pyqtSlot(str)
    def updateTime(self, time_str):
        self.ui.txt_Chronometer.setText(time_str) # Chronometer in the Box page
        self.ui.OV1_Chronometer.setText(time_str) # Chronometer in the Overview page

        # Check if the time is 1 hour (format expected: "hh:mm:ss")
        hours, minutes, seconds = map(int, time_str.split(':'))
        if hours = 1:
            self.ui.OV_Box.setStyleSheet("background-color: yellow;")  # Makes the background color of the overview box 1 yellow if the
                                                                       # animal has been performing the task for 1h
                                                                       
        if hours = 2:
            self.ui.OV_Box.setStyleSheet("background-color: red;")  # Background becomes red when animals is in the task for 2h