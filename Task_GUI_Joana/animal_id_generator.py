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
    items = ["Test-animal", "1061768", "1060358", "1060359", "1060360", "1060148", "1053835", "1053836", "1053833", "1060138", "1060141", "1061220", "1061221", "1061233", "1061234"]
    
    # Create a font with the specified size
    font = QFont()
    font.setPointSize(font_size)
    
    # Apply the font to the combo box
    combobox.setFont(font)
    
    for item in items:
        combobox.addItem(item)







