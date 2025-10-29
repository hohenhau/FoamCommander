#!/usr/bin/env python3

"""
This script processes OpenFOAM log files to extract and plot residual data.
Plots and CSV files are saved in the OpenFOAM standard 'postProcessing' directory.
"""

import re
import matplotlib.pyplot as plt
import os
import sys
import argparse
import csv
from datetime import datetime

def extract_residuals(log_file):
    """Extract residual data from OpenFOAM log file."""
    residuals = {}
    iterations = []
    
    time_pattern = r"^Time = (\d+(?:\.\d+)?)"
    residual_pattern = r"^.+?:  Solving for (.+?), Initial residual = (.+?), Final residual = (.+?), No Iterations (.+)$"
    
    current_time = None
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                time_match = re.match(time_pattern, line)
                if time_match:
                    current_time = float(time_match.group(1))
                    iterations.append(current_time)
                    continue
                
                res_match = re.match(residual_pattern, line)
                if res_match and current_time is not None:
                    field = res_match.group(1)
                    final_res = float(res_match.group(3))
                    
                    if field not in residuals:
                        residuals[field] = []
                    residuals[field].append(final_res)
                    
    except FileNotFoundError:
        print(f"Error: Log file '{log_file}' not found!")
        sys.exit(1)
    
    return iterations, residuals

def save_residuals_to_csv(iterations, residuals, output_path):
    """Save residual data to a CSV file."""
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header row
        header = ['Time'] + list(residuals.keys())
        writer.writerow(header)
        
        # Write data rows
        min_len = min(len(iterations), *(len(values) for values in residuals.values()))
        for i in range(min_len):
            row = [iterations[i]] + [residuals[field][i] for field in residuals]
            writer.writerow(row)
    
    print(f"CSV file saved to: {output_path}")

def plot_residuals(log_file):
    """Create and save residual plots from OpenFOAM log data."""
    output_dir = os.path.join('postProcessing', 'residuals')
    os.makedirs(output_dir, exist_ok=True)
    
    iterations, residuals = extract_residuals(log_file)
    
    plt.figure(figsize=(12, 8))
    
    for field, values in residuals.items():
        min_len = min(len(iterations), len(values))
        plt.semilogy(iterations[:min_len], values[:min_len], label=field)
    
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Time')
    plt.ylabel('Residual')
    plt.title('OpenFOAM Residuals')
    plt.legend()
    plt.tight_layout()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_basename = f'residuals_{timestamp}'
    plot_path = os.path.join(output_dir, f'{output_basename}.png')
    csv_path = os.path.join(output_dir, f'{output_basename}.csv')
    
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {plot_path}")
    
    save_residuals_to_csv(iterations, residuals, csv_path)

def main():
    """Main function to handle command line arguments and run the plotting routine."""
    parser = argparse.ArgumentParser(
        description='Plot OpenFOAM residuals from log file and save as CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('log_file', 
                       nargs='?', 
                       default='log.foamRun',
                       help='Path to the OpenFOAM log file (default: log.foamRun)')
    
    args = parser.parse_args()
    plot_residuals(args.log_file)

if __name__ == "__main__":
    main()
