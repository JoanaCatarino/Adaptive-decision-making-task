'''
Created on Sat Jul 20 17:32:26 2024

@author: JoanaCatarino
'''

import sys
import asyncio
import websockets
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer, QDate, Slot
from ui_form import Ui_TaskGui
from threading import Thread
from qasync import asyncSlot
from qasync import QEventLoop, QApplication
from server import Server

# Import different functions/classes
from animal_id_generator import animal_id
from sound_generator import tone_10KHz, tone_5KHz, white_noise
from chronometer_generator import Chronometer
from date_updater import DateUpdater
from file_writer import write_task_start_file
from box_controls import BoxControls

# Import task classes
from task_test_rig import TestRig
from task_free_licking import FreeLicking
from task_spout_sampling import SpoutSampling
from task_twochoice_auditory import TwoChoiceAuditoryTask
from task_adaptive_sensorimotor import AdaptiveSensorimotorTask
from task_adaptive_sensorimotor_distractor import AdaptiveSensorimotorTaskDistractor
          

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
                                                                height: 14px;}''')

        # Initialize BoxControls for each box
        self.box_controls = {
            1: BoxControls(self.ui, self.send_command_sync, 1, self.execute_task, self.stop_task, self.update_time), # Behavioral Box 1
            2: BoxControls(self.ui, self.send_command_sync, 2, self.execute_task, self.stop_task, self.update_time), # Behavioral Box 2
            3: BoxControls(self.ui, self.send_command_sync, 3, self.execute_task, self.stop_task, self.update_time), # Behavioral Box 3
            4: BoxControls(self.ui, self.send_command_sync, 4, self.execute_task, self.stop_task, self.update_time), # Behavioral Box 4
            5: BoxControls(self.ui, self.send_command_sync, 3, self.execute_task, self.stop_task, self.update_time) # Ephys rig  
        }

        # Placeholder for the current task
        self.current_task = None

        # Create Server
        self.server = Server(self)
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.server.run(), loop)

    def execute_task(self):
        # Stop any currently running task
        self.stop_task()

        # Select box (currently assuming Box1 for example purposes, replace with actual selection logic)
        selected_box = 1
        controls = self.box_controls[selected_box]
        selected_task = controls.controls["Task"].currentText()

        # Create file with data unless the selected task is 'Test rig'
        if selected_task != 'Test rig':
            write_task_start_file(controls.controls["Date"], controls.controls["AnimalID"])

        if selected_task == 'Test rig':
            self.current_task = TestRig(self.ui)
            controls.enable_controls()
        elif selected_task == 'Free Licking':
            self.current_task = FreeLicking()
        elif selected_task == 'Spout Sampling':
            self.current_task = SpoutSampling()
        elif selected_task == 'Two-Choice Auditory Task':
            self.current_task = TwoChoiceAuditoryTask()
        elif selected_task == 'Adaptive Sensorimotor Task':
            self.current_task = AdaptiveSensorimotorTask()
        elif selected_task == 'Adaptive Sensorimotor Task w/ Distractor':
            self.current_task = AdaptiveSensorimotorTaskDistractor()

        if self.current_task:
            self.current_task.start()
            controls.chronometer.start()
        else:
            controls.disable_controls()

    def stop_task(self):
        if self.current_task and hasattr(self.current_task, 'stop'):
            self.current_task.stop()
            self.current_task = None

        # Stop the chronometer for all boxes
        for controls in self.box_controls.values():
            controls.chronometer.stop()

        # Disable test rig controls for all boxes
        for controls in self.box_controls.values():
            controls.disable_controls()

    @Slot(str)
    def update_time(self, time_str):
        # Update the chronometer display for the currently active box
        selected_box = 1  # Replace with actual logic to determine the active box
        controls = self.box_controls[selected_box]
        controls.controls["ChronometerDisplay"].setText(time_str)

    @asyncSlot()
    async def send_command_sync(self, command):
        await self.send_command(command)

    async def send_command(self, command):
        for ws in self.server.websocket_handle:
            await ws.send(command)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    widget = TaskGui()
    widget.show()
    with loop:
        loop.run_forever()
        
