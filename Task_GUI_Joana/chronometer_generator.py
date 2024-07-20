# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 11:24:48 2024

@author: JoanaCatarino
"""

from PySide6.QtCore import QTimer, Signal, QObject

class Chronometer(QObject):
    timeChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.elapsed_time = 0

    def start(self):
        self.elapsed_time = 0
        self.timer.start(1000)

    def stop(self):
        self.timer.stop()

    def updateTime(self):
        self.elapsed_time += 1
        hours = self.elapsed_time // 3600
        minutes = (self.elapsed_time % 3600) // 60
        seconds = self.elapsed_time % 60
        self.timeChanged.emit(f"{hours:02} : {minutes:02} : {seconds:02}")
