# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 10:50:44 2025

@author: JoanaCatarino
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

class PlotPerformance(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create Figure and Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax2 = self.ax.twinx()  # Create secondary y-axis

        # Initialize Data Lists
        self.total_trials = []
        self.correct_trials = []
        self.incorrect_trials = []
        
        # Set Up Plot
        self.ax.set_ylabel("HR/FA")
        self.ax2.set_ylabel("d'", color='#27605F')
        self.ax.set_ylim(0, 1)  # Ensure HR/FA stays within 0-1
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

    def update_plot(self, total_trials, correct_trials, incorrect_trials):
        """Update stair plot with new lick data."""

        # Append Data
        self.total_trials.append(total_trials)
        self.correct_trials.append(correct_trials)
        self.incorrect_trials.append(incorrect_trials)
        
        # Calculate variables for plots
        HR = ((np.array(self.correct_trials) + 0.5) / (np.array(self.total_trials) + 1)) # Hit rate
        FA = ((np.array(self.incorrect_trials) + 0.5) / (np.array(self.total_trials) + 1)) # False alarms
        
        # Clip HR and FA to avoid -inf and inf issues in norm.ppf()
        HR = np.clip(HR, 0.01, 0.99)
        FA = np.clip(FA, 0.01, 0.99)
        
        # Calculate d' (d-prime)
        d_prime = norm.ppf(HR) - norm.ppf(FA)

        # Generate x-axis values(trial_numbers)
        trial_numbers = np.arange(1, len(self.total_trials)+1, dtype=int)

        # Clear and Redraw Stair Plot
        self.ax.clear()
        self.ax2.clear()
        
        self.ax.step(trial_numbers, HR, where='post', color='black', linewidth=2, label='Hit Rate')
        self.ax.step(trial_numbers, FA, where='post', color='red', linewidth=2, label='False Alarm')
        
        # Plot d' (d-prime) on the secondary y-axis (right)
        self.ax2.plot(trial_numbers, d_prime, color='#27605F', linewidth=2, label="d'")
      
        # Update Labels & Formatting
        self.ax.set_ylabel("HR/FA", labelpad=9)
        self.ax2.set_ylabel("d'", color='#27605F')
        self.ax.grid(True)
        
        # Set y-axis tick labels to whole numbers
        self.ax.set_ylim(0, 1)
        
        # Ensure x-axis labels are integers (no decimals)
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        # Add legend and set colors
        # Combine Legends for both axes
        lines1, labels1 = self.ax.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        self.ax.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=3, frameon=False, prop={'size':9})
            
        # Adjust layout to increase padding at the top
        self.figure.subplots_adjust(top=0.85)  
        self.figure.subplots_adjust(right=0.95)

        # Redraw Canvas
        self.ax.relim() 
        self.ax.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.canvas.draw()
        
    def reset_plot(self):
        """Clears the plot data and refreshes the figure."""
        self.total_trials.clear()
        self.correct_trials.clear()
        self.incorrect_trials.clear()

        # Clear both axes
        self.ax.clear()
        self.ax2.clear()

        # Reinitialize the primary y-axis (HR & FA)
        self.ax.set_xlabel("Trial Number")
        self.ax.set_ylabel("HR / FA", color='black')
        self.ax.set_ylim(0, 1)
        self.ax.grid(True, linestyle='dotted')

        # Reinitialize the secondary y-axis (d-prime)
        self.ax2.set_ylabel("d'", color='#27605F')

        # Redraw the canvas
        self.canvas.draw()










