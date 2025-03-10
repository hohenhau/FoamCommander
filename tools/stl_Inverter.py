#!/usr/bin/env python3
import os
import re
import sys

def invert_stl_normals(input_path):
    """
    Reads an STL file and inverts all normal vectors while preserving formatting.
    
    Args:
        input_path (str): Path to the input STL file
    
    Returns:
        str: Path to the output file with inverted normals
    """
    # Check if file exists
    if not os.path.isfile(input_path):
        print(f"Error: File '{input_path}' does not exist.")
        sys.exit(1)
    
    # Check if file has .stl extension (case insensitive)
    if not input_path.lower().endswith(('.stl')):
        print(f"Error: '{input_path}' is not an STL file. File must have .stl extension.")
        sys.exit(1)
    
    # Create output filename
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_inverted{ext}"
    
    # Regex pattern to match normal vectors line
    normal_pattern = re.compile(r'(.*facet normal\s+)(-?\d+\.\d+e[+-]\d+)(\s+)(-?\d+\.\d+e[+-]\d+)(\s+)(-?\d+\.\d+e[+-]\d+)(.*)')
    
    # Process the file
    try:
        with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
            for line in infile:
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
                    
                    # Write the inverted normal line
                    inverted_line = f"{prefix}{x_inverted}{space1}{y_inverted}{space2}{z_inverted}{suffix}"
                    outfile.write(inverted_line)
                else:
                    # Write unchanged line
                    outfile.write(line)
        
        print(f"Successfully inverted normal vectors. Output saved to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error processing STL file: {e}")
        sys.exit(1)

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
    invert_stl_normals(sys.argv[1])
