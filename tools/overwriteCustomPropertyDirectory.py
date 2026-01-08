#!/usr/bin/env python3

import os

from utilities.fileConstants import BASE_DIR, CUSTOM_PROPERTY_FILE_PATH
from utilities.classFoamDictEditor import FoamDictEditor


def overwrite_custom_property_directory():
    """Overwrites the 'directory' entry with the current project folder name."""
    # Instantiate dict editor
    fde = FoamDictEditor(CUSTOM_PROPERTY_FILE_PATH)

    # Get the base name of the current directory and set
    str_directory = "directory"
    old_directory = fde.get_value(str_directory)
    # os.path.normpath removes trailing slashes (e.g., 'path/to/dir/' -> 'path/to/dir')
    # os.path.basename gets the last component (e.g., 'path/to/dir' -> 'dir')
    new_directory = os.path.basename(os.path.normpath(BASE_DIR))
    print(f"Overwriting old directory {old_directory} with current directory {new_directory}")
    fde.set_value('directory', new_directory)
