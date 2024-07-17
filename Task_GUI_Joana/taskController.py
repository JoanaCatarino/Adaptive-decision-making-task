# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer, Slot
from ui_form import Ui_TaskGui

# Import different functions
from animal_id_generator import animal_id
from sound_generator import tone_10KHz, tone_5KHz, white_noise
from chronometer_generator import Chronometer

class TaskGui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TaskGui()
        self.ui.setupUi(self)
        
        # Call function that has the list of animals to add to the dropdown menu of Animal_ID   
        font_size = 10 # Font size of the items in the dropdown menu
        animal_id(self.ui.Box1_Animal_ID)
        
        # Initialize Chronometer
        self.chronometer = Chronometer()
        self.chronometer.timeChanged.connect(self.updateTime)
        
        self.ui.Box1_Start.clicked.connect(self.chronometer.start)
        self.ui.Box1_Stop.clicked.connect(self.chronometer.stop)
        
    @Slot(str)
    def updateTime(self, time_str):
        self.ui.chronometer.setText(time_str)

#def test():
   # print('Hi world')
 
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TaskGui()
    # Below is the custom function
    #widget.ui.Box1_Start.clicked.connect(test)
    widget.ui.Box1_10Tone.clicked.connect(tone_10KHz)
    widget.ui.Box1_5Tone.clicked.connect(tone_5KHz)
    widget.ui.Box1_Punishment.clicked.connect(white_noise)
    widget.show()
    sys.exit(app.exec())



