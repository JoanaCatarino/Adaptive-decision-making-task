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
    items = ["Test-animal", "1020226", "1020227", "1020228", "1031912", "1031913", "1033993", "1033996", "1033998", "1033999", "1021218", "1021219", "1038513"]
    
    # Create a font with the specified size
    font = QFont()
    font.setPointSize(font_size)
    
    # Apply the font to the combo box
    combobox.setFont(font)
    
    for item in items:
        combobox.addItem(item)







