# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 16:27:08 2024

@author: JoanaCatarino
"""

from PyQt5.QtCore import QTimer, QDate
from PyQt5.QtGui import QFont

class DateUpdater:
    def __init__(self, label, font_size=10):
        self.label = label
        self.set_font_size(font_size)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_date)
        self.timer.start(1000 * 60 * 60 * 24)  # Update every day
        self.update_date()  # Set the initial date

    def update_date(self):
        current_date = QDate.currentDate()
        self.label.setText(current_date.toString('yyyy-MM-dd'))

    def set_font_size(self, font_size):
        font = self.label.font()
        font.setPointSize(font_size)
        self.label.setFont(font)
