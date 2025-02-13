#!/usr/bin/python

"""Copies settings from 'system/createBafflePorous' to '0/p'"""

import re
import sys
import os
from pathlib import Path
from typing import Dict, Optional

def read_file(file_path: Path) -> Optional[str]:
    """Read and return file contents, handling potential errors."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None

def extract_master_patches(content: str) -> Dict[str, Dict]:
    """Extract master patch configurations from createBafflePorous file."""
    patches = {}
    
    # Find all master patches and their configurations
    master_pattern = r'(\w+)\s*//\s*Master patch\s*\{[^{]*patchFields\s*\{[^{]*p\s*\{([^}]*)\}'
    matches = re.finditer(master_pattern, content, re.DOTALL)
    
    for match in matches:
        master_name = match.group(1)
        config = match.group(2)
        
        # Extract patch name
        name_match = re.search(r'name\s+(\w+)', match.group(0))
        if name_match:
            patch_name = name_match.group(1)
            
            # Parse configuration parameters
            params = {}
            param_patterns = {
                'type': r'type\s+(\w+)',
                'patchType': r'patchType\s+(\w+)',
                'D': r'D\s+(\d+)',
                'I': r'I\s+(\d+)',
                'length': r'length\s+([0-9.]+)',
                'uniformJump': r'uniformJump\s+(\w+)',
                'value': r'value\s+(\w+\s+[0-9.]+)'
            }
            
            for param, pattern in param_patterns.items():
                param_match = re.search(pattern, config)
                if param_match:
                    params[param] = param_match.group(1)
            
            patches[patch_name] = params
    
    return patches

def update_p_file_content(p_content: str, patch_configs: Dict[str, Dict]) -> str:
    """Update the p file content with new patch configurations."""
    # Create the new boundaryField entries
    new_entries = []
    
    # Keep existing entries that we don't need to modify
    boundary_field_match = re.search(r'boundaryField\s*\{([^}]*)\}', p_content, re.DOTALL)
    if not boundary_field_match:
        print("Error: Could not find boundaryField section in p file")
        return p_content
        
    existing_content = boundary_field_match.group(1)
    
    # Keep entries that aren't related to porous baffles
    for entry in re.finditer(r'"([^"]+)"\s*\{[^}]*\}', existing_content):
        entry_name = entry.group(1)
        if not any(name in entry_name for name in patch_configs.keys()):
            new_entries.append(entry.group(0))
    
    # Add new porous baffle entries
    for base_name, config in patch_configs.items():
        # Extract patch number (0 or 1) from base name
        patch_num = re.search(r'(\d+)$', base_name).group(1)
        paired_name = base_name[:-1] + ('1' if patch_num == '0' else '0')
        
        entry = f'''    "({base_name}|{paired_name})"
    {{
        type            {config.get('type', 'porousBafflePressure')};
        patchType       {config.get('patchType', 'cyclic')};
        D               {config.get('D', '0')};
        I               {config.get('I', '0')};
        length          {config.get('length', '0')};
        uniformJump     {config.get('uniformJump', 'false')};
        value           {config.get('value', 'uniform 0')};
    }}'''
        new_entries.append(entry)
    
    # Reconstruct the file content
    before_boundary = p_content[:boundary_field_match.start()]
    after_boundary = p_content[boundary_field_match.end():]
    
    new_content = (
        f"{before_boundary}boundaryField\n{{\n"
        f"{chr(10).join(new_entries)}\n"
        f"}}{after_boundary}"
    )
    
    return new_content

def main(source_path: str, target_path: str):
    """Main function to coordinate the configuration copying process."""
    # Convert paths to be relative to current working directory
    cwd = os.getcwd()
    source = Path(cwd) / source_path
    target = Path(cwd) / target_path
    
    # Read source file
    source_content = read_file(source)
    if not source_content:
        sys.exit(1)
    
    # Read target file
    target_content = read_file(target)
    if not target_content:
        sys.exit(1)
    
    # Extract configurations from source
    patch_configs = extract_master_patches(source_content)
    if not patch_configs:
        print("Error: No master patch configurations found in source file")
        sys.exit(1)
    
    # Update target content
    new_content = update_p_file_content(target_content, patch_configs)
    
    # Write updated content to target file
    try:
        with open(target, 'w') as f:
            f.write(new_content)
        print(f"Successfully updated {target}")
    except Exception as e:
        print(f"Error writing to {target}: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("Usage: python script.py <source_file> <target_file>")
    #     print("Example: python script.py system/createBafflePorous 0/p")
    #     sys.exit(1)
    
    # main(sys.argv[1], sys.argv[2])
    main('system/createBafflePorous', '0/p')

