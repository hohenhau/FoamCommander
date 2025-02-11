#!/usr/bin/python

"""Changes the dimensions of files from [] to [0 0 0 0 0 0] for ParaView Compatibility"""

import os

def update_dimensions(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if 'dimensions' in line:
                line = 'dimensions      [0 0 0 0 0 0 0];\n'
            file.write(line)

def main():
    target_files = {'yPlus', 'zPlus', 'CourantNumber'}
    for root, _, files in os.walk('.'):
        for file_name in files:
            if file_name in target_files:
                file_path = os.path.join(root, file_name)
                update_dimensions(file_path)
                print(f'Updated dimensions in {file_path}')

if __name__ == '__main__':
    main()
