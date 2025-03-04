#!/usr/bin/python

"""Accepts files with a specified termination (.gen, .steady, .transient) and overwrite the base equivalent"""

import os
import shutil
import sys

def main():
    # Step 1: Get file ending from command-line argument or user input
    if len(sys.argv) > 1:
        file_ending = sys.argv[1].strip()
    else:
        file_ending = input("Enter the file ending to search for (e.g., transient, gen, steady): ").strip()

    # Validate input
    if not file_ending:
        print("No file ending provided. Exiting.")
        return

    # Step 2: Get current working directory
    working_dir = os.getcwd()
    print(f"Searching in directory: {working_dir}")

    # Step 3 & 4: Search for files with the given ending and create copies
    for root, _, files in os.walk(working_dir):
        for file in files:
            if file.endswith(f".{file_ending}"):
                source_path = os.path.join(root, file)

                # Generate new file name (remove file ending)
                new_file_name = file[:-(len(file_ending)+1)]  # Remove ".<ending>"
                destination_path = os.path.join(root, new_file_name)

                # Step 5: Copy and overwrite if necessary
                shutil.copy2(source_path, destination_path)

                # Print relative paths for cleaner output
                relative_source = os.path.relpath(source_path, working_dir)
                relative_destination = os.path.relpath(destination_path, working_dir)

                print(f"Copied: {relative_source} --> {relative_destination}")

    print("File processing complete.")

if __name__ == "__main__":
    main()

