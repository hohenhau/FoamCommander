#!/usr/bin/env python3
import os
import re
import sys
import tempfile
import shutil

def invert_stl_normals(input_path):
    """
    Reads an STL file and inverts all normal vectors while also reversing vertex order.
    This ensures proper orientation reversal for OpenFOAM.
    Overwrites the original file with the modified content.
    True zero values in any scientific notation format are not inverted.
    
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
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
            
            with open(input_path, 'r') as original_file:
                lines = original_file.readlines()
                
                i = 0
                while i < len(lines):
                    line = lines[i]
                    
                    # Process normal vectors line
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
                        
                        # Look for vertex lines and reverse their order
                        if i+1 < len(lines) and "outer loop" in lines[i+1]:
                            temp_file.write(lines[i+1])  # Write "outer loop" line unchanged
                            
                            # Store vertex lines
                            vertex1 = lines[i+2]
                            vertex2 = lines[i+3]
                            vertex3 = lines[i+4]
                            
                            # Write vertices in reversed order (vertex1, vertex3, vertex2)
                            # Keep vertex1 in the same position but swap vertex2 and vertex3
                            temp_file.write(vertex1)
                            temp_file.write(vertex3)
                            temp_file.write(vertex2)

                            # Write endloop and endfacet lines
                            temp_file.write(lines[i+5])  # endloop
                            temp_file.write(lines[i+6])  # endfacet
                            
                            # Skip the lines we've already processed
                            i += 7
                            continue
                    else:
                        # Write unchanged line
                        temp_file.write(line)
                    
                    i += 1
        
        # Replace the original file with the temporary file
        shutil.move(temp_path, input_path)
        print(f"Successfully inverted normal vectors and vertex order in '{input_path}'")
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
    Only true zero values (in any scientific notation format) are not negated.
    
    Args:
        value_str (str): A string representing a number in scientific notation
        
    Returns:
        str: The negated value in same format, or unchanged if true zero
    """
    # Convert to float to check if it's mathematically zero
    # This handles different representations of zero like 0.000e+0, 0.000000e+000, etc.
    try:
        value = float(value_str)
        if value == 0.0:
            return value_str  # Don't modify true zero values
    except ValueError:
        # If conversion fails for some reason, continue with string-based approach
        pass
    
    # For all non-zero values
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
