# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 13:06:27 2025

@author: JoanaCatarino
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class LiveLickPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.times = []   # Store time points
        self.licks = []   # Store total licks
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Total Licks")
        self.ax.set_title("Total Licks Over Time")
        self.ax.grid(True)
        self.plot, = self.ax.step([], [], where='post', color='b', linewidth=2)

    def update_plot(self, time, total_licks):
        """Update the stair plot with new lick data."""
        self.times.append(time)
        self.licks.append(total_licks)

        self.plot.set_data(self.times, self.licks)
        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw()
