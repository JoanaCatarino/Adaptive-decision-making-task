# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 14:46:19 2025

@author: JoanaCatarino
"""
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

def start_camera(cap, timer, update_frame_slot):
    cap.open(0)
    if not cap.isOpened():
        print("Error: Camera not accessible")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    timer.timeout.connect(update_frame_slot)
    timer.start(30)

def stop_camera(cap, label, ov_label):
    if cap.isOpened():
        cap.release()
    label.clear()
    ov_label.clear()

def update_frame(cap, label, ov_label):
    ret, frame = cap.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = 3 * w
        qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        label.setPixmap(pixmap.scaled(label.size(), Qt.IgnoreAspectRatio))
        ov_label.setPixmap(pixmap.scaled(ov_label.size(), Qt.IgnoreAspectRatio))
