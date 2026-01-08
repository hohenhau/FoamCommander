#!/usr/bin/env python3

import os

from utilities.fileConstants import BASE_DIR, CUSTOM_PROPERTY_FILE_PATH
from utilities.classFoamDictEditor import ClassFoamDictEditor


def overwrite_custom_property_directory():
    """Overwrites the 'directory' entry with the current project folder name."""
    # os.path.normpath removes trailing slashes (e.g., 'path/to/dir/' -> 'path/to/dir')
    # os.path.basename gets the last component (e.g., 'path/to/dir' -> 'dir')
    directory_name = os.path.basename(os.path.normpath(BASE_DIR))

    fde = ClassFoamDictEditor(CUSTOM_PROPERTY_FILE_PATH)
    fde.set_value('directory', directory_name)
