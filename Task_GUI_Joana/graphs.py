# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 18:22:28 2024

@author: JoanaCatarino
"""
'''
# Plot graphs and camera using PyQtGraph

import pyqtgraph as pg


class CameraWidget():
    
    def __init__(self, ui):
        self.ui = ui
        
'''        
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from form_updt import Ui_TaskGui

class VideoPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()

        # Create a pyqtgraph ImageView for displaying video frames
        self.video_view = pg.ImageView()
        
        # Load the video using OpenCV
        self.cap = cv2.VideoCapture(video_path)

        # Create a timer to update the frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 ms for approx 30 FPS video

    def update_frame(self):
        # Read the next frame from the video
        ret, frame = self.cap.read()
        
        if ret:
            # Convert the frame to RGB (OpenCV uses BGR by default)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Transpose frame for pyqtgraph (expected format: (rows, cols, channels))
            frame = np.transpose(frame, (1, 0, 2))

            # Update the ImageView with the new frame
            self.video_view.setImage(frame)
        else:
            self.timer.stop()  # Stop the timer if video ends


