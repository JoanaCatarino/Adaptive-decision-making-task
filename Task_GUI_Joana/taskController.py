'''
Created on Sat Jul 20 17:32:26 2024

@author: JoanaCatarino
'''

import sys
import websockets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSlot, QTimer, QDate
from form_updt import Ui_TaskGui

# Import different functions/classes
from gui_controls import GuiControls
from stylesheet import stylesheet

class TaskGui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TaskGui()
        self.ui.setupUi(self)
        
        # Initialize Gui controls
        self.gui_controls = GuiControls(self.ui, self.updateTime)
            
        # Set the style sheet for disabled radio buttons
        self.setStyleSheet('''QRadioButton:disabled {color: gray;} 
                              QRadioButton::indicator:disabled {border: 1px solid gray;
                                                                background-color: transparent;
                                                                border-radius: 7px;
                                                                width: 14px;
                                                                height: 14px;}
                              QPushButton:disabled {color:gray;}''')
                  








    # Define function to have the chonometer with the hour, minute and second as the text
    @pyqtSlot(str)
    def updateTime(self, time_str):
        self.ui.txt_Chronometer.setText(time_str) # Chronometer in the Box page
        self.ui.OV_box_Chronometer.setText(time_str) # Chronometer in the Overview page

        # Check if the time is 1 hour (format expected: "hh:mm:ss")
        hours, minutes, seconds = map(int, time_str.split(':'))
        
        # Reset the color if the time is reset (e.g., to "00:00:00")
        if hours == 0 and minutes == 0:
            self.ui.OV_Box.setStyleSheet("background-color: white;")  # Reset to default color 
        
        if minutes == 1:
            self.ui.OV_Box.setStyleSheet("background-color: #F5E268;")  # Makes the background color of the overview box 1 yellow if the
                                                                       # animal has been performing the task for 1h                                                           
        if minutes == 2:
            self.ui.OV_Box.setStyleSheet("background-color: #BD3C49;")  # Background becomes red when animals is in the task for 2h        
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TaskGui()
    widget.show()
    sys.exit(app.exec_())
