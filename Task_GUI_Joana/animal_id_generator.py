# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 17:44:52 2024

@author: JoanaCatarino
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox
from PyQt5.QtGui import QFont  # Import QFont for font manipulation

def animal_id(combobox, font_size=9):
    items = ["Test-animal","524345", "536455", "126846", "122364","344656"]
    
    # Create a font with the specified size
    font = QFont()
    font.setPointSize(font_size)
    
    # Apply the font to the combo box
    combobox.setFont(font)
    
    for item in items:
        combobox.addItem(item)







