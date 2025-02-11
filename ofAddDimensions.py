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
        with open(file_path, 'rb') as file:
            lines = []
            for line in file:
                try:
                    decoded_line = line.decode('utf-8')
                    lines.append(decoded_line)
                    if 'dimensions' in decoded_line:
                        lines[-1] = 'dimensions      [0 0 0 0 0 0 0];\n'
                except UnicodeDecodeError:
                    print(f"Binary data encountered in {file_path}. Stopping processing.")
                    return
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        print(f'Processed file: {file_path}')
    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")

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

if __name__ == '__main__':
    main()
