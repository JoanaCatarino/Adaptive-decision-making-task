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
        
        while self._run_flag and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.frameCaptured.emit(frame)

        self.cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

