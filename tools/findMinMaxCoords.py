#!/usr/bin/python
import re
import os
import sys

# Global variables to track min/max coordinates and vertex count
MIN_X = float('+inf')
MIN_Y = float('+inf')
MIN_Z = float('+inf')
MAX_X = float('-inf')
MAX_Y = float('-inf')
MAX_Z = float('-inf')
VERTEX_COUNT = 0


def update_max_and_min(x: float, y: float, z: float):
    """
    Updates global min/max coordinates based on the given x, y, z values.
    """
    global MIN_X, MIN_Y, MIN_Z, MAX_X, MAX_Y, MAX_Z
    MAX_X = max(x, MAX_X)
    MAX_Y = max(y, MAX_Y)
    MAX_Z = max(z, MAX_Z)
    MIN_X = min(x, MIN_X)
    MIN_Y = min(y, MIN_Y)
    MIN_Z = min(z, MIN_Z)


def search_for_coordinates(text: str):
    """
    Searches for vertex coordinates in a of text and updates the min/max coordinate values
    """
    global VERTEX_COUNT
    match = re.search(r'vertex ([0-9.e\-+]+) ([0-9.e\-+]+) ([0-9.e\-+]+)', text)
    if match:
        x_coord = float(match.group(1))
        y_coord = float(match.group(2))
        z_coord = float(match.group(3))
        VERTEX_COUNT += 1
        update_max_and_min(x_coord, y_coord, z_coord)


def search_for_stl_files_in_directory(dir_path):
    """
    Function to collect a list of stl files from a directory
    """
    # Check if the directory exists
    if not os.path.isdir(dir_path):
        print(f"The directory '{dir_path}' does not exist.")
        sys.exit(1)
    stl_files = [os.path.join(dir_path, i) for i in os.listdir(dir_path) if i.endswith('.stl')]
    if not stl_files:
        print(f"No '.stl' files found in the directory '{dir_path}'.")
        sys.exit(1)
    print(f"Found the following '.stl' files in '{dir_path}': {stl_files}")
    return stl_files


if __name__ == "__main__":

    args_len = len(sys.argv)
    if args_len <= 1:
        print('No files specified, checking for files in constant/triSurface directory')
        file_names = search_for_stl_files_in_directory('constant/triSurface')
    else:
        file_names = [sys.argv[i] for i in range(1, args_len)]
    py_file_path = os.path.dirname(os.path.realpath(__file__))
    file_count = 0

    # Process each file provided as an argument
    for filename in file_names:
        with open(filename) as file:
            file_count += 1
            for line in file:
                search_for_coordinates(line)

    # Output results
    print(f'{file_count} files with {VERTEX_COUNT} vertices')
    print(f'X: {MIN_X} - {MAX_X}')
    print(f'Y: {MIN_Y} - {MAX_Y}')
    print(f'Z: {MIN_Z} - {MAX_Z}')

    precision_decimals = 4
    boundary_extension = 10**(-precision_decimals)
    print(f'\nCoordinates for the blockMeshDict (precision to {boundary_extension} metres):')
    print(f'Xmin {round(MIN_X - boundary_extension, precision_decimals)};  // minimum x')
    print(f'Xmax {round(MAX_X + boundary_extension, precision_decimals)};  // maximum x')
    print(f'Ymin {round(MIN_Y - boundary_extension, precision_decimals)};  // minimum y')
    print(f'Ymax {round(MAX_Y + boundary_extension, precision_decimals)};  // maximum y')
    print(f'Zmin {round(MIN_Z - boundary_extension, precision_decimals)};  // minimum z')
    print(f'Zmax {round(MAX_Z + boundary_extension, precision_decimals)};  // maximum z\n')
