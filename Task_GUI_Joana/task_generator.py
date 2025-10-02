# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 16:15:34 2024

@author: JoanaCatarino

Populates the task dropdown menu in the GUI with the different tasks used in this project
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox
from PyQt5.QtGui import QFont  # Import QFont for font manipulation

def task (combobox, font_size=8):
    items = ['',
             'Test rig',
             'Free Licking',
             'Spout Sampling',
             'Two-Choice Auditory Task Blocks',
             'Two-Choice Auditory Task',
             'Adaptive Sensorimotor Task',
             'Adaptive Sensorimotor Task w/ Distractor',
             'test Two-Choice Auditory Task Blocks',
             'Passive protocol sounds',
             'Optotagging 10ms protocol',
             'Optotagging 100ms protocol'
             ]
    
    # Create a font with the specified size
    font = QFont()
    font.setPointSize(font_size)
    
    # Apply the font to the combo box
    combobox.setFont(font)
    
    for item in items:
        combobox.addItem(item)
