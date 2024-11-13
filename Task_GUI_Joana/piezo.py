import matplotlib
matplotlib.use('Qt5Agg')

import sys
import serial
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Set up the serial connection
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # Adjust port if necessary

# Variables to hold data and buffer
piezo_adder1 = []
piezo_bool1 = []
piezo_adder2 = []
piezo_bool2 = []
buffer = bytearray()

# Parameters for the plot
packet_size = 6 #each data packet is 4 bytes
max_data_points = 600

class LivePlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a figure and axis for the plot
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Create the plot line objects for piezo_adder and piezo_adder2
        self.line1, = self.ax.plot([], [], lw=2, label="Piezo Adder 1")
        self.line2, = self.ax.plot([], [], lw=2, label="Piezo Adder 2", color="orange")

        # Configure the plot appearance
        self.ax.set_xlim(0, max_data_points / 60)
        self.ax.set_ylim(0, 50)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Piezo Adder")
        self.ax.legend()

        # Set up layout for the widget
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Initialize data lists for x-axis and y-axes
        self.x_data = []
        self.y_data1 = []
        self.y_data2 = []

    def update_plot(self):
        global buffer

             # Read a chunk of data
        bytes_to_read = packet_size * 10
        buffer.extend(ser.read(bytes_to_read))

        # Process packets in the buffer
        while len(buffer) >= packet_size: ## Check that I have enough bytes to decode
            if buffer[0] == 0x7F and buffer[5] == 0x80:
                #print(release_count, buffer[:4], ser.in_waiting)
                piezo_adder1.append(buffer[1])
                piezo_bool1.append(buffer[2])
                piezo_adder2.append(buffer[3])
                piezo_bool2.append(buffer[4])

                # Keep only the last max_data_points in the list
                if len(piezo_adder1) > max_data_points:
                    piezo_adder1.pop(0)
                if len(piezo_adder2) > max_data_points:
                    piezo_adder2.pop(0)
                buffer = buffer[packet_size:]
            else:
                buffer.pop(0)


        # Update x and y data for plotting
        self.x_data = [i / 60 for i in range(len(piezo_adder1))]
        self.y_data1 = piezo_adder1
        self.y_data2 = piezo_adder2

        # Update the line data
        self.line1.set_data(self.x_data, self.y_data1)
        self.line2.set_data(self.x_data, self.y_data2)

        # Redraw the canvas
        self.ax.relim()
        self.ax.autoscale_view()  # Update scale if necessary
        self.canvas.draw()