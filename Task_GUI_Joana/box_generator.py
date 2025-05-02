# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 16:21:34 2024

@author: JoanaCatarino

Populates the box drop down menu in the GUI with the identification of each box 
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox
from PyQt5.QtGui import QFont  # Import QFont for font manipulation

def box(combobox, font_size=8):
    items = [" ","1","2", "3", "4", "Ephys"]
    
    # Create a font with the specified size
    font = QFont()
    font.setPointSize(font_size)
    
    # Apply the font to the combo box
    combobox.setFont(font)
    
    for item in items:
        combobox.addItem(item)



