import matplotlib
matplotlib.use('Qt5Agg')

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtCore import QTimer
from piezo_reader import PiezoReader  # your fixed reader above

class LiveViewer(QMainWindow):
    def __init__(self, edge_k=3, max_points=600):
        super().__init__()
        self.setWindowTitle("Piezo Live Viewer (adder frames @ 60 Hz)")

        # Reader
        self.reader = PiezoReader()  # auto-starts internal thread

        # Two plots
        central = QWidget()
        layout = QHBoxLayout(central)
        self.left_plot  = LivePlotWidget(max_data_points=max_points, edge_k=edge_k, color='tab:blue',  ylabel='Left adder')
        self.right_plot = LivePlotWidget(max_data_points=max_points, edge_k=edge_k, color='tab:orange', ylabel='Right adder')
        layout.addWidget(self.left_plot)
        layout.addWidget(self.right_plot)
        self.setCentralWidget(central)

        # Update timer ~60 Hz (16 ms)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(16)

    def refresh(self):
        # Slice the last max_points for each plot
        a1 = list(self.reader.piezo_adder1)[-self.left_plot.max_data_points:]
        a2 = list(self.reader.piezo_adder2)[-self.right_plot.max_data_points:]

        self.left_plot.update_plot(a1)
        self.right_plot.update_plot(a2)

        # Example: if you change edge_k in your task, reflect it here:
        # self.left_plot.set_edge_threshold(new_edge_k)
        # self.right_plot.set_edge_threshold(new_edge_k)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LiveViewer(edge_k=3, max_points=600)  # 10 s window (600 frames @ 60 Hz)
    win.resize(1000, 400)
    win.show()
    sys.exit(app.exec_())



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