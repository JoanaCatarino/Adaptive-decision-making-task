'''
Created on Sat Jul 20 17:32:26 2024

@author: JoanaCatarino
'''

import sys
import websockets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from form_updt import Ui_TaskGui

# Import different functions/classes
from gui_controls import GuiControls

class TaskGui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TaskGui()
        self.ui.setupUi(self)
        
        # Initialize BoxControls for Box 1
        self.gui_controls =GuiControls(self.ui, self.updateTime)
        
      
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TaskGui()
    widget.show()
    sys.exit(app.exec_())
