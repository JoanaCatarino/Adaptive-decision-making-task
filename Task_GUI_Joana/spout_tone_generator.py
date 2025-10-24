# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 17:20:02 2024

@author: JoanaCatarino

Generates a spout-tone map in the form of a .csv file that should be present in all the boxes - some tasks need this file to run properly
    - Defines which tone is associated to each spout and the combination remains locked for all the training sessions
    - Atributes the pairs in a random way but taking into acount how many tone-spout pairs of each type exist so that in the end we have the same number of each
    - The generated file is read in the beginning of each task that relies on sounds
"""
import csv
import os
import random
from collections import Counter

# Define the spouts and tones
spouts = ['left', 'right']
tones = ['8KHz', '16KHz']

# List of animals that need assigment of pairs
animals = ["986215", "986235", "999770", "999772", "986167", "986168", "986169", "986170", "986171"]

# Directory and filename for csv with assignments
directory = 'L:/dmclab/Joana/Behavior/Spout-tone map'
filename = 'spout_tone_generator.csv'

# Generate all possible pairs of spouts and tones, which are:
    # left - 8KHz; left - 16KHz; right - 8KHz; right - 16KHz
pairs = [(spout, tone) for spout in spouts for tone in tones]

# Create complementary pair for each assignment
# Example: If an animal is assigned (Left, 8KHz), the complementary pair for Right will be (Right, 16KHz)
def complementary_pair(pair):
    spout, tone = pair
    # Find the complementary spout and tone
    complementary_spout = 'right' if spout == 'left' else 'left'
    complementary_tone = '16KHz' if tone == '8KHz' else '8KHz'
    return (complementary_spout, complementary_tone)


def generate_assignments():
    assignments = []
    for pair in pairs:
        comp_pair = complementary_pair(pair)
        assignments.append((pair, comp_pair))
    return assignments


def read_existing_assignments(filename):
    # Read the existing .csv file to get the count of different tone-spout pairs and existing animals
    pair_counts = Counter()
    existing_animals = []

    if not os.path.isfile(filename):
        return pair_counts, existing_animals

    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip header
        for row in reader:
            existing_animals.append(row[0])
            spout_8khz = (row[1], '8KHz')
            spout_16khz = (row[2], '16KHz')
            pair_counts[spout_8khz] += 1
            pair_counts[spout_16khz] += 1

    return pair_counts, existing_animals   

 
def assign_pairs(animals, existing_counts):
    
    assignments = generate_assignments()
    
    # Shuffle the assignments to introduce randomness
    random.shuffle(assignments)
    
    #Create a dictionary to hold animal assignments
    animal_assignments = {}
   
    # Randomly assign pairs to animals, allowing repeats
    #for animal in animals:
        #pair_assignment = random.choice(assignments)
        #animal_assignments[animal] = pair_assignment
    
    #return animal_assignments   

    for animal in animals:
        # Sort pairs by current count to prefer underrepresented pairs
        assignments.sort(key=lambda x: existing_counts[x[0]] + existing_counts[x[1]])
        
        # Choose the least represented pair
        chosen_pair, comp_pair = assignments[0]

        # Update counts with the chosen pair
        existing_counts[chosen_pair] += 1
        existing_counts[complementary_pair] += 1

        animal_assignments[animal] = (chosen_pair, comp_pair)

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
            writer.writerow(['Animal', '8KHz', '16KHz'])
        
        # Write the animal assignments
        for animal, (pair, comp_pair) in assignments.items():
            row = [animal]
            # Determine which spout is assigned to 8KHz and 16KHz
            if pair[1] == '8KHz':
                row.append(pair[0])  # 'L' or 'R' for 8KHz
                row.append(comp_pair[0])  # 'L' or 'R' for 16KHz
            else:
                row.append(comp_pair[0])  # 'L' or 'R' for 8KHz
                row.append(pair[0])  # 'L' or 'R' for 16KHz
            writer.writerow(row) 


# Read existing assignments to get the current pair counts and existing animals
existing_counts, existing_animals = read_existing_assignments(os.path.join(directory, filename))

# Filter out any animals that already exist in the file
new_animals = [animal for animal in animals if animal not in existing_animals]

if not new_animals:
    print("No new animals to add.")
else:
    # Get the assignments, ensuring an even distribution of pairs
    assignments = assign_pairs(animals, existing_counts)

    # Save the assignments to the CSV file
    save_assignments(assignments, directory, filename)


# Print the results
for animal, (pair, comp_pair) in assignments.items():
    print(f'{animal} : {pair[0]} - {pair[1]} and {comp_pair[0]} - {comp_pair[1]}')