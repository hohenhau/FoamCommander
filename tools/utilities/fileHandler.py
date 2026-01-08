#!/usr/bin/python

import os
import sys
import subprocess


# ----- Directory Handler -------------------------------------------------------------------------------------------- #

def check_directory_exists(path: str) -> None:
    """Check that the target directory exists"""
    if not os.path.isdir(path):
        display_path = get_final_path_components(path)
        sys.exit(f'The directory {display_path} could not be found')


def create_directory(path: str) -> None:
    """Ensure that the target directory exists. If it does not exist, create it."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory created: {path}")
    else:
        print(f"Directory already exists: {path}")


def compress_directory(path: str) -> None:
    """Compress the target directory using 7Z for easy export"""
    cwd = os.getcwd()
    try:
        os.chdir(path)
        subprocess.run(["foco", "compress"], check=True)
    except subprocess.CalledProcessError:
        print(f'Could not compress {path}')
    finally:
        os.chdir(cwd)


def get_list_of_directories(path: str) -> list[str]:
    """Get a list of all directories within the target directory"""
    return sorted([os.path.join(path, dir) for dir in os.listdir(path) if os.path.isdir(os.path.join(path, dir))])


def get_final_path_components(path):
    """Returns the ending of the target path for display purposes"""
    abs_path = os.path.abspath(path)
    path_parts = abs_path.split(os.sep)
    extracted_parts = str(*path_parts[-2:])
    return os.path.join(extracted_parts) if len(path_parts) > 1 else path_parts[-1]


# ----- File Handler ------------------------------------------------------------------------------------------------- #

def get_list_of_files(path: str, suffix: str = "", contains: str = "") -> list[str]:
    """Get a list of all files in the target directory matching the suffix."""
    # Check the directory exists
    check_directory_exists(path)
    # Get a lost of relevant files
    files = [
        f for f in os.listdir(path)
        if f.lower().endswith(suffix.lower()) and
           contains.lower() in f.lower() and
           os.path.isfile(os.path.join(path, f))]
    if not files:
        display_path = get_final_path_components(path)
        if suffix == "" and contains == "":
            print(f'No files found in {display_path}')
        elif suffix != "" and contains == "":
            print(f'No {suffix} files found in {display_path}')
        elif suffix == "" and contains != "":
            print(f'No files containing {contains} found in {display_path}')
        else:
            print(f'No {suffix} files containing {contains} found in {display_path}')
        sys.exit(1)  # Terminate program
    return files
