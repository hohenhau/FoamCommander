#!/usr/bin/env python3

from utilities.fileConstants import BASE_DIR, CUSTOM_PROPERTY_FILE_PATH
from utilities.classFoamDictEditor import ClassFoamDictEditor

def overwrite_custom_property_directory():
    """Overwrites the directory stored in the custom property file."""
    fde = ClassFoamDictEditor(CUSTOM_PROPERTY_FILE_PATH)
    fde.set_value('directory', BASE_DIR.split('/')[-1])
