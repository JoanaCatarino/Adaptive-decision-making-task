# -*- coding: utf-8 -*-
"""
Created on Sun May 11 17:56:47 2025

@author: JoanaCatarino
"""

import os
import pandas as pd

# ===== USER INPUT =====
date_str = "20250509"  # You can change this dynamically
protocol_name = "Free_Licking"
base_dir = r"Z:\dmclab\Joana\Behavior\Data"

# ======================
def run_analysis_on_file(input_csv_path):
    """Replace this with your actual analysis logic."""
    df = pd.read_csv(input_csv_path)
    # Example processing
    result = {"rows": len(df), "columns": len(df.columns)}
    return pd.DataFrame([result])


def main(date_str, protocol_name, base_dir):
    for animal_id in os.listdir(base_dir):
        animal_path = os.path.join(base_dir, animal_id)
        behavior_data_path = os.path.join(animal_path, "Behavior", date_str)

        if not os.path.isdir(behavior_data_path):
            continue  # Skip if no data folder for this date

        # Get the first .csv file in the folder (adjust as needed)
        csv_files = [f for f in os.listdir(behavior_data_path) if f.endswith('.csv')]
        if not csv_files:
            continue  # No data file to analyze

        input_csv_path = os.path.join(behavior_data_path, csv_files[0])

        # Run your analysis
        result_df = run_analysis_on_file(input_csv_path)

        # Build output path
        analysis_dir = os.path.join(animal_path, "Analysis", protocol_name)
        os.makedirs(analysis_dir, exist_ok=True)

        output_csv_path = os.path.join(analysis_dir, f"{animal_id}_{protocol_name}.csv")
        result_df.to_csv(output_csv_path, index=False)
        print(f"Analysis complete for {animal_id}: saved to {output_csv_path}")

if __name__ == "__main__":
    main(date_str, protocol_name, base_dir)