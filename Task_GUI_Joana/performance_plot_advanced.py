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
        self.trial_numbers = []
        self.total_trials = []
        self.correct_trials = []
        self.incorrect_trials = []
        
        # Set Up Plot
        self.ax.set_ylabel("HR/FA")
        self.ax2.set_ylabel("d'", color='#9DB4C0')
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

        # Prevent duplicate updates using a flag
        if hasattr(self, 'plot_updated') and self.plot_updated:
            print(f"Skipping duplicate plot update for trial {total_trials}")
            return  # Exit early if the plot was already updated
        
        self.plot_updated = True  # Set flag to prevent multiple updates

        # Increment trial number (should match total number of trials, including omissions)
        #trial_number = len(self.trial_numbers)   # Use independent counter
        self.trial_numbers.append(trial_number)
        
        # Always append total trials to keep trial history
        self.total_trials.append(total_trials)
    
        # If this is the first trial, initialize previous values
        if len(self.correct_trials) > 0:
            last_correct = self.correct_trials[-1]
            last_incorrect = self.incorrect_trials[-1]
        else:
            last_correct = 0
            last_incorrect = 0
            
        # Use the exact number of completed trials for the x-axis
        trial_numbers = list(range(1, total_trials + 1))
        self.total_trials = trial_numbers
    
        # Ensure y-values are correctly assigned
        self.correct_trials.append(correct_trials)
        self.incorrect_trials.append(incorrect_trials)
    
        # Keep previous values if no new correct/incorrect trial data is received
        self.correct_trials.append(correct_trials if correct_trials is not None else last_correct)
        self.incorrect_trials.append(incorrect_trials if incorrect_trials is not None else last_incorrect)
    
        # Convert lists to NumPy arrays
        total_trials_arr = np.array(self.total_trials)
        correct_trials_arr = np.array(self.correct_trials)
        incorrect_trials_arr = np.array(self.incorrect_trials)
    
        # Calculate Hit Rate (HR) and False Alarm Rate (FA)
        HR = (correct_trials_arr + 0.5) / (total_trials_arr + 1) #Hit rate
        FA = (incorrect_trials_arr + 0.5) / (total_trials_arr + 1) # False alarm
        
        # Clip HR and FA to avoid -inf and inf issues in norm.ppf()
        HR = np.clip(HR, 0.01, 0.99)
        FA = np.clip(FA, 0.01, 0.99)
        
        # Calculate d' (d-prime)
        d_prime = norm.ppf(HR) - norm.ppf(FA)

        # Ensure trial numbers are actual trial count
        trial_numbers = np.array(self.trial_numbers, dtype=int)

        # Clear and Redraw Stair Plot
        self.ax.clear()
        self.ax2.clear()        
        
        self.ax.step(trial_numbers, HR, where='post', color='black', linewidth=2, label='Hit Rate')
        self.ax.step(trial_numbers, FA, where='post', color='red', linewidth=2, label='False Alarm')
        
        # Plot d' (d-prime) on the secondary y-axis (right)
        self.ax2.step(trial_numbers, d_prime, color='#9DB4C0', linewidth=2, label="d'")
      
        # Update Labels & Formatting
        self.ax.set_ylabel("HR/FA", labelpad=7)
        self.ax2.set_ylabel("d'", color='#9DB4C0')
        self.ax.grid(True)
        
        # Set y-axis tick labels to whole numbers
        self.ax.set_ylim(0, 1)
        
        # **Explicitly Set Y-Axis Limits for d'**
        self.ax2.set_ylim(min(d_prime) - 0.5, max(d_prime) + 0.5)  # Expand limits slightly
        
        # Ensure x-axis labels are integers (no decimals)
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        # Format y-axes
        self.ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.1f}'))
        self.ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.1f}'))
        
        # Ensure right y-axis labels are visible
        self.ax2.tick_params(axis='y', labelcolor='#27605F')
        
        # Add legend and set colors
        # Combine Legends for both axes
        lines1, labels1 = self.ax.get_legend_handles_labels()
        lines2, labels2 = self.ax2.get_legend_handles_labels()
        self.ax.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=3, frameon=False, prop={'size':9})
            
        # Adjust layout to increase padding at the top
        self.figure.subplots_adjust(top=0.85)  

        # Redraw Canvas
        self.ax.relim() 
        self.ax.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.canvas.draw()
        
    def reset_plot(self):
        """Clears the plot data and refreshes the figure."""
        self.trial_numbers.clear()
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
        self.ax2.set_ylabel("d'", color='#9DB4C0')
        self.ax2.set_ylim(-2, 2)  # Reset range for d'
        self.ax2.tick_params(axis='y', labelcolor='#27605F')
        
        # Ensure that lists remain the same size when the next trial starts
        self.trial_numbers.append(0)
        self.total_trials.append(0)
        self.correct_trials.append(0)
        self.incorrect_trials.append(0)

        # Redraw the canvas
        self.canvas.draw()
