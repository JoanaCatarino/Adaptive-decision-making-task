# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:47:58 2024

@author: JoanaCatarino
"""
import asyncio
import time


async def free_licking():
    print('Free Licking starting')
    quiet_window = 0 # pre-defined variable
    while True:
        print(f'Quiet window = {quiet_window}')
        await asyncio.sleep(1)


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
from gpiozero import AnalogInputDevice
import time

# Custom class extending AnalogInputDevice
class CustomAnalogInput(AnalogInputDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Additional initialization if needed

    def _read(self):
        # Replace this method with your actual reading logic
        # For example, if using another ADC library or direct GPIO reads
        # Return a normalized value between 0 and 1
        return 0.0  # Placeholder for actual analog read logic

# Create instances for left and right piezo sensors
left_piezo = CustomAnalogInput(channel=0)  # Replace channel with appropriate identifier
right_piezo = CustomAnalogInput(channel=1)  # Replace channel with appropriate identifier

# Define the threshold
threshold = 0.2

# Counters for the number of times each piezo registers a signal above the threshold
left_piezo_count = 0
right_piezo_count = 0
total_count = 0

try:
    while True:
        # Read normalized analog values from the custom analog input
        left_signal = left_piezo.value
        right_signal = right_piezo.value
        
        # Check if either signal is above the threshold
        if left_signal > threshold:
            left_piezo_count += 1
            total_count += 1
            print(f"correct (left), Total: {total_count}")
        
        if right_signal > threshold:
            right_piezo_count += 1
            total_count += 1
            print(f"correct (right), Total: {total_count}")
        
        # Minimal delay to prevent high CPU usage
        time.sleep(0.01)

except KeyboardInterrupt:
    # Handle any cleanup here if necessary
    print("Program interrupted, cleaning up...")
    print(f"Final counts - Left: {left_piezo_count}, Right: {right_piezo_count}, Total: {total_count}")
    
#%% test with buttons

from gpiozero import Button
import time

# Set up GPIO pins for the buttons (replace with actual GPIO pin numbers)
left_button = Button(17)
right_button = Button(27)

# Threshold for the duration in seconds and mandatory interval in seconds
press_threshold = 1.0  # 1 second
interval_threshold = 3.0  # 3 seconds

# Counters for the number of times each button is pressed above the threshold duration
left_button_count = 0
right_button_count = 0
total_count = 0
early_press_count = 0

# Time of the last valid press
last_valid_press_time = 0

# Function to handle button presses and count them
def handle_button_press(button, is_left):
    global left_button_count, right_button_count, total_count, early_press_count, last_valid_press_time

    # Record the current time
    current_time = time.time()
    
    # Check if the current press is an early press
    if current_time - last_valid_press_time < interval_threshold:
        early_press_count += 1
        print("early press")
        # Reset the last valid press time to enforce the mandatory interval
        last_valid_press_time = current_time
        return

    # Record the time when the button was pressed
    start_time = current_time
    
    # Wait until the button is released
    button.wait_for_release()
    
    # Calculate the duration the button was pressed
    press_duration = time.time() - start_time
    
    # Check if the press duration is above the threshold
    if press_duration > press_threshold:
        if is_left:
            left_button_count += 1
            print(f"correct (left), Total: {total_count + 1}")
        else:
            right_button_count += 1
            print(f"correct (right), Total: {total_count + 1}")
        total_count += 1
        # Update the last valid press time
        last_valid_press_time = current_time

# Assign the handle_button_press function to both buttons
left_button.when_pressed = lambda: handle_button_press(left_button, is_left=True)
right_button.when_pressed = lambda: handle_button_press(right_button, is_left=False)

# Keep the program running
try:
    while True:
        time.sleep(0.1)  # Keep the loop running, minimal delay to save CPU
except KeyboardInterrupt:
    # Cleanup and print final counts
    print("\nProgram interrupted, cleaning up...")
    print(f"Final counts - Left: {left_button_count}, Right: {right_button_count}, Total: {total_count}")
    print(f"Total early presses: {early_press_count}")
