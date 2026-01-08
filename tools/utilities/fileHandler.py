#!/usr/bin/python

import os
import sys
import subprocess
import shutil


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


def get_final_path_components(path: str) -> str:
    """Returns the ending of the target path for display purposes."""
    abs_path = os.path.abspath(path)
    path_parts = abs_path.split(os.sep)
    relevant_parts = path_parts[-2:] if len(path_parts) > 1 else path_parts[-1:]
    if not relevant_parts:
        return ""
    # Pass the first element as the required 'path' argument, then unpack the rest
    # This satisfies the (path, *paths) signature requirement
    return str(os.path.join(relevant_parts[0], *relevant_parts[1:]))


# ----- File Handler ------------------------------------------------------------------------------------------------- #

def check_file_exists(path:str, file_name:str):
    """Check if a specified file exists"""
    if not os.path.isfile(path):
        display_path = get_final_path_components(path)
        print(f"Error: No file not found at {display_path}")
        sys.exit(1)


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


def check_and_create_file(file_directory: str, file_name: str, template_file_path: str) -> None:
    """Checks if a file exists and if not, creates if from a template"""
    check_directory_exists(file_directory)
    check_directory_exists(template_file_path)
    file_path = os.path.join(file_directory, file_name)
    if not os.path.isfile(file_path):
        shutil.copy2(template_file_path, file_path)

