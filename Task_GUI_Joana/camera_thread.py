# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 14:46:19 2025

@author: JoanaCatarino
"""

# camera_thread.py

from PyQt5.QtCore import QThread
import time

class CameraThread(QThread):
    def __init__(self, cap, label, ov_label, interval_ms=30):
        super().__init__()
        self.cap = cap
        self.label = label
        self.ov_label = ov_label
        self.interval = interval_ms / 1000.0
        self.running = True

    def run(self):
        from camera_utils import update_frame
        while self.running and self.cap.isOpened():
            update_frame(self.cap, self.label, self.ov_label)
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        self.wait()


