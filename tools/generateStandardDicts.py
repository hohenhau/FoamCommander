#!/usr/bin/python

import os

# Global Variables
from utilities.fileConstants import TEMPLATE_CONSTANT_DIR, TEMPLATE_SYSTEM_DIR
from utilities.fileConstants import SYSTEM_DIR, CONSTANT_DIR


def generate_system_dicts():
    dict_names = ['blockMeshDict', 'controlDict', 'rankfile', 'functions']

    for dict_name in dict_names:
        template_path = os.path.join(TEMPLATE_SYSTEM_DIR, dict_name)
        output_path = os.path.join(SYSTEM_DIR, f'{dict_name}.gen')
        print(f'Generating {dict_name}.gen in {SYSTEM_DIR}')
        with open(output_path, 'w') as outfile, open(template_path) as template:
            outfile.write(template.read())

def generate_constant_dicts():
    dict_names = ['turbulenceProperties', 'transportProperties', 'transportProperties', 'RASProperties']

    for dict_name in dict_names:
        template_path = os.path.join(TEMPLATE_CONSTANT_DIR, dict_name)
        output_path = os.path.join(CONSTANT_DIR, f'{dict_name}.gen')
        print(f'Generating {dict_name}.gen in {CONSTANT_DIR}')
        with open(output_path, 'w') as outfile, open(template_path) as template:
            outfile.write(template.read())

if __name__ == "__main__":
    generate_system_dicts()
    generate_constant_dicts()
