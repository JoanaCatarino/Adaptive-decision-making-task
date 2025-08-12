import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class LivePlotWidget(QWidget):
    def __init__(self, max_data_points, edge_k=3, color='blue', parent=None, ylabel=''):
        super().__init__(parent)

        self.max_data_points = max_data_points   # number of frames to keep
        self.edge_k = edge_k                     # adder frame threshold (0..19)

        # Figure & canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Axes setup
        self.ax.set_xlim(0, self.max_data_points / 60.0)  # seconds (60 Hz frames)
        self.ax.set_ylim(0, 19)                            # adder is 0..19
        self.ax.set_xlabel("Time (s)", labelpad=10)
        self.ax.set_ylabel(ylabel, labelpad=10)

        # Main line
        (self.line,) = self.ax.plot([], [], lw=2, color=color)

        # Threshold line (dashed)
        self.th_line = self.ax.axhline(self.edge_k, linestyle='--', linewidth=1)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.figure.tight_layout(pad=2.0)

        # Data buffers used for plotting
        self.x_data = []
        self.y_data = []

    def set_edge_threshold(self, edge_k: int):
        """Update the visual threshold line and cached value."""
        self.edge_k = int(edge_k)
        self.th_line.set_ydata([self.edge_k, self.edge_k])
        self.canvas.draw_idle()

    def update_plot(self, y_data):
        """
        y_data: sequence/array of adder counts (0..19) for the last N frames.
        """
        if not y_data:
            return

        n = len(y_data)
        # X in seconds; last n frames over 60 Hz
        self.x_data = [i / 60.0 for i in range(n)]
        self.y_data = y_data

        self.line.set_data(self.x_data, self.y_data)

        # Keep fixed limits to avoid bouncing; only autoscale X if buffer grew
        # (xmax is fixed by max_data_points; no need for relim each frame)
        self.canvas.draw_idle()

    def get_last_active_time(self, threshold=None):
        """
        Returns the last time (seconds) the piezo was 'active', i.e., last frame with adder >= threshold.
        If threshold is None, uses self.edge_k.
        """
        thr = self.edge_k if threshold is None else threshold
        last_active_time = None
        for i in range(len(self.y_data) - 1, -1, -1):
            if self.y_data[i] >= thr:
                last_active_time = self.x_data[i]
                break
        return last_active_time



'''
import matplotlib
matplotlib.use('Qt5Agg')

import sys
import serial
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from piezo_reader import PiezoReader
from time import sleep


class LivePlotWidget(QWidget):
    def __init__(self, max_data_points, color='blue', parent=None):
        super().__init__(parent)

        self.max_data_points = max_data_points

        # Set up the plot figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        

        # Configure plot appearance
        self.ax.set_xlim(0, self.max_data_points / 60)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Time (s)", labelpad=10)
        self.ax.set_ylabel("", labelpad=10)
        self.line, = self.ax.plot([], [], lw=2, color=color) # set line color for the plots

        # Set up layout for the widget
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Remove spacing
        self.setLayout(layout)
        
        #  new!! test to see if it improves layout of the plots
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Apply tight layout to ensure everything fits 
        self.figure.tight_layout(pad=2.0)  # Adjust the padding as needed 

        # Initialize data lists for x-axis and y-axis
        self.x_data = []
        self.y_data = []

    def update_plot(self, y_data):
        # Update x and y data for plotting
        self.x_data = [i / 60 for i in range(len(y_data))]
        self.y_data = y_data

        # Update the line data
        self.line.set_data(self.x_data, self.y_data)

        # Redraw the canvas
        self.ax.relim()
        self.ax.autoscale_view()  # Update scale if necessary
        self.canvas.draw()
        

    def get_last_active_time(self, threshold=1):
        """
        Returns the last time (x value) the piezo sensor was active,
        defined as the last occurrence where y data > threshold.
        """
        last_active_time = None
        # Find last active time
        for i in reversed(range(len(self.y_data))):
            if self.y_data[i] > threshold:
                last_active_time = self.x_data[i]
                break
        return last_active_time