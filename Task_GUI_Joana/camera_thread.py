# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 14:46:19 2025

@author: JoanaCatarino
"""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2
import time

class CameraThread(QThread):
    frame_ready = pyqtSignal(QPixmap)

    def __init__(self, cap, interval_ms=30):
        super().__init__()
        self.cap = cap
        self.interval = interval_ms / 1000.0
        self.running = True

    def run(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = 3 * w
                qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.frame_ready.emit(pixmap)  # ✨ Safe signal to GUI
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        self.wait()
