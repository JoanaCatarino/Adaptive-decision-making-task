# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 14:46:19 2025

@author: JoanaCatarino

Configuration of the camera in the GUI - only works for cameras connected to the Rbpi directly via USB (slot 0)
"""
from PyQt5.QtCore import QThread, pyqtSignal
import cv2

class CameraThread(QThread):
    frameCaptured = pyqtSignal(object)
    cameraStatus = pyqtSignal(bool)  # New signal

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self._run_flag = True

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cameraStatus.emit(self.cap.isOpened())  # Emit status once opened
        
        while self._run_flag and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.frameCaptured.emit(frame)

        self.cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

