#!/usr/bin/python

"""Changes the dimensions of files from [] to [0 0 0 0 0 0 0] for ParaView Compatibility"""

import os

def is_numeric(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def update_dimensions(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        print(f"Warning: Skipping binary file {file_path} due to decoding error.")
        return

    with open(file_path, 'w', encoding='utf-8') as file:
        for line in lines:
            if 'dimensions' in line:
                line = 'dimensions      [0 0 0 0 0 0 0];\n'
            file.write(line)


def main():
    target_files = {'yPlus', 'zPlus', 'CourantNumber'}
    current_dir = '.'

    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        if os.path.isdir(item_path) and is_numeric(item):
            for root, _, files in os.walk(item_path):
                for file_name in files:
                    if file_name in target_files:
                        file_path = os.path.join(root, file_name)
                        update_dimensions(file_path)
                        print(f'Processed file: {file_path}')


if __name__ == '__main__':
    main()
