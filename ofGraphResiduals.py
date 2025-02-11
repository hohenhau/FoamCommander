#!/usr/bin/env python3

"""
This script processes OpenFOAM log files to extract and plot residual data.
Plots are saved in the OpenFOAM standard 'postProcessing' directory.
"""

import re
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import argparse
from datetime import datetime

def extract_residuals(log_file):
    """Extract residual data from OpenFOAM log file."""
    # Initialize data storage
    residuals = {}
    iterations = []
    
    # Regex patterns for log file parsing
    time_pattern = r"^Time = (\d+(?:\.\d+)?)"
    residual_pattern = r"^.+?:  Solving for (.+?), Initial residual = (.+?), Final residual = (.+?), No Iterations (.+)$"
    
    current_time = None
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                # Extract time step information
                time_match = re.match(time_pattern, line)
                if time_match:
                    current_time = float(time_match.group(1))
                    iterations.append(current_time)
                    continue
                
                # Extract residual information
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


def plot_residuals(log_file):
    """Create and save residual plots from OpenFOAM log data."""
    
    # Create postProcessing directory structure
    output_dir = os.path.join('postProcessing', 'residuals')
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract data
    iterations, residuals = extract_residuals(log_file)
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Plot each residual field
    for field, values in residuals.items():
        min_len = min(len(iterations), len(values))
        plt.semilogy(iterations[:min_len], values[:min_len], label=field)
    
    # Customize plot appearance
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Time')
    plt.ylabel('Residual')
    plt.title('OpenFOAM Residuals')
    plt.legend()
    plt.tight_layout()
    
    # Generate timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f'residuals_{timestamp}.png')

    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_path}")


def main():
    """Main function to handle command line arguments and run the plotting routine."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Plot OpenFOAM residuals from log file',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('log_file', 
                       nargs='?', 
                       default='log',
                       help='Path to the OpenFOAM log file (default: log)')
    # Parse arguments and run
    args = parser.parse_args()
    plot_residuals(args.log_file)


if __name__ == "__main__":
    main()
