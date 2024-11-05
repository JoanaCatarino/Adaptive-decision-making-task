# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 16:52:36 2024

@author: JoanaCatarino

- This script is currently creating a .csv file for data and .json file that contains info about the session(animal_id,
date, time, task)

"""
import os
import csv
import json
from PyQt5.QtCore import QTimer, QDate, QTime

# Define the save directory path directly here
SAVE_DIRECTORY = "/home/rasppi-ephys/test_dir" 

if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)

def write_task_start_file(date_label, animal_id_combobox, task_combobox, box_combobox):
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
    
    # Find the current time
    current_time = QTime.currentTime().toString("HHmm")
    
    # Find the selected animal ID
    animal_id = animal_id_combobox.currentText()
    
    # Find the selected task
    task = task_combobox.currentText()
    
    # Find the box in which the animal is was trained that day
    box = box_combobox.currentText()
    
    # Construct the directory path for the animal ID within the saved directory
    animal_directory = os.path.join(SAVE_DIRECTORY, animal_id)
    
    # Create the directory if it does not exist
    if not os.path.exists(animal_directory):
        os.makedirs(animal_directory)
    
    # Construct the base file name (for both csv and json file)
    base_file_name = f"{animal_id}_{formatted_date}_{current_time}"
    csv_file_path = os.path.join(animal_directory, base_file_name + '.csv')
    json_file_path = os.path.join(animal_directory, base_file_name + '.json')
    
    # Ensure the file name is unique for both csv and json files
    counter = 1
    while os.path.exists(csv_file_path) or os.path.exists(json_file_path):
        file_name = f'{animal_id}_{formatted_date}_{current_time}_{counter}'
        csv_file_path = os.path.join(animal_directory, base_file_name + '.csv')
        json_file_path = os.path.join(animal_directory, base_file_name + '.json')
        counter += 1
   
    # Create the CSV file and leave it open so tha the different heads can be defined per task 
    with open(csv_file_path, 'w', newline='') as csv_file:
       writer = csv.writer(csv_file)
   
    # Create the json file and write important info to keep track of different sessions
    session_info = {'animal_id': animal_id,
                   'date': formatted_date,
                   'time': current_time,
                   'task': task,
                   'box' : box}
   
    with open(json_file_path, 'w') as json_file:
       json.dump(session_info, json_file, indent=4)

    return csv_file_path, json_file_path


    

