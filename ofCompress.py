#!/usr/bin/python

"""Uses 7zip Compresses all files in a directory with the exception of processor folders"""

import os
import subprocess

def main():
    Get the current directory
    current_dir = os.getcwd()
    dir_name = os.path.basename(current_dir)
    zip_file_path = os.path.join(current_dir, f"{dir_name}.7z")

    Collect files and directories to compress
    files_to_compress = []
    for root, dirs, files in os.walk(current_dir):
        # Skip directories containing 'processor'
        if 'processor' in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            files_to_compress.append(file_path)

    Compress the files
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
