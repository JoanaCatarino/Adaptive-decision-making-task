# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 14:46:19 2025

@author: JoanaCatarino
"""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2

class CameraThread(QThread):
    frame_ready = pyqtSignal(QPixmap)

    def __init__(self, resolution=(320, 240), fps=15, parent=None):
        super().__init__(parent)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.running = False

    def run(self):
        self.running = True
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.frame_ready.emit(pixmap)
            self.msleep(30)  # around 30 FPS

    def stop(self):
        self.running = False
        self.wait()
        if self.cap.isOpened():
            self.cap.release()
