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
        self.total_licks = []
        self.licks_left = []
        self.licks_right = []

        # Set Up Plot
        #self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Total Licks")
        self.ax.grid(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self, time, total_licks, licks_left, licks_right):
        """Update stair plot with new lick data."""

        # Append Data
        self.times.append(time)
        self.total_licks.append(total_licks)
        self.licks_left.append(licks_left)
        self.licks_right.append(licks_right)

        # Clear and Redraw Stair Plot
        self.ax.clear()
        self.ax.step(self.times, self.total_licks, where='post', color='#FF864E', linewidth=2, label='Total licks')
        self.ax.step(self.times, self.licks_left, where='post', color='#955C66', linewidth=2, linestyle= 'dashed', label='Licks left')
        self.ax.step(self.times, self.licks_right, where='post', color='#4E8070', linewidth=2, linestyle= 'dashed', label='Licks right')
        
        # Update Labels & Formatting
        self.ax.set_ylabel("Licks")
        self.ax.grid(True)
        
        # Add legend and set colors
        legend = self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.18), ncol=3, frameon=False, prop={'size':8.5})
        for text, color in zip(legend.get_texts(), ['#FF864E', '#955C66', '#4E8070']):
            text.set_color(color)

        # Redraw Canvas
        self.canvas.draw()
