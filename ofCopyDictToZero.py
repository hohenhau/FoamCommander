#!/usr/bin/python

"""Copies settings from 'system/createBafflePorous' to '0/p'"""

import os
import re

ORIGIN_FILE = 'system/createBafflePorous'
TARGET_FILE = '0/p'

def parse_baffle_settings(origin_path):
    if not os.path.exists(origin_path):
        print(f"Error: Origin file {origin_path} not found.")
        return {}

    with open(origin_path, 'r') as file:
        content = file.read()

    baffle_data = {}
    patch_pattern = re.compile(r'(\w+)\s*{\s*name\s+(\w+);.*?patchFields\s*{\s*p\s*{(.*?)}}', re.S)

    for patch_match in patch_pattern.finditer(content):
        logical_patch_name = patch_match.group(1)
        physical_patch_name = patch_match.group(2)
        patch_content = patch_match.group(3)

        coefficients = {}
        for key in ['D', 'I', 'length', 'uniformJump', 'value']:
            match = re.search(fr'{key}\s+(.*?);', patch_content)
            if match:
                coefficients[key] = match.group(1).strip()

        if coefficients:
            base_name = re.sub(r'\d+$', '', physical_patch_name)
            if base_name not in baffle_data:
                baffle_data[base_name] = coefficients

    return baffle_data

def update_target_file(target_path, baffle_data):
    if not os.path.exists(target_path):
        print(f"Error: Target file {target_path} not found.")
        return

    with open(target_path, 'r') as file:
        content = file.read()

    for base_name, coeffs in baffle_data.items():
        patch_group = f'(porousBaffle{base_name}0|porousBaffle{base_name}1)'
        patch_block = f'''    "{patch_group}"
    {{
        type            porousBafflePressure;
        patchType       cyclic;
        D               {coeffs['D']};
        I               {coeffs['I']};
        length          {coeffs['length']};
        uniformJump     {coeffs['uniformJump']};
        value           {coeffs['value']};
    }}'''

        if re.search(fr'\"{patch_group}\"', content):
            content = re.sub(fr'\"{patch_group}\".*?}}', patch_block, content, flags=re.S)
        else:
            insert_pos = content.rfind('}')
            content = content[:insert_pos] + patch_block + '\n' + content[insert_pos:]

    with open(target_path, 'w') as file:
        file.write(content)

    print(f"Updated {target_path} with baffle settings.")

def main():
    baffle_data = parse_baffle_settings(ORIGIN_FILE)
    if baffle_data:
        update_target_file(TARGET_FILE, baffle_data)
    else:
        print("No valid baffle data found in origin file.")

if __name__ == '__main__':
    main()

