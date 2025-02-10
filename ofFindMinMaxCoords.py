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


if __name__ == "__main__":
    py_file_path = os.path.dirname(os.path.realpath(__file__))
    args_len = len(sys.argv)
    file_names = [sys.argv[i] for i in range(1, args_len)]
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

    boundary_extension = 0.000001
    print('Coordinates for the blockMeshDict:')
    print(f'Xmin {MIN_X - boundary_extension};  // minimum x')
    print(f'Xmax {MAX_X + boundary_extension};  // maximum x')
    print(f'Ymin {MIN_Y - boundary_extension};  // minimum y')
    print(f'Ymax {MAX_Y + boundary_extension};  // maximum y')
    print(f'Zmin {MIN_Z - boundary_extension};  // minimum z')
    print(f'Zmax {MAX_Z + boundary_extension};  // maximum z')
