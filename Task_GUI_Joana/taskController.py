'''
Created on Sat Jul 20 17:32:26 2024

@author: JoanaCatarino
'''

import sys
import asyncio
import websockets
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, QDate, Slot, QUrl
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from ui_form import Ui_TaskGui
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
                        
        
        # Tests for the video part
        
        # Create a QMediaPlayer object
        self.media_player = QMediaPlayer(self)
        
        # Replace the placeholder QWidget with QVideoWidget
        self.video_widget = QVideoWidget(self)
        
        self.video_placeholder = self.findChild(QWidget, 'self.ui.Box1_Camera')
        
        # Get the layout of the placeholder widget and add QVideoWidget to it
        layout = self.video_placeholder.layout()
        layout.addWidget(self.video_widget)
        self.video_placeholder.setLayout(layout)
        
        # Set the video output to the QVideoWidget
        self.media_player.setVideoOutput(self.video_widget)
        
        def play_video(self):
            # Set the media file (URL or local file path)
            video_url = QUrl.fromLocalFile('C:/Users/JoanaCatarino/Joana/test_directory/test_video/video1.avi')
            self.media_player.setSource(video_url)
            self.media_player.play()
        

        
        # Initialize BoxControls for Box 1
        self.box1_controls = BoxControls(self.ui, self.send_command_sync, self.updateTime)
        
        # Placeholder for the current task
        self.current_task = None
        
        # create Server
        self.server = Server(self)
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.server.run(),loop)

    # Define function to have the chonometer with the hour, minute and second as the text
    @Slot(str)
    def updateTime(self, time_str):
        self.ui.Box1_Chronometer.setText(time_str)
        self.ui.OV1_Chronometer.setText(time_str)
        
    @asyncSlot()
    async def send_command_sync(self, command):
        await self.send_command(command)
        

    async def send_command(self, command):
        for ws in self.server.websocket_handle:
            await ws.send(command)
            

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
