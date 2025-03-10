#!/usr/bin/env python3
import os
import re
import sys
import tempfile
import shutil

def invert_stl_normals(input_path):
    """
    Reads an STL file and inverts all normal vectors while preserving formatting.
    Overwrites the original file with the modified content.
    
    Args:
        input_path (str): Path to the input STL file
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if file exists
    if not os.path.isfile(input_path):
        print(f"Error: File '{input_path}' does not exist.")
        return False
    
    # Check if file has .stl extension (case insensitive)
    if not input_path.lower().endswith(('.stl')):
        print(f"Error: '{input_path}' is not an STL file. File must have .stl extension.")
        return False
    
    # Regex pattern to match normal vectors line
    normal_pattern = re.compile(r'(.*facet normal\s+)(-?\d+\.\d+e[+-]\d+)(\s+)(-?\d+\.\d+e[+-]\d+)(\s+)(-?\d+\.\d+e[+-]\d+)(.*)')
    
    # Process the file using a temporary file
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
            
            # Process the original file
            with open(input_path, 'r') as original_file:
                for line in original_file:
                    match = normal_pattern.match(line)
                    if match:
                        # Extract components
                        prefix = match.group(1)
                        x_normal = match.group(2)
                        space1 = match.group(3)
                        y_normal = match.group(4)
                        space2 = match.group(5)
                        z_normal = match.group(6)
                        suffix = match.group(7)
                        
                        # Invert normals by adding a negative sign or removing it
                        x_inverted = negate_value(x_normal)
                        y_inverted = negate_value(y_normal)
                        z_inverted = negate_value(z_normal)
                        
                        # Write the inverted normal line with the newline character
                        inverted_line = f"{prefix}{x_inverted}{space1}{y_inverted}{space2}{z_inverted}{suffix}\n"
                        temp_file.write(inverted_line)
                    else:
                        # Write unchanged line (already includes newline)
                        temp_file.write(line)
        
        # Replace the original file with the temporary file
        shutil.move(temp_path, input_path)
        print(f"Successfully inverted normal vectors in '{input_path}'")
        return True
        
    except Exception as e:
        print(f"Error processing STL file: {e}")
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        return False

def negate_value(value_str):
    """
    Negates a numeric value in scientific notation.
    
    Args:
        value_str (str): A string representing a number in scientific notation
        
    Returns:
        str: The negated value in same format
    """
    if value_str.startswith('-'):
        return value_str[1:]  # Remove the negative sign
    else:
        return f"-{value_str}"  # Add a negative sign

if __name__ == "__main__":
    # Check if a filename was provided
    if len(sys.argv) != 2:
        print("Usage: python stl_normal_inverter.py path/to/file.stl")
        sys.exit(1)
        
    # Process the STL file
    success = invert_stl_normals(sys.argv[1])
    if not success:
        sys.exit(1)
