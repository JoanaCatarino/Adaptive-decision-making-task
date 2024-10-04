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

def stylesheet(ui): 
    
    # Stylesheet to set colors to start, stop and update buttons
    ui.btn_Start.setStyleSheet('''QPushButton{ background-color:#85b79d;
                                                    color: black;           
                                                    border: 0px solid #85b79d; 
                                                    border-radius: 0px;
                                                    padding: 1px;
                                                    font-size: 12px;
                                                    font-weight: bold}
                                  QPushButton:disabled {background-color:#C2C6C2; 
                                                        color:#757875;}''')

                               
    ui.btn_Stop.setStyleSheet('''QPushButton{  background-color:#EF8354;    
                                                    color: black;           
                                                    border: 0px solid #EF8354; 
                                                    border-radius: 0px;
                                                    padding: 1px;
                                                    font-size: 12px;
                                                    font-weight: bold}
                                  QPushButton:disabled {background-color:#C2C6C2; 
                                                        color:#757875;}''')

                              
    ui.btn_Update.setStyleSheet('''QPushButton{ background-color:#BA94BD;
                                                     color: black;           
                                                     border: 0px solid #BA94BD; 
                                                     border-radius: 0px;
                                                     padding: 1px;
                                                     font-size: 12px;
                                                     font-weight: bold}
                                  QPushButton:disabled {background-color:#C2C6C2; 
                                                        color:#757875;}''')


# Style sheet to set style for disabled buttons                              

    ui.chk_BlueLED.setStyleSheet('''QRadioButton:disabled {color: gray;} 
                                    QRadioButton::indicator:disabled {border: 1px solid gray;
                                                                background-color: transparent;
                                                                border-radius: 7px;
                                                                width: 14px;
                                                                height: 14px;}''')

    ui.chk_WhiteLED_Left.setStyleSheet('''QRadioButton:disabled {color: gray;} 
                                          QRadioButton::indicator:disabled {border: 1px solid gray;
                                                                background-color: transparent;
                                                                border-radius: 7px;
                                                                width: 14px;
                                                                height: 14px;}''')
                                    
    ui.chk_WhiteLED_Right.setStyleSheet('''QRadioButton:disabled {color: gray;} 
                                           QRadioButton::indicator:disabled {border: 1px solid gray;
                                                                background-color: transparent;
                                                                border-radius: 7px;
                                                                width: 14px;
                                                                height: 14px;}''')
                        
    ui.chk_Reward_left.setStyleSheet('''QRadioButton:disabled {color: gray;} 
                                        QRadioButton::indicator:disabled {border: 1px solid gray;
                                                                background-color: transparent;
                                                                border-radius: 7px;
                                                                width: 14px;
                                                                height: 14px;}''')
                        

                               
    ui.chk_Reward_right.setStyleSheet('''QRadioButton:disabled {color: gray;} 
                                         QRadioButton::indicator:disabled {border: 1px solid gray;
                                                                background-color: transparent;
                                                                border-radius: 7px;
                                                                width: 14px;
                                                                height: 14px;}''')

    ui.chk_Punishment.setStyleSheet('''QRadioButton:disabled {color: gray;} 
                                       QRadioButton::indicator:disabled {border: 1px solid gray;
                                                                background-color: transparent;
                                                                border-radius: 7px;
                                                                width: 14px;
                                                                height: 14px;}''')
                                    
    ui.chk_10Tone.setStyleSheet('''QRadioButton:disabled {color: gray;} 
                                   QRadioButton::indicator:disabled {border: 1px solid gray;
                                                                background-color: transparent;
                                                                border-radius: 7px;
                                                                width: 14px;
                                                                height: 14px;}''')                                    

    ui.chk_5Tone.setStyleSheet('''QRadioButton:disabled {color: gray;} 
                                  QRadioButton::indicator:disabled {border: 1px solid gray;
                                                                background-color: transparent;
                                                                border-radius: 7px;
                                                                width: 14px;
                                                                height: 14px;}''')   

                   