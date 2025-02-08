#!/usr/bin/python

import os
import re

def delete_numeric_folders(directory):
    number_pattern = re.compile(r'^\d+(\.\d+)?$')

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # Check if it's a directory and matches the number pattern (except '0')
        if os.path.isdir(item_path) and number_pattern.fullmatch(item) and item != '0':
            try:
                # Recursively remove all files and subdirectories
                for root, dirs, files in os.walk(item_path, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for subdir in dirs:
                        os.rmdir(os.path.join(root, subdir))

                # Remove the now-empty directory
                os.rmdir(item_path)
                print(f"Removed: {item_path}")
            except Exception as e:
                print(f"Error removing {item_path}: {e}")

if __name__ == "__main__":
    target_directory = os.getcwd()  # Use the directory where the script is run
    delete_numeric_folders(target_directory)
