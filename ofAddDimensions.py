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

    for time_step in time_steps:
        target_directory = os.path.join(base_dir, time_step)
        if not os.path.isdir(target_directory):  # Ensure it's a directory
            continue

        for field in fields:
            target_files = [i for i in os.listdir(target_directory)
                            if os.path.isfile(os.path.join(target_directory, i)) and field in i]
            print(f"Files found in {target_directory} for field '{field}': {target_files}")
        
        # item_path = os.path.join(current_dir, item)
        # if os.path.isdir(item_path) and is_numeric(item):
        #     for root, _, files in os.walk(item_path):
        #         for file_name in files:
        #             if file_name in fields:
        #                 file_path = os.path.join(root, file_name)
        #                 update_dimensions(file_path)

if __name__ == '__main__':
    main()
