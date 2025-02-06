# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 13:06:27 2025

@author: JoanaCatarino
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import datetime

class PlotLicks(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create Figure and Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Initialize Data Lists
        self.times = []
        self.lick_counts = []

        # Set Up Plot
        #self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Total Licks")
        self.ax.grid(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self, time, total_licks):
        """Update stair plot with new lick data."""

        # Append Data
        self.times.append(time)
        self.lick_counts.append(total_licks)

        # Clear and Redraw Stair Plot
        self.ax.clear()
        self.ax.step(self.times, self.lick_counts, where='post', color='#FF864E', linewidth=2)

        # Update Labels & Formatting
        self.ax.set_ylabel("Total Licks")
        self.ax.grid(True)
        #self.ax.autoscale_view() # Ensure proper scaling

        # Redraw Canvas
        self.canvas.draw()
