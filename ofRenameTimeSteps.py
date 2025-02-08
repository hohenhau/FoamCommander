#!/usr/bin/python

import os
import re

def detect_digit_counts(directory):
    """Detects the max number of leading and trailing digits in folder names."""
    number_pattern = re.compile(r'^\d+(\.\d+)?$')
    leading_digits = 0
    trailing_digits = 0

    for item in os.listdir(directory):
        if number_pattern.fullmatch(item) and item != "0":
            if '.' in item:
                before_decimal, after_decimal = item.split('.')
            else:
                before_decimal, after_decimal = item, ""

            leading_digits = max(leading_digits, len(before_decimal))
            trailing_digits = max(trailing_digits, len(after_decimal))

    return leading_digits, trailing_digits

def format_number(name, leading_digits, trailing_digits):
    """Formats a numeric folder name to have uniform leading/trailing digits."""
    if name == "0":
        return name  # Do not change the "0" folder

    num = float(name)  # Convert to float for normalization
    formatted_name = f"{num:0{leading_digits}.{trailing_digits}f}"

    return formatted_name

def rename_numeric_folders(directory):
    """Renames numeric folders to a uniform format based on detected digit counts."""
    number_pattern = re.compile(r'^\d+(\.\d+)?$')

    # Automatically detect digit counts
    leading_digits, trailing_digits = detect_digit_counts(directory)

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        if os.path.isdir(item_path) and number_pattern.fullmatch(item) and item != "0":
            new_name = format_number(item, leading_digits, trailing_digits)
            new_path = os.path.join(directory, new_name)

            if new_name != item:
                try:
                    os.rename(item_path, new_path)
                    print(f"Renamed timestep: {item} -> {new_name}")
                except Exception as e:
                    print(f"Error renaming {item}: {e}")

if __name__ == "__main__":
    target_directory = os.getcwd()  # Use the directory where the script is run
    rename_numeric_folders(target_directory)

