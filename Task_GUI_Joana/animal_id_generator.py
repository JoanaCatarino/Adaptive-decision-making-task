# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 17:44:52 2024

@author: JoanaCatarino

Populates the animal_id drop down menu in the GUI with the animals added here in items
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox
from PyQt5.QtGui import QFont  # Import QFont for font manipulation

def animal_id(combobox, font_size=8):
    items = ["Test-animal","950764", "950765", "950766", "950767", "956628", "956627", "942914", "956699", "956700"]
    
    # Create a font with the specified size
    font = QFont()
    font.setPointSize(font_size)
    
    # Apply the font to the combo box
    combobox.setFont(font)
    
    for item in items:
        combobox.addItem(item)







