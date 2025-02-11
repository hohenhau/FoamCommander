import re
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import argparse


def extract_residuals(log_file):
    # Initialize dictionaries to store data
    residuals = {}
    iterations = []
    
    # Regular expressions for matching residual lines
    time_pattern = r"^Time = (\d+(?:\.\d+)?)"
    residual_pattern = r"^.+?:  Solving for (.+?), Initial residual = (.+?), Final residual = (.+?), No Iterations (.+)$"
    
    current_time = None
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                # Check for time step
                time_match = re.match(time_pattern, line)
                if time_match:
                    current_time = float(time_match.group(1))
                    iterations.append(current_time)
                    continue
                
                # Check for residual line
                res_match = re.match(residual_pattern, line)
                if res_match and current_time is not None:
                    field = res_match.group(1)
                    initial_res = float(res_match.group(2))
                    final_res = float(res_match.group(3))
                    
                    if field not in residuals:
                        residuals[field] = []
                    residuals[field].append(final_res)
    except FileNotFoundError:
        print(f"Error: Log file '{log_file}' not found!")
        sys.exit(1)
    
    return iterations, residuals


def plot_residuals(log_file, output_dir='plots', save_plot=True):
    # Extract data
    iterations, residuals = extract_residuals(log_file)
    
    # Create plots directory if it doesn't exist
    if save_plot:
        os.makedirs(output_dir, exist_ok=True)
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Plot each residual
    for field, values in residuals.items():
        # Ensure lengths match by using the minimum length
        min_len = min(len(iterations), len(values))
        plt.semilogy(iterations[:min_len], values[:min_len], label=field)
    
    # Customize the plot
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Time')
    plt.ylabel('Residual')
    plt.title('OpenFOAM Residuals')
    plt.legend()
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot if requested
    if save_plot:
        output_path = os.path.join(output_dir, 'residuals.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_path}")
    
    plt.show()


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Plot OpenFOAM residuals from log file')
    parser.add_argument('log_file', nargs='?', default='log', 
                        help='Path to the OpenFOAM log file (default: log)')
    parser.add_argument('-o', '--output-dir', default='plots', 
                        help='Directory to save the plot (default: plots)')
    # Parse arguments
    args = parser.parse_args()
    # Run the plotting function with provided arguments
    plot_residuals(args.log_file, args.output_dir)
