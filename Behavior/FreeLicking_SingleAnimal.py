# -*- coding: utf-8 -*-
"""
Created on Sun May 11 17:56:47 2025

@author: JoanaCatarino

Code to analyze free licking data for single animals and per training sesssion
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# ========== USER INPUT ==========

date_str = "20250512"  # Format: YYYYMMDD
protocol_name = "Free_Licking"
task_name = 'Free Licking'
base_dir = r"Z:\dmclab\Joana\Behavior\Data"
QW = '3' # input which quiet window was used in that session

# ================================

def run_analysis_on_file(input_csv_path, date_str, protocol_name, task_name, QW):
    try:
        df = pd.read_csv(input_csv_path)

        if 'lick' not in df.columns or 'left_spout' not in df.columns or 'right_spout' not in df.columns:
            print(f"Skipping file (missing expected columns): {input_csv_path}")
            return None

        # Preprocessing
        licks_df = df[['trial_number', 'session_start', 'lick', 'left_spout', 'right_spout']].copy()
        licks_df['time'] = licks_df.index * 0.1  # Simulated time in seconds
        licks_df['relative_time'] = licks_df['time']
        licks_only = licks_df[licks_df['lick'] == 1].copy()

        # Timing info
        start_time = df['trial_start'].min()
        end_time = df['trial_end'].max()
        session_duration_minutes = (end_time - start_time) / 60
        session_start = df['session_start'].iloc[0]
        licks_only['true_relative_time_min'] = (df.loc[licks_only.index, 'lick_time'] - session_start) / 60

        # Cumulative licks
        licks_only['is_left'] = licks_only['left_spout'] == 1
        licks_only['is_right'] = licks_only['right_spout'] == 1
        cumulative_total = licks_only.groupby('trial_number').size().cumsum()
        cumulative_left = licks_only[licks_only['is_left']].groupby('trial_number').size().cumsum()
        cumulative_right = licks_only[licks_only['is_right']].groupby('trial_number').size().cumsum()

        # Summary counts
        total_licks = len(licks_only)
        left_licks = licks_only['left_spout'].sum()
        right_licks = licks_only['right_spout'].sum()
        
        # Output path
        animal_id = input_csv_path.parts[-4]
        analysis_dir = input_csv_path.parents[2] / "Analysis" / protocol_name / date_str
        analysis_dir.mkdir(parents=True, exist_ok=True)
        output_path = analysis_dir / f"{animal_id}_{date_str}_{protocol_name}.png"

        # Plotting and saving
        plot_lick_analysis(licks_only, cumulative_total, cumulative_left, cumulative_right,
                           total_licks, left_licks, right_licks, session_duration_minutes, output_path, animal_id,
                           date_str, protocol_name, task_name, QW)
        return True

    except Exception as e:
        print(f"Error processing file {input_csv_path}: {e}")
        return None

def plot_lick_analysis(licks_only, cumulative_total, cumulative_left, cumulative_right,
                       total_licks, left_licks, right_licks, session_duration_minutes,
                       output_path, animal_id, date_str, protocol_name, task_name, QW,
                       top_color='#AC90BF', top_marker='x'):
   
    labels = ['Total', 'Left', 'Right']
    values = [total_licks, left_licks, right_licks]
    colors = ['#F5A885', '#BB5C7A', '#5EA5A3']
    x_pos = [0.5, 1.0, 1.5]

    fig = plt.figure(figsize=(12, 12))
    fig.suptitle(f"Animal: {animal_id} | Date: {date_str} | Task: {task_name} | QW: {QW}s",
        fontsize=14)
    gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 1], width_ratios=[1, 1], hspace=0.6)

    # Plot 1 - Licks over time
    ax0 = fig.add_subplot(gs[0, :])
    ax0.scatter(licks_only['true_relative_time_min'], [1]*len(licks_only), alpha=0.6, color=top_color, marker=top_marker)
    ax0.set_xlabel("Time (min)")
    ax0.set_title("Licks Over time")
    ax0.set_yticks([])
    ax0.set_xlim(0, session_duration_minutes)
    ax0.spines['top'].set_visible(False)
    ax0.spines['right'].set_visible(False)
    
        # Plot 2 - Licks over trials
    ax1 = fig.add_subplot(gs[1, :])
    ax1.plot(cumulative_total, drawstyle='steps-post', label="Total Licks", color="#F5A885")
    ax1.plot(cumulative_left, drawstyle='steps-post', label="Left Spout", color="#BB5C7A")
    ax1.plot(cumulative_right, drawstyle='steps-post', label="Right Spout", color="#5EA5A3")
    ax1.set_xlabel("Trial Number")
    ax1.set_ylabel("Total Licks")
    ax1.set_title("Licks over trials")
    ax1.grid(True, color="#DAD4D4")  # Only this plot has grid
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Plot 3 - Licks Summary (bar plot)    
    ax2 = fig.add_subplot(gs[2, 0])
    bars = ax2.bar(x_pos, values, width=0.2, color=colors)
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{int(height)}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5),
                     textcoords="offset points",
                     ha='center', va='bottom')

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(labels)
    ax2.set_ylabel("Licks")
    ax2.set_title("Lick Summary")
    ax2.set_xlim(0.3, 1.7)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # Plot 4 - Legend
    ax3 = fig.add_subplot(gs[2, 1])
    ax3.axis('off')
    ax3.legend(bars, ['Total Licks', 'Left Spout', 'Right Spout'],
               loc='center', fontsize=12)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path.with_suffix('.png'), dpi=300)
    plt.savefig(output_path.with_suffix('.pdf'), dpi=300)
    plt.savefig(output_path.with_suffix('.svg'))

def main(date_str, protocol_name, task_name, QW, base_dir):
    base_path = Path(base_dir)
    for animal_dir in base_path.iterdir():
        if not animal_dir.is_dir():
            continue
        data_folder = animal_dir / "Behavior" / date_str
        if not data_folder.exists():
            continue
        csv_files = list(data_folder.glob("*.csv"))
        if not csv_files:
            continue

        print(f"\nAnalyzing {animal_dir.name} — {csv_files[0].name}")
        run_analysis_on_file(csv_files[0], date_str, protocol_name, task_name, QW)

# Run the analysis
main(date_str, protocol_name, task_name, QW, base_dir)