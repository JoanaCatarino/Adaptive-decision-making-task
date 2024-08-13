# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 17:49:53 2024

@author: JoanaCatarino
"""
# =============================================================================
# class SpoutSampling:
#     def start (self):
#         print ('Spout sampling starting')
#         def stop():
#             print ('Spout sampling stopping')
#         self.stop = stop
# =============================================================================
        
#%%

# Start by importing the spout_tone generator file
# Establish the correct association between spout and tone for the animal selected in the dropdown menu

import pandas as pd

animal = '757463' # Select animal - needs to be done through the dropdown menu when the task starts
df = pd.read_csv('C:/Users/JoanaCatarino/Joana/test_directory/spout_tone_generator.csv')

# Function to retrieve data for a specific animal
def get_animal_data(animal):
    # Ensure that the 'Animal' column is treated as strings and handle any NaN or non-string values
    df['Animal'] = df['Animal'].astype(str).str.strip().str.lower()
    
    # Filter the DataFrame for the specified animal
    animal_data = df[df['Animal'] == animal]
    
    if not animal_data.empty:
        # Extract values from the '5 KHz' and '10 KHz' columns
        tone_5, tone_10 = animal_data[['5KHz', '10KHz']].values[0]
        return tone_5, tone_10
    else:
        return None, None  # Return None values if no data is found


tone_5, tone_10 = get_animal_data(animal)

if tone_5 is not None and tone_10 is not None:
    print(f"5KHz tone: {tone_5}")
    print(f"10KHz tone: {tone_10}")
else:
    print(f"No data found for {animal_name}")








