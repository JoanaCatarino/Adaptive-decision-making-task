# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 15:09:03 2024

@author: JoanaCatarino
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from form_updt import Ui_TaskGui

# Import different functions/classes
from animal_id_generator import animal_id

class GuiControls:
    
    def __init__(self, ui):
        self.ui = ui
        
        # initialize components:
        self.populate_ddm_animalID() # dropdown menu with animal IDs
        self.populate_ddm_task() # dropdown menu with different task names
        
        
    def populate_ddm_animalID(self):
        # Populate the dropdown menu for Animal_ID
        font_size = 9  # Font size of the items in the dropdown menu
        animal_id(self.ui.ddm_Animal_ID)  
        
        
    def populate_ddm_task(self):
        font_size = 9
        task(self.ui.ddm_Task)