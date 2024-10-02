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
        self.populate_dropdown() # dropdown menu with animal IDs