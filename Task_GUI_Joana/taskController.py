'''
Created on Sat Jul 20 17:32:26 2024

@author: JoanaCatarino
'''

import sys
import asyncio
import websockets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
#from PySide6.QtCore import QTimer, QDate, Slot, QUrl
from form_updt import Ui_TaskGui
from threading import Thread
from qasync import asyncSlot
from qasync import QEventLoop, QApplication
from server import Server

# Import different functions/classes
from box_controls import BoxControls

class TaskGui(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_TaskGui()
        self.ui.setupUi(self)
        
        # Set the style sheet for disabled radio buttons
        self.setStyleSheet('''QRadioButton:disabled {color: gray;} 
                              QRadioButton::indicator:disabled {border: 1px solid gray;
                                                                background-color: transparent;
                                                                border-radius: 7px;
                                                                width: 14px;
                                                                height: 14px;}
                              QPushButton:disabled {color:gray;}''')
                        
        
        # Initialize BoxControls for Box 1
        self.box1_controls = BoxControls(self.ui, self.send_command_sync, self.updateTime)
        
        # Placeholder for the current task
        self.current_task = None
        
        # create Server
        self.server = Server(self)
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.server.run(),loop)

    # Define function to have the chonometer with the hour, minute and second as the text
    #@Slot(str)
   # def updateTime(self, time_str):
        #self.ui.Box1_Chronometer.setText(time_str)
        #self.ui.OV1_Chronometer.setText(time_str)
        
   # @asyncSlot()
   # async def send_command_sync(self, command):
       # await self.send_command(command)
        

    #async def send_command(self, command):
       # for ws in self.server.websocket_handle:
           # await ws.send(command)
            

if __name__ == "__main__":
    
   # server_thread = Thread(target=run_server, daemon=True)
   # server_thread.start()
    
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    widget = TaskGui()
    widget.show()
    with loop:
        loop.run_forever()
