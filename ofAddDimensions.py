#!/usr/bin/python
"""Updates the 'dimensions' field from [] to [0 0 0 0 0 0 0] for ParaView compatibility"""
import os
import struct
import numpy as np

# Global Variables
DESIRED_FIELDS = {'yPlus', 'Co'}

def is_numeric(text: str):
    """
    Checks if a string can be converted to a float.
    """
    try:
        float(text)
        return True
    except ValueError:
        return False

def update_dimensions(file_path: str):
    """Updates the 'dimensions' field to [0 0 0 0 0 0 0] for ParaView compatibility"""
    with open(file_path, 'rb') as file:
        data = file.read()
    # Locate the 'dimensions' string within the file
    start_index = data.find(b'dimensions      [')  # Find where 'dimensions [' starts
    if start_index == -1:
        print(f"No 'dimensions' field found in {file_path}")
        return
    # We need to know where the ']' corresponding to the 'dimensions' field is
    end_index = data.find(b'];', start_index)
    if end_index == -1:
        print(f"No closing '];' found for dimensions field in {file_path}")
        return
    # Replace the old dimensions with the new ones
    new_dimensions = b'dimensions      [0 0 0 0 0 0 0];'
    new_data = data[:start_index] + new_dimensions + data[end_index+2:]
    # Write the modified binary data back to the file
    with open(file_path, 'wb') as file:
        file.write(new_data)

def obtain_paths_of_relevant_files(desired_fields: set):
    """Obtains the paths of files that contain one of the specified desired fields"""
    base_dir = os.getcwd()
    time_steps = [i for i in os.listdir(base_dir) if is_numeric(i) or 'processor' in i]
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
    print(f'Changing dimensions for the following fields: {DESIRED_FIELDS}')
    file_paths = obtain_paths_of_relevant_files(DESIRED_FIELDS)
    for relevant_path in file_paths:
        update_dimensions(relevant_path)
    print(f'Updated {len(file_paths)} files')

if __name__ == '__main__':
    main()
