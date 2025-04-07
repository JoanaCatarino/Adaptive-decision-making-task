# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 14:46:19 2025

@author: JoanaCatarino
"""
from PyQt5.QtCore import QThread, pyqtSignal
import cv2

class CameraThread(QThread):
    frameCaptured = pyqtSignal(object)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self._run_flag = True

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # Set resolution (optional but can help achieve 30 FPS)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.cap.set(cv2.CAP_PROP_FPS, 30) #set camera to 30 frames per second
        
        while self._run_flag and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.frameCaptured.emit(frame)

        self.cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

