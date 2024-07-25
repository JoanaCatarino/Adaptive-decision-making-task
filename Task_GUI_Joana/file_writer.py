# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 16:52:36 2024

@author: JoanaCatarino
"""
import os
from PySide6.QtCore import QTime, QDate

# Define the save directory path directly here
SAVE_DIRECTORY = "C:/Users/JoanaCatarino/Joana/test_directory"  # Update this path to your desired directory

if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)

def write_task_start_file(date_label, animal_id_combobox):
    # Check if the save directory is set
    if not SAVE_DIRECTORY:
        raise ValueError("Save directory not set")
    
    # Fetch the current date text from the date label
    date_text = date_label.text()
    
    # Parse the date text into a QDate object
    # Assuming the date text is in the format "dd-MM-yyyy"
    try:
        date_obj = QDate.fromString(date_text, "dd-MM-yyyy")
        formatted_date = date_obj.toString("ddMMyyyy")
    except Exception as e:
        raise ValueError(f"Error parsing date: {e}")
    
    # Fetch the current time
    current_time = QTime.currentTime().toString("HHmm")
    
    # Fetch the selected animal ID
    animal_id = animal_id_combobox.currentText()
    
    # Construct the directory path for the animal ID within the saved directory
    animal_directory = os.path.join(SAVE_DIRECTORY, animal_id)
    
    # Create the directory if it does not exist
    if not os.path.exists(animal_directory):
        os.makedirs(animal_directory)
    
    # Construct the base file name
    base_file_name = f"{animal_id}_{formatted_date}_{current_time}.txt"
    file_path = os.path.join(animal_directory, base_file_name)
    
    # Ensure the file name is unique
    counter = 1
    while os.path.exists(file_path):
        file_name = f"{animal_id}_{formatted_date}_{current_time}_{counter}.txt"
        file_path = os.path.join(animal_directory, file_name)
        counter += 1
    
    # Create the .txt file
    with open(file_path, 'w') as file:
        file.write(f"Task started for animal ID: {animal_id} at {current_time} on {formatted_date}\n")
    
    return file_path

