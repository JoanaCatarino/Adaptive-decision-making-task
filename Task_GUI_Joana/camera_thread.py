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

    def __init__(self, interval_ms=30):
        super().__init__()
        self.interval = interval_ms / 1000.0
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(0)  # ✅ moved inside thread

        if not cap.isOpened():
            print("Camera not accessible inside thread")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = 3 * w
                qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.frame_ready.emit(pixmap)
            time.sleep(self.interval)

        cap.release()

    def stop(self):
        self.running = False
        self.wait()
