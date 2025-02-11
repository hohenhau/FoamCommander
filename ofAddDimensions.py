#!/usr/bin/python

"""Changes the dimensions of files from [] to [0 0 0 0 0 0 0] for ParaView Compatibility"""

import os

# Global Variables
DESIRED_FIELDS = {'yPlus', 'Co'}

def is_numeric(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def update_dimensions(file_path):
    # Read the file and find the line to replace
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Find the line containing "dimensions"
    for i, line in enumerate(lines):
        try:
            if 'dimensions' in line:
                lines[i] = 'dimensions      [0 0 0 0 0 0 0];\n'
                break
        except UnicodeDecodeError:
            continue  # Skip lines that can't be decoded

    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)


def obtain_paths_of_relevant_files(desired_fields):
    desired_fields = {'yPlus', 'Co'}
    base_dir = os.getcwd()
    time_steps = [i for i in os.listdir(base_dir) if is_numeric(i)]
    print("Time steps found:", time_steps)
    relevant_paths = list()
    for time_step in time_steps:
        time_dir = os.path.join(base_dir, time_step)
        print(f'Processing directory {time_dir}')
        fields = set([i for i in os.listdir(time_dir)])
        for desired_field in desired_fields:
            if desired_field in fields:
                relevant_paths.append(str(os.path.join(time_dir, desired_field)))
    return relevant_paths


def main():
    global DESIRED_FIELDS
    relevant_paths = obtain_paths_of_relevant_files(DESIRED_FIELDS)
    for relevant_path in relevant_paths:
        update_dimensions(relevant_path) 


if __name__ == '__main__':
    main()
