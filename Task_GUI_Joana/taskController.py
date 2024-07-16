# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from animal_id_generator import animal_id
from ui_form import Ui_TaskGui


class TaskGui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TaskGui()
        self.ui.setupUi(self)
        
        # Call function that has the list of animals to add to the dropdown menu of Animal_ID   
        font_size = 10 # Font size of the items in the dropdown menu
        animal_id(self.ui.Box1_Animal_ID)

def test():
    print('Hi world')
 
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TaskGui()
    # Below is the custom function
    widget.ui.Box1_Start.clicked.connect(test)
    widget.show()
    sys.exit(app.exec())



