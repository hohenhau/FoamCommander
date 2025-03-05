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
    """Extract patch configurations from createBafflePorous file."""
    patches = {}
    
    # Clean the content
    content = re.sub(r'\*+', '', content)
    print("Debug: Looking for baffles section...")
    
    # Find the baffles section with a more lenient pattern
    baffles_pattern = r'baffles[^{]*{(.*?)^}(?=\s*//|\s*$)'
    baffles_match = re.search(baffles_pattern, content, re.DOTALL | re.MULTILINE)
    
    if not baffles_match:
        print("Debug: Pattern failed. Printing content around 'baffles':")
        if 'baffles' in content:
            start = content.find('baffles')
            print(content[max(0, start-50):min(len(content), start+200)])
        return patches

    baffles_content = baffles_match.group(1)
    print("Debug: Found baffles section. Length:", len(baffles_content))
    
    # Find patches section
    patches_match = re.search(r'patches\s*{(.*?)}(?=\s*[}\n])', baffles_content, re.DOTALL)
    if not patches_match:
        print("Debug: Patches section not found in baffles content")
        print("Debug: Baffles content preview:", baffles_content[:200])
        return patches

    patches_content = patches_match.group(1)
    print("Debug: Found patches section. Length:", len(patches_content))
    
    # Find all patches with p configuration
    patch_sections = re.finditer(r'(\w+)\s*{(?:[^{}]|{(?:[^{}]|{[^{}]*})*})*}', patches_content, re.DOTALL)
    
    for section in patch_sections:
        section_content = section.group(0)
        print(f"Debug: Processing patch section: {section.group(1)}")
        
        # Get patch name
        name_match = re.search(r'name\s+(\w+)', section_content)
        if not name_match:
            continue
            
        patch_name = name_match.group(1)
        print(f"Debug: Found patch name: {patch_name}")
        
        # Look for p configuration
        p_config_match = re.search(r'p\s*{([^}]*)}', section_content, re.DOTALL)
        if not p_config_match:
            continue
            
        config = p_config_match.group(1)
        
        # Find the neighbour patch name
        neighbour_match = re.search(r'neighbourPatch\s+(\w+)', section_content)
        if not neighbour_match:
            continue
            
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
        
        patches[patch_name] = {
            'config': params,
            'neighbour': neighbour_match.group(1)
        }
    
    if not patches:
        print("Debug: No valid patches found after processing")
    else:
        print(f"Debug: Found {len(patches)} valid patches")
    
    return patches

def update_p_file_content(p_content: str, patch_configs: Dict[str, Dict]) -> str:
    """Update the p file content with new patch configurations."""
    new_entries = []
    
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
    processed_pairs = set()
    for patch_name, patch_data in patch_configs.items():
        neighbour_name = patch_data['neighbour']
        pair_key = tuple(sorted([patch_name, neighbour_name]))
        
        if pair_key in processed_pairs:
            continue
            
        entry = f'''    "({patch_name}|{neighbour_name})"
    {{
        type            {patch_data['config'].get('type', 'porousBafflePressure')};
        patchType       {patch_data['config'].get('patchType', 'cyclic')};
        D               {patch_data['config'].get('D', '0')};
        I               {patch_data['config'].get('I', '0')};
        length          {patch_data['config'].get('length', '0')};
        uniformJump     {patch_data['config'].get('uniformJump', 'false')};
        value           {patch_data['config'].get('value', 'uniform 0')};
    }}'''
        new_entries.append(entry)
        processed_pairs.add(pair_key)
    
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
    cwd = os.getcwd()
    source = Path(cwd) / source_path
    target = Path(cwd) / target_path
    
    source_content = read_file(source)
    if not source_content:
        sys.exit(1)
    
    target_content = read_file(target)
    if not target_content:
        sys.exit(1)
    
    patch_configs = extract_master_patches(source_content)
    if not patch_configs:
        print("Error: No patch configurations found in source file")
        sys.exit(1)
    
    new_content = update_p_file_content(target_content, patch_configs)
    
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

