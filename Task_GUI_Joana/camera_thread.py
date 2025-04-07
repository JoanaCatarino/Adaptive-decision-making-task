# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 14:46:19 2025

@author: JoanaCatarino
"""

# camera_thread.py

import sys
import cv2
import threading
import serial
import time
import random

import asyncio

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow, QSizePolicy
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtCore import pyqtSlot, QTimer, QDate, Qt, QThread
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from qasync import QEventLoop, asyncSlot  # Import qasync for async integration
from form_updt import Ui_TaskGui

class CameraThread(QThread):
    def __init__(self, cap, label, ov_label, interval_ms=30):
        super().__init__()
        self.cap = cap
        self.label = label
        self.ov_label = ov_label
        self.interval = interval_ms / 1000.0
        self.running = True

    def run(self):
        while self.running and self.cap.isOpened():
            self.update_frame()
            time.sleep(self.interval)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = 3 * w
            qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.IgnoreAspectRatio))
            self.ov_label.setPixmap(pixmap.scaled(self.ov_label.size(), Qt.IgnoreAspectRatio))

    def stop(self):
        self.running = False
        self.wait()


