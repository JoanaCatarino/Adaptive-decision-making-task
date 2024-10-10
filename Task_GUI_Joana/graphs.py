# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 18:22:28 2024

@author: JoanaCatarino
"""
  
import sys
import cv2
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets

class CameraApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Webcam Stream")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create a layout
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Create an ImageView for displaying frames
        self.image_view = pg.ImageView()
        self.layout.addWidget(self.image_view)

        # Create a button to start/stop the webcam feed
        self.button = QtWidgets.QPushButton("Start Webcam")
        self.button.clicked.connect(self.toggle_camera)
        self.layout.addWidget(self.button)

        # Initialize webcam
        self.cap = None
        self.timer = None
        self.is_camera_active = False

    def toggle_camera(self):
        if not self.is_camera_active:
            self.start_camera()
            self.button.setText("Stop Webcam")
        else:
            self.stop_camera()
            self.button.setText("Start Webcam")

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Unable to access the webcam.")
            return

        # Start the timer to update the image view
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 milliseconds
        self.is_camera_active = True

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to grab frame from webcam.")
            return

        # Convert the frame to RGB format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Transpose the image to match the ImageView format
        self.image_view.setImage(np.transpose(frame, (1, 0, 2)))

    def stop_camera(self):
        if self.timer is not None:
            self.timer.stop()
        if self.cap is not None:
            self.cap.release()
        self.is_camera_active = False

    def closeEvent(self, event):
        self.stop_camera()  # Ensure the camera is released on close
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())


