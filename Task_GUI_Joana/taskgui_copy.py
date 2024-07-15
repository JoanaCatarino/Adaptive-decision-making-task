# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_TaskGui

class TaskGui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TaskGui()
        self.ui.setupUi(self)

def test():
    print('Hi world')
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TaskGui()
    # Below is the custom function
    widget.ui.Box1_Start.clicked.connect(test)
    widget.show()
    sys.exit(app.exec())
