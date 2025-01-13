# This Python file uses the following encoding: utf-8

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui_form import Ui_TaskGui

import asyncio #added
from qasync import QEventLoop # added



class TaskGui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TaskGui()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Use qasync's QEventLoop to integrate asyncio
    loop = QEventLoop(app) #added
    asyncio.set_event_loop(loop) #added
    
    widget = TaskGui()
    widget.show()
    
    # Run both the PyQt and asyncio event loops
    with loop:
        loop.run_forever() #added
    
    #sys.exit(app.exec())