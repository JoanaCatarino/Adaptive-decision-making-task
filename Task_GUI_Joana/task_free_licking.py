# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:47:58 2024

@author: JoanaCatarino

 -- Free Licking task --
- The goal of this task is to make the animals familiarized with the spouts and the reward type they give (sucrose water)
- In this task animals should receive a reward when they lick either of the spouts
- Criterion: After 100 licks a Quiet window of 3000 ms is introduced - never on the first session 
"""

# =============================================================================
# import asyncio
# import time
# 
# 
# async def free_licking():
#     print('Free Licking starting')
#     quiet_window = 0 # pre-defined variable
#     while True:
#         print(f'Quiet window = {quiet_window}')
#         await asyncio.sleep(1)
# =============================================================================

# =============================================================================
# =============================================================================
# class FreeLicking:
#     def start (self):
#         self.send_command_sync('free_licking')
#         print ('Free licking starting')
#         
#         def stop():
#             print ('Free licking stopping')
#         self.stop = stop
#         
# 
#     async def free_licking():
#         quiet_window = 0 # defined variable
#         print(quiet_window)
# =============================================================================

#%%

# virtual pin factory
from gpiozero.pins.mock import MockFactory
from gpiozero import Device
Device.pin_factory = MockFactory()


from gpiozero import Button
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Gpiozero pins - to be added in gpio_map.py file later
button_blue = Button(26)
button_red = Button(16)

# Initialize counters:
total_presses = 0
button_blue_presses = 0
button_red_presses = 0
early_presses = 0

# Define fixed variabled
threshold = 1  # threshold of 1 second

# Dictionary to store the press start time and last valid press times
press_start_times = {}
last_valid_press_time = 0
quiet_window = 3 # seconds

# Global variable to indicate the remaining time for the interval
remaining_time = 0
can_press_message_shown = False # Flag to track whether the message has been shown

# Data lists for plotting
times = []
button_blue_counts = []
button_red_counts = []
early_press_counts = []

# Define callback functions for each button
def button_blue_pressed():
    press_start_times[26] = time.time()
    
def button_blue_released():
    global total_presses, button_blue_presses, early_presses, last_valid_press_time, can_press_message_shown
    press_duration = time.time() - press_start_times[26]
    current_time = time.time()
    
    if press_duration >= 1: #Threshold of 1 second
        if current_time - last_valid_press_time >= quiet_window:
            total_presses += 1
            button_blue_presses += 1
            last_valid_press_time = current_time
            can_press_message_shown = False #Reset the flag after a valid press
            print(f'Pressed blue - Total presses:{total_presses}, button blue presses:{button_blue_presses}')
        else:
            early_presses +=1
            last_valid_press_time = current_time #Reset the interval timer
            can_press_message_shown = False #Reset the flag after a valid press
            print(f'Early press - Total early presses:{early_press}')
    update_plot_data()
    
def button_red_pressed():
    press_start_times[16] = time.time()
    
def button_red_released():
    global total_presses, button_red_presses, early_presses, last_valid_press_time, can_press_message_shown
    press_duration = time.time() - press_start_times[16]
    current_time = time.time()
    
    if press_duration >= 1: #Threshold of 1 second
        if current_time - last_valid_press_time >= quiet_window:
            total_presses += 1
            button_red_presses += 1
            last_valid_press_time = current_time
            can_press_message_shown = False #Reset the flag after a valid press
            print(f'Pressed red - Total presses:{total_presses}, button red presses:{button_red_presses}')
        else:
            early_presses +=1
            last_valid_press_time = current_time #Reset the interval timer
            can_press_message_shown = False #Reset the flag after a valid press
            print(f'Early press - Total early presses:{early_press}')
    update_plot_data()    
    
# Timer function to display the remaining time
def display_timer():
    global remaining_time, can_press_message_shown
    while True:
        current_time = time.time()
        if last_valid_press_time:
            remaining_time = quiet_window - (current_time - last_valid_press_time)
            if remaining_time > 0:
                print (f'Time until next valid press:{remaining_time:.1f} seconds', end='\r')
            elif not can_press_message_shown:
                print ('You can press a button now!', end='\r')
                can_press_message_shown = True #Set the flag to indicate that the message has been shown
        time.sleep(0.1) #Update every 100ms
        
# Start the timer display in a separate thread
timer_thread = threading.Thread(target = display_timer, daemon=True)
timer_thread.start()

def update_plot_data():
    current_time = time.time() - start_time
    times.append(current_time)
    button_blue_counts.append(button_blue_presses)
    button_red_counts.append(button_red_presses)
    early_press_counts.append(early_presses)
    
# Plotting function for real-time updates
def animate(i):
    plt.cla()
    plt.plot(times, button_blue_counts, label='Button blue presses', color='#3AA8C1')
    plt.plot(times, button_red_coutns, label='Button red presses', color='#7C0902')
    plt.plot(times, early_press_counts, label='Early presses', color='#FF7538')
    plt.xlabel('Time(s)')
    plt.ylabel('Count')
    plt.legend(loc='upper left')
    plt.tight_layout()
    
# Attach the callback functions to the button press events
button_blue.when_pressed = button_blue_pressed
button_blue.when_released = button_blue_released
button_red.when_pressed = button_red_pressed
button_red.when_released = button_red_released

print('Press the buttons...')

plt.show()

# Keep the program running to detect button presses
input('Press Enter to exit...\n')
 






