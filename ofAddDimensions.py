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
    fields = {'yPlus', 'Co'}
    base_dir = os.getcwd()
    time_steps = [i for i in os.listdir(base_dir) if is_numeric(i)]
    print("Time steps found:", time_steps)
    relevant_files = list()
    for time_step in time_steps:
        time_dir = os.path.join(base_dir, time_step)
        for field in fields:
            # Collect all files from the directory
            time_files = [i for i in os.listdir(time_dir)]
            # Filter out the relevant files using the fields
            time_files = [i for i in time_files if os.path.isfile(i) and field in i]
            print(time_files)
            relevant_files = relevant_files + time_files
    for files in relevant_files:
        print(files)
        
        # item_path = os.path.join(current_dir, item)
        # if os.path.isdir(item_path) and is_numeric(item):
        #     for root, _, files in os.walk(item_path):
        #         for file_name in files:
        #             if file_name in fields:
        #                 file_path = os.path.join(root, file_name)
        #                 update_dimensions(file_path)

if __name__ == '__main__':
    main()
