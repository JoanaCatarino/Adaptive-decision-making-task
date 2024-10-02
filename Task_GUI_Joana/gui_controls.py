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
        selected_animal = int(self.ui.ddm_Animal_ID.currentText()) # Covert string to integer
        self.ui.OV_txt_AnimalID.setText(f'{selected_animal}')
        
        
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
        
        self.ui.OV_box_Chronometer = Chronometer() # Chronometer Overview tab
        self.ui.OV_box_Chronometer.timeChanged.connect(self.updateTime_slot)
        

    def _connect_buttons(self):
        # Connect Start and Stop buttons + update button
        self.ui.btn_Start.clicked.connect(self.execute_task)
        self.ui.btn_Stop.clicked.connect(self.stop_task)
        #self.ui.Box1_Update.clicked.connect(self.print_variables)
   

