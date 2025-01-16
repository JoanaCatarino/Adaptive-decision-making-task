# This Python file uses the following encoding: utf-8

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui_form import Ui_TaskGui


class TaskGui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TaskGui()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)   
    widget = TaskGui()
    widget.show()    
    sys.exit(app.exec())