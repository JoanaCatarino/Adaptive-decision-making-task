# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 16:52:36 2024

@author: JoanaCatarino

- Creates a .csv file for data and .json file that contains info about the session(animal_id, date, time, task, box)
- Defines the name format for the files when saving data, as well as the location in which the files are being saved
- Defines data structure for saved files, which remains the same across tasks
"""
import os
import csv
import json
from PyQt5.QtCore import QTimer, QDate, QTime

home = os.getenv('HOME')

# Define the save directory path directly here
SAVE_DIRECTORY = os.path.join(home,"save_dir")

# Create a dictionary for the different tasks with the identifier that is used in the data file name
TASK_NICKNAME = {
    'Free Licking': 'FreeLick',
    'Spout Sampling': 'SpoutSamp',
    'Two-Choice Auditory Task': '2ChoiceAuditory',
    'Adaptive Sensorimotor Task': 'AdaptSensorimotor',
    'Adaptive Sensorimotor Task w/ Distractor': 'AdaptSensorimotor_distractor',
    'Free Pressing': 'FreePress',
    'Press Sampling': 'PressSamp',
    'Two-Choice Lever Task': '2ChoiceLever',
    'Two-Choice Auditory Task Blocks': '2ChoiceBlocks'}

# Save data
if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)

def create_data_file(date_label, animal_id_combobox, task_combobox, box_combobox):
    # Check if the save directory is set
    if not SAVE_DIRECTORY:
        raise ValueError("Save directory not set")

    # Fetch the current date text from the date label
    date_text = date_label.text()

    # Parse the date text into a QDate object
    # Assuming the date text is in the format "yyyy-mm-dd"
    try:
        date_obj = QDate.fromString(date_text, "yyyy-MM-dd")
        formatted_date = date_obj.toString("yyyyMMdd")
    except Exception as e:
        raise ValueError(f"Error parsing date: {e}")

    # Find the current time
    current_time = QTime.currentTime().toString("HHmmss")

    # Find the selected animal ID
    animal_id = animal_id_combobox.currentText()

    # Find the selected task
    task = task_combobox.currentText()

    # Find the box in which the animal is was trained that day
    box = box_combobox.currentText()
    
    # Get the short name for the task to save in the file name
    task_nickname = TASK_NICKNAME.get(task, 'UNK') # unk is for unknown is the task selected is not defined in the dictionary

    # Construct the directory path for the animal ID within the saved directory
    animal_directory = os.path.join(SAVE_DIRECTORY, animal_id)

    # Create the directory if it does not exist
    if not os.path.exists(animal_directory):
        os.makedirs(animal_directory)

    # Construct the base file name (for both csv and json file)
    base_file_name = f'{task_nickname}_{animal_id}_{formatted_date}_{current_time}_box{box}'
    csv_file_path = os.path.join(animal_directory, base_file_name + '.csv')
    json_file_path = os.path.join(animal_directory, base_file_name + '.json')

    # Ensure the file name is unique for both csv and json files
    counter = 1
    while os.path.exists(csv_file_path) or os.path.exists(json_file_path):
        file_name = f'{task_nickname}_{animal_id}_{formatted_date}_{current_time}_box{box}_{counter}'
        csv_file_path = os.path.join(animal_directory, base_file_name + '.csv')
        json_file_path = os.path.join(animal_directory, base_file_name + '.json')
        counter += 1
        
    # Define common csv headers for all tasks - this order and info remains the same across tasks
    headers = ["trial_number", "trial_start", "trial_end", "trial_duration", "ITI", "block", "early_lick",
               "stim", "8KHz", "16KHz", "lick", "left_spout", "right_spout", "lick_time", "reward",
               "punishment", "omission", "RW", "QW", "WW", "valve_opening", "ITImin", "ITImax",
               "threshold_left", "threshold_right", "autom_reward", "no_punishment","ignore_licks", "catch_trial",
               "distractor_trial", "distractor_left", "distractor_right", "session_start"]

    # Create the CSV file and leave it open so tha the different heads can be defined per task
    with open(csv_file_path, 'w', newline='') as csv_file:
       writer = csv.writer(csv_file)
       writer.writerow(headers)

    # Create the json file and write important info to keep track of different sessions
    session_info = {'animal_id': animal_id,
                   'date': formatted_date,
                   'time': current_time,
                   'task': task,
                   'box' : box}

    with open(json_file_path, 'w') as json_file:
       json.dump(session_info, json_file, indent=4)

    return csv_file_path, json_file_path



