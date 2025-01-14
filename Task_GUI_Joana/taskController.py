'''
Created on Sat Jul 20 17:32:26 2024

@author: JoanaCatarino
'''

import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSlot, QTimer, QDate
from form_updt import Ui_TaskGui

# Import different functions/classes
from gui_controls import GuiControls
from task_free_licking import FreeLickingTask
from task_test_rig import TestRig
from stylesheet import stylesheet

#test
import pyqtgraph as pg


class TaskGui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TaskGui()
        self.ui.setupUi(self)

        # Instantiate FreeLickingTask
        #self.free_licking_task = FreeLickingTask(self.ui)
        
        # Instantiate TestRigTask
        self.test_rig = TestRig(self.ui)
        
        # Initialize Gui controls
        self.gui_controls = GuiControls(self.ui, self.updateTime, self.test_rig)


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

        if hours == 1:
            self.ui.OV_Box.setStyleSheet("background-color: #F5E268;")  # Makes the background color of the overview box 1 yellow if the
                                                                       # animal has been performing the task for 1h
        if hours == 2:
            self.ui.OV_Box.setStyleSheet("background-color: #BD3C49;")  # Background becomes red when animals is in the task for 2h


if __name__ == "__main__":
    from qasync import QEventLoop, asyncSlot  # Import qasync for async integration
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    widget = TaskGui()
    widget.show()

    # Use qasync to manage the event loop
    with loop:
        loop.run_forever()

    sys.exit(app.exec_())