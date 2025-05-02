# -*- coding: utf-8 -*-
"""
Created on Fri May  2 13:03:01 2025

@author: JoanaCatarino

file to create a new folder with all the files created during training that day so that they can easily transfered to the server
"""
from pathlib import Path
from datetime import datetime, date
import shutil

# Set the base folder to scan
home = Path.home()
save_dir = Path('save_dir')
base_folder = home / save_dir
to_transfer_folder = base_folder / "to_transfer"

# Create the 'to_transfer' folder if it doesn't exist
to_transfer_folder.mkdir(exist_ok=True)

# Get today's date
today = date.today()

# Recursively check all files in the base_folder
for file_path in base_folder.rglob("*"):
    if file_path.is_file():
        # Get creation time and convert to date
        created_time = datetime.fromtimestamp(file_path.stat().st_ctime).date()
        if created_time == today:
            # Copy to the 'to_transfer' folder
            shutil.copy2(file_path, to_transfer_folder / file_path.name)