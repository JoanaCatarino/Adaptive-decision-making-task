'''
# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer, QDate, Slot
from ui_form import Ui_TaskGui

# Import different functions
from animal_id_generator import animal_id
from sound_generator import tone_10KHz, tone_5KHz, white_noise
from chronometer_generator import Chronometer
from date_updater import DateUpdater
from file_writer import write_task_start_file

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
        
        # Create and configure a Qtimer to have the current date in the gui
        self.date_updater = DateUpdater(self.ui.Box1_Date, font_size = 10)
        
        # Call function that has the list of animals to add to the dropdown menu of Animal_ID   
        font_size = 10 # Font size of the items in the dropdown menu
        animal_id(self.ui.Box1_Animal_ID)
        
        # Initialize Chronometer
        self.Box1_Chronometer = Chronometer()
        self.Box1_Chronometer.timeChanged.connect(self.updateTime)
        
        # Connect Start button to the drop_down menu for the tasks and the Stop button to stop the task
        self.ui.Box1_Start.clicked.connect(self.execute_task)
        self.ui.Box1_Stop.clicked.connect(self.stop_task)
        
        # Placeholder for the current task
        self.current_task = None

        
    def execute_task(self):
        # Stop any currently running task
        self.stop_task()
        
        selected_task = self.ui.Box1_Task.currentText()
        
        # Create file with data unless the selected task is 'Test rig'
        if selected_task != 'Test rig':
            write_task_start_file(self.ui.Box1_Date, self.ui.Box1_Animal_ID)
        
        if selected_task == 'Test rig':
            self.current_task = TestRig(self.ui)
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
            self.Box1_Chronometer.start()
        
    def stop_task(self):
        if self.current_task and hasattr(self.current_task, 'stop'):
            self.current_task.stop()
            self.current_task = None
        
        # Stop the chronometer 
        self.ui.Box1_Stop.clicked.connect(self.Box1_Chronometer.stop)


    # Define function to have the chonometer with the hour, minute and second as the text
    @Slot(str)
    def updateTime(self, time_str):
        self.ui.Box1_Chronometer.setText(time_str)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TaskGui()
    widget.show()
    sys.exit(app.exec())
'''
# This Python file uses the following encoding: utf-8
import sys
import asyncio
import websockets
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer, QDate, Slot
from ui_form import Ui_TaskGui
from threading import Thread

# Import different functions
from animal_id_generator import animal_id
from sound_generator import tone_10KHz, tone_5KHz, white_noise
from chronometer_generator import Chronometer
from date_updater import DateUpdater
from file_writer import write_task_start_file

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
        
        # Create and configure a Qtimer to have the current date in the gui
        self.date_updater = DateUpdater(self.ui.Box1_Date, font_size = 10)
        
        # Call function that has the list of animals to add to the dropdown menu of Animal_ID   
        font_size = 10 # Font size of the items in the dropdown menu
        animal_id(self.ui.Box1_Animal_ID)
        
        # Initialize Chronometer
        self.Box1_Chronometer = Chronometer()
        self.Box1_Chronometer.timeChanged.connect(self.updateTime)
        
        # Connect Start button to the drop_down menu for the tasks and the Stop button to stop the task
        self.ui.Box1_Start.clicked.connect(self.execute_task)
        self.ui.Box1_Stop.clicked.connect(self.stop_task)
        
        # test led button
        self.ui.Box1_BlueLED.clicked.connect(lambda: self.send_command_sync('led_blue'))
        
        # Placeholder for the current task
        self.current_task = None

        
    def execute_task(self):
        # Stop any currently running task
        self.stop_task()
        
        selected_task = self.ui.Box1_Task.currentText()
        
        # Create file with data unless the selected task is 'Test rig'
        if selected_task != 'Test rig':
            write_task_start_file(self.ui.Box1_Date, self.ui.Box1_Animal_ID)
        
        if selected_task == 'Test rig':
            self.current_task = TestRig(self.ui)
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
            self.Box1_Chronometer.start()
        
    def stop_task(self):
        if self.current_task and hasattr(self.current_task, 'stop'):
            self.current_task.stop()
            self.current_task = None
        
        # Stop the chronometer 
        self.ui.Box1_Stop.clicked.connect(self.Box1_Chronometer.stop)


    # Define function to have the chonometer with the hour, minute and second as the text
    @Slot(str)
    def updateTime(self, time_str):
        self.ui.Box1_Chronometer.setText(time_str)


    def send_command_sync(self, command):
        asyncio.ensure_future(self.send_command(command))


    async def send_command(self, command):
        uri = 'ws://10.237.66.177:8765'
        async with websockets.connect(uri) as websocket:
            await websocket.send(command)
            
#def run_server():
   # import server
   # asyncio.run(server.main())    


if __name__ == "__main__":
    
   # server_thread = Thread(target=run_server, daemon=True)
   # server_thread.start()
    
    app = QApplication(sys.argv)
    widget = TaskGui()
    widget.show()
    sys.exit(app.exec())
