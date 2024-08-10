# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 17:20:02 2024

@author: JoanaCatarino

"""
import csv
import os
import random

# Define the spouts and tones
spouts = ['Left', 'Right']
tones = ['5KHz', '10KHz']

# List of animals that need assigment of pairs
animals = ['452688', '542729', '757457', '754563']

# Directory and filename for csv with assignments
directory = 'C:/Users/JoanaCatarino/Joana/test_directory'
filename = 'spout_tone_generator.csv'

# Generate all possible pairs of spouts and tones, which are:
    # left - 5KHz; left - 10KHz; right - 5KHz; right - 10KHz
pairs = [(spout, tone) for spout in spouts for tone in tones]

# Create complementary pair for each assignment
# Example: If a subject is assigned (Left, 5KHz), the complementary pair for Right will be (Right, 10KHz)
def complementary_pair(pair):
    spout, tone = pair
    # Find the complementary spout and tone
    complementary_spout = 'Right' if spout == 'Left' else 'Left'
    complementary_tone = '10KHz' if tone == '5KHz' else '5KHz'
    return (complementary_spout, complementary_tone)


def generate_assignments():
    assignments = []
    for pair in pairs:
        comp_pair = complementary_pair(pair)
        assignments.append((pair, comp_pair))
    return assignments

 
def assign_pairs(animals):
    
    assignments = generate_assignments()
    
    #Create a dictionary to hold animal assignments
    animal_assignments = {}
   
    # Randomly assign pairs to subjects, allowing repeats
    for animal in animals:
        pair_assignment = random.choice(assignments)
        animal_assignments[animal] = pair_assignment
    
    return animal_assignments    

def save_assignments(assignments, directory, filename):
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Path to the csv file
    file_path = os.path.join(directory, filename)
    
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write headers if the file does not exist
        if not file_exists:
            writer.writerow(['Animal', '5KHz', '10KHz'])
        
        # Write the subject assignments
        for animal, (pair, comp_pair) in assignments.items():
            row = [animal]
            # Determine which spout is assigned to 5KHz and 10KHz
            if pair[1] == '5KHz':
                row.append(pair[0])  # 'L' or 'R' for 5KHz
                row.append(comp_pair[0])  # 'L' or 'R' for 10KHz
            else:
                row.append(comp_pair[0])  # 'L' or 'R' for 5KHz
                row.append(pair[0])  # 'L' or 'R' for 10KHz
            writer.writerow(row) 

# Get the assignments
assignments = assign_pairs(animals)


# Save the assignments to a .csv file 
save_assignments(assignments, directory, filename)

# Print the results
for animal, (pair, comp_pair) in assignments.items():
    print(f'{animal} : {pair[0]} - {pair[1]} and {comp_pair[0]} - {comp_pair[1]}')