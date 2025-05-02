# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 13:06:27 2025

@author: JoanaCatarino

Sets the real-time plots in the GUI for the free licking and spout sampling tasks
     - This plots have the number of licks over trials and in which spout the licks happened
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import FuncFormatter
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMainWindow, QSizePolicy
import datetime
import numpy as np
from scipy.stats import norm

class PlotLicks(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create Figure and Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Initialize Data Lists
        self.trial_numbers = []
        self.total_trials = []
        self.total_licks = []
        self.licks_left = []
        self.licks_right = []

        # Set Up Plot
        #self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Licks")
        self.ax.grid(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0,0,0,0) 
        layout.setSpacing(0) 
        self.setLayout(layout)
        
        #  new!! test to see if it improves layout of the plots
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        
        # Apply tight layout to ensure everything fits 
        self.figure.tight_layout(pad=2.9)  

    def update_plot(self, total_trials, total_licks, licks_left, licks_right):
        """Update stair plot with new lick data."""
        
        # Increment trial number (should match total number of trials, including omissions)
        trial_number = len(self.trial_numbers)   # Use independent counter
        self.trial_numbers.append(trial_number)
        
        # Always append total trials to keep trial history
        self.total_trials.append(total_trials)
        
        # Append Data
        self.total_licks.append(total_licks)
        self.licks_left.append(licks_left)
        self.licks_right.append(licks_right)
        
        # Ensure trial numbers are actual trial count
        trial_numbers = np.array(self.trial_numbers, dtype=int)
        # Convert lists to NumPy arrays
        total_trials_arr = np.array(self.total_trials)

        # Clear and Redraw Stair Plot
        self.ax.clear()
        self.ax.step(trial_numbers, self.total_licks, where='post', color='#FF864E', linewidth=2, label='Total licks')
        self.ax.step(trial_numbers, self.licks_left, where='post', color='#955C66', linewidth=2, linestyle= 'dashed', label='Licks left')
        self.ax.step(trial_numbers, self.licks_right, where='post', color='#4E8070', linewidth=2, linestyle= 'dashed', label='Licks right')
        
        # Update Labels & Formatting
        self.ax.set_ylabel("Licks", labelpad=9)
        self.ax.grid(True)
        
        # Set y-axis tick labels to whole numbers
        self.ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x)}'))
        
        # Ensure x-axis labels are integers (no decimals)
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        # Add legend and set colors
        legend = self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.18), ncol=3, frameon=False, prop={'size':8.5})
        for text, color in zip(legend.get_texts(), ['#FF864E', '#955C66', '#4E8070']):
            text.set_color(color)
            
        # Adjust layout to increase padding at the top
        self.figure.subplots_adjust(top=0.85)  
        self.figure.subplots_adjust(right=0.95)

        # Redraw Canvas
        self.ax.relim() 
        self.ax.autoscale_view() 
        self.canvas.draw()
        
    def reset_plot(self):
        """Clears the plot data and refreshes the figure."""
        self.trial_numbers.clear()
        self.total_trials.clear()
        self.total_licks.clear()
        self.licks_left.clear()
        self.licks_right.clear()
    
        self.ax.clear()  # Clear the existing plot
        self.ax.set_ylabel("Licks")
        self.ax.grid(True)
        
        # Keep a placeholder data point to avoid dimension mismatches
        self.trial_numbers.append(0)
        self.total_trials.append(0)
        self.total_licks.append(0)
        self.licks_left.append(0)
        self.licks_right.append(0)
    
        # Redraw the canvas
        self.canvas.draw()