import matplotlib
matplotlib.use('Qt5Agg')

import sys
import serial
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from piezo_reader import PiezoReader


class LivePlotWidget(QWidget):
    def __init__(self, max_data_points, parent=None):
        super().__init__(parent)

        self.max_data_points = max_data_points

        # Set up the plot figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Configure plot appearance
        self.ax.set_xlim(0, self.max_data_points / 60)
        self.ax.set_ylim(0, 30)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("")
        self.line, = self.ax.plot([], [], lw=2)
        #self.ax.legend()

        # Set up layout for the widget
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Remove spacing
        self.setLayout(layout)
        
        #  new!! test to see if it improves layout of the plots
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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