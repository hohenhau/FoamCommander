#!/usr/bin/env python3

import sys
import subprocess


def get_numeric_input(prompt):
    """Get a numeric input from the user and exit if invalid."""
    value = input(f"{prompt}: ")
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        print("Invalid input. Exiting.")
        sys.exit(1)


def get_timestep_inputs():
    """Get CFD timestep metrics from the user."""
    start_time = get_numeric_input("Enter start time")
    step_size = get_numeric_input("Enter step size")
    steps = get_numeric_input("Enter number of steps")
    return start_time, step_size, steps


def get_field_inputs():
    """Get CFD field names from the user until they press enter with no input."""
    fields = []
    print("Enter CFD field names one by one (press enter without input to finish):")
    while True:
        field = input("Field: ").strip()
        if field == "":
            break
        fields.append(field)
    return fields


def reconstruct_par(start_time, step_size, steps, fields):
    """Run reconstructPar commands based on user inputs."""
    if fields:
        field_str = " ".join(fields)
        cmd = f"reconstructPar -fields '({field_str})'"
        print(f"Executing: {cmd}")
        subprocess.run(cmd, shell=True)

    for i in range(steps):
        time = start_time + i * step_size
        cmd = f"reconstructPar -time {time}"
        print(f"Executing: {cmd}")
        subprocess.run(cmd, shell=True)

    cmd = "reconstructPar -latestTime"
    print(f"Executing: {cmd}")
    subprocess.run(cmd, shell=True)


def main():
    """Process command-line arguments and handle missing inputs accordingly."""
    args = sys.argv[1:]

    # Check input length
    if len(args) < 3:
        # Query numbers
        print("Insufficient arguments. Please enter required timestep metrics.")
        start_time, step_size, steps = get_timestep_inputs()

        # Process fields if any exist in input
        fields = [arg for arg in args if not arg.replace('.', '', 1).isdigit()]
        if not fields:
            fields = get_field_inputs()

    else:
        # Check if first three inputs are numbers
        try:
            start_time = float(args[0]) if "." in args[0] else int(args[0])
            step_size = float(args[1]) if "." in args[1] else int(args[1])
            steps = int(args[2])
            fields = args[3:]  # Remaining arguments are fields
        except ValueError:
            print("Invalid numeric input. Please enter required timestep metrics.")
            start_time, step_size, steps = get_timestep_inputs()
            fields = args  # Process remaining input as fields

        # If there are no fields in input, query fields
        if not fields:
            print("No fields specified for reconstruction")
            fields = get_field_inputs()

    reconstruct_par(start_time, step_size, steps, fields)


if __name__ == "__main__":
    main()
