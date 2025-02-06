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
        #self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Total Licks")
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
        self.ax.grid(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self, time, total_licks):
        """Update stair plot with new lick data."""
        # Convert time to datetime object
        timestamp = datetime.datetime.now()

        # Append Data
        self.times.append(timestamp)
        self.lick_counts.append(total_licks)

        # Clear and Redraw Stair Plot
        self.ax.clear()
        self.ax.step(self.times, self.lick_counts, where='post', color='#FF864E', linewidth=2)

        # Update Labels & Formatting
        #self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Total Licks")
        #self.ax.set_title("Licks Over Time (Stair Plot)")
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
        self.ax.grid(True)

        # Redraw Canvas
        self.canvas.draw()
