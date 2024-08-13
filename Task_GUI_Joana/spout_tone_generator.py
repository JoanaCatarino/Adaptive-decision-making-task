# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 17:20:02 2024

@author: JoanaCatarino

"""
import csv
import os
import random
from collections import Counter

# Define the spouts and tones
spouts = ['Left', 'Right']
tones = ['5KHz', '10KHz']

# List of animals that need assigment of pairs
animals = ['452694', '542735', '757463', '754569', '234567']

# Directory and filename for csv with assignments
directory = 'C:/Users/JoanaCatarino/Joana/test_directory'
filename = 'spout_tone_generator.csv'

# Generate all possible pairs of spouts and tones, which are:
    # left - 5KHz; left - 10KHz; right - 5KHz; right - 10KHz
pairs = [(spout, tone) for spout in spouts for tone in tones]

# Create complementary pair for each assignment
# Example: If an animal is assigned (Left, 5KHz), the complementary pair for Right will be (Right, 10KHz)
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
            spout_5khz = (row[1], '5KHz')
            spout_10khz = (row[2], '10KHz')
            pair_counts[spout_5khz] += 1
            pair_counts[spout_10khz] += 1

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
            writer.writerow(['Animal', '5KHz', '10KHz'])
        
        # Write the animal assignments
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