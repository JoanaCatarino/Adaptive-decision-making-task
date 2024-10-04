# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 13:43:06 2024

@author: JoanaCatarino

Define stylesheets for different buttons in the Gui

"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSlot, QTimer, QDate
from form_updt import Ui_TaskGui

def stylesheet(self): 
    
    # Style sheet to set colors to start, stop and update buttons
    self.ui.btn_Start.setStyleSheet('''QPushButton{ background-color:#85b79d;
                                                    color: black;           
                                                    border: 0px solid #85b79d; 
                                                    border-radius: 0px;
                                                    padding: 1px;
                                                    font-size: 12px;
                                                    font-weight: bold}''')

    self.ui.btn_Stop.setStyleSheet('''QPushButton{  background-color:#EF8354;
                                                    color: black;           
                                                    border: 0px solid #EF8354; 
                                                    border-radius: 0px;
                                                    padding: 1px;
                                                    font-size: 12px;
                                                    font-weight: bold}''')

    self.ui.btn_Update.setStyleSheet('''QPushButton{ background-color:#BA94BD;
                                                     color: black;           
                                                     border: 0px solid #BA94BD; 
                                                     border-radius: 0px;
                                                     padding: 1px;
                                                     font-size: 12px;
                                                     font-weight: bold}''')

# Style sheet to set style for disabled buttons                              