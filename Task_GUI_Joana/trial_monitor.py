# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 11:42:26 2025

@author: JoanaCatarino
"""

from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
from collections import deque

class TrialMonitor(QWidget):
    
    def __init__(self, gui_controls):
        
        # Connection to GUI
        self.gui_controls = gui_controls

        self.trial_history = deque(maxlen=15)  # Store last 15 trials

        self.grid_layout = QGridLayout(self)  # Layout for labels
        self.labels = {"block": [], "left_spout": [], "right_spout": [], "trial_number": []}

        for col in range(15):
            # Block type (Top row: "B1" to "B15")
            lbl_block = QLabel("S", self)
            lbl_block.setObjectName(f"lbl_B{col + 1}")  # Naming convention
            lbl_block.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(lbl_block, 0, col)
            self.labels["block"].append(lbl_block)

            # Left Spout (Middle row: "L1" to "L15")
            lbl_left = QLabel(" ")
            lbl_left.setObjectName(f"lbl_L{col + 1}")
            lbl_left.setAutoFillBackground(True)
            self.grid_layout.addWidget(lbl_left, 1, col)
            self.labels["left_spout"].append(lbl_left)

            # Right Spout (Middle row: "R1" to "R15")
            lbl_right = QLabel(" ")
            lbl_right.setObjectName(f"lbl_R{col + 1}")
            lbl_right.setAutoFillBackground(True)
            self.grid_layout.addWidget(lbl_right, 2, col)
            self.labels["right_spout"].append(lbl_right)

            # Trial Number (Bottom row: "T1" to "T15")
            lbl_trial = QLabel(str(col + 1), self)
            lbl_trial.setObjectName(f"lbl_T{col + 1}")
            lbl_trial.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(lbl_trial, 3, col)
            self.labels["trial_number"].append(lbl_trial)

        self.setLayout(self.grid_layout)

    def update_trial(self, trial_data):
        """ Update the QLabel widgets with new trial data """
        self.trial_history.append(trial_data)

        for col, trial in enumerate(self.trial_history):
            # Update Block Type (S, AL, AR)
            self.labels["block"][col].setText(trial["block_type"])

            # Update Spout Choices with color
            self.update_color(self.labels["left_spout"][col], trial, "L")
            self.update_color(self.labels["right_spout"][col], trial, "R")

            # Update Trial Number
            self.labels["trial_number"][col].setText(str(trial["trial_number"]))

    def update_color(self, label, trial, spout_side):
        """ Set QLabel background color based on outcome """
        color = QColor(Qt.lightGray)  # Default: omission

        if trial["spout"] == spout_side:
            if trial["outcome"] == "correct":
                color = QColor(Qt.green)
            elif trial["outcome"] == "incorrect":
                color = QColor(Qt.red)

        palette = label.palette()
        palette.setColor(QPalette.Window, color)
        label.setPalette(palette)
