# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 15:09:03 2024

@author: JoanaCatarino
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QFont
from form_updt import Ui_TaskGui

# Import different functions/classes
from animal_id_generator import animal_id
from task_generator import task
from date_updater import DateUpdater

class GuiControls:
    
    def __init__(self, ui):
        self.ui = ui
        
        # initialize components:
        self.populate_ddm_animalID() # dropdown menu with animal IDs
        self.populate_ddm_task() # dropdown menu with different task names
        self.setup_date() # Date
        
        
    def populate_ddm_animalID(self):
        # Populate the dropdown menu for Animal_ID
        font_size = 8 # Font size of the items in the dropdown menu
        animal_id(self.ui.ddm_Animal_ID)  
        
        
    def populate_ddm_task(self):
        font_size = 8
        task(self.ui.ddm_Task)
        
        
    def setup_date(self):
        # Create and configure a DateUpdater
        self.date_updater = DateUpdater(self.ui.txt_Date, font_size=8)
        