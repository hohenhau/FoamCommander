#!/usr/bin/python

"""Uses 7zip Compresses all files in a directory with the exception of processor folders"""

import os
import subprocess

def main():
    # 1. Get the current directory
    current_dir = os.getcwd()
    dir_name = os.path.basename(current_dir)
    parent_dir = os.path.dirname(current_dir)
    zip_file_path = os.path.join(parent_dir, f"{dir_name}.7z")

    # 2. Delete existing zip file if it exists
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
        print(f"Deleted existing archive: {zip_file_path}")

    # 3. Collect files and directories to compress
    files_to_compress = []
    for root, dirs, files in os.walk(current_dir):
        # Skip directories containing 'processor'
        if 'processor' in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            files_to_compress.append(file_path)

    # 4. Compress the files
    if files_to_compress:
        try:
            subprocess.run(["7z", "a", zip_file_path] + files_to_compress, check=True)
            print(f"Compressed files into {zip_file_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create archive: {e}")
    else:
        print("No files to compress.")

if __name__ == "__main__":
    main()

