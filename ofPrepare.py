#!/usr/bin/python

import os
import re
import sys
from ofEstimateInternalFields import estimate_internal_fields
from ofParseArgs import detect_and_parse_arguments

# Global Variables
PY_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_BOUNDARY_DIR = os.path.join(PY_FILE_PATH, "templatesBoundary")
TEMPLATE_SYSTEM_DIR = os.path.join(PY_FILE_PATH, "templatesSystem")
CURRENT_DIR = os.getcwd() 
TRI_SURFACE_DIR = os.path.join(CURRENT_DIR, "constant", "triSurface")
ZERO_DIR = os.path.join(CURRENT_DIR, "0.gen")
SYSTEM_DIR = os.path.join(CURRENT_DIR, "system")


def initialisation():
    # Only run if there is a triSurface directory
    if not os.path.isdir(TRI_SURFACE_DIR):
        print(f"Error: The directory '{TRI_SURFACE_DIR}' does not exist, or is not accessible")
        sys.exit(1)
    # Ensure directories exist
    os.makedirs(ZERO_DIR, exist_ok=True)


def get_patch_type_from_patch_name(input_name: str):
    """Determine the patch type based on keywords in the name."""
    common_types = ['inlet', 'inletOutlet', 'outlet', 'empty', 'symmetry', 'slip', 'cyclicAMI', 'cyclic']
    additional_types = [('mirror', 'symmetry'),
                        ('honeycomb', 'honeycomb'),
                        ('baffle', 'baffle'),
                        ('porous', 'baffle'),
                        ('screen', 'baffle'),
                        ('min', 'empty'),
                        ('max', 'empty'),
                        ('atmosphere', 'inletOutlet')]
    all_types = [(i, i) for i in common_types] + additional_types
    for patch_name, patch_type in all_types:
        if patch_name.lower() in input_name.lower():
            return patch_type
    return 'wall'


def get_boundary_type_from_patch_type(input_type: str):
    """Determine the boundary type based the patch type"""
    common_boundary_types = ['empty', 'symmetry', 'slip', 'cyclicAMI', 'cyclic']
    additional_boundary_types = [('inlet', 'fixedValue'),
                                 ('outlet', 'zeroGradient'),
                                 ('wall', 'zeroGradient'),
                                 ('baffle', 'cyclic')]
    all_types = [(i, i) for i in common_boundary_types] + additional_boundary_types
    for patch_type, boundary_type in all_types:
        if patch_type.lower() in input_type.lower():
            return boundary_type
    return 'zeroGradient'


def load_and_process_stl_files():
    """Processes STL files, renaming and extracting patch names."""
    if not os.path.exists(TRI_SURFACE_DIR) or not os.path.isdir(TRI_SURFACE_DIR):
        print(f"Error: Directory '{TRI_SURFACE_DIR}' does not exist.")
        sys.exit(1)  # Terminate program
    stl_files = [f for f in os.listdir(TRI_SURFACE_DIR) if f.lower().endswith(".stl")]
    if not stl_files:
        print("No STL files found. Exiting...")
        sys.exit(1)  # Terminate program
    patches = list()
    for filename in stl_files:
        filepath = os.path.join(TRI_SURFACE_DIR, filename)
        new_file_name = f'{filename.split(".")[0]}.{filename.split(".")[1].lower()}'
        new_filepath = os.path.join(TRI_SURFACE_DIR, new_file_name)
        patch_name = re.split(r"\.", filename)[0]
        if patch_name not in patches:
            print(f"Match: {patch_name}")
            patches.append(patch_name)
        # Read entire file content
        with open(filepath, 'r') as file:
            content = file.read()
        # Process content
        content = re.sub(r'^solid.*$', f'solid {patch_name}', content, flags=re.MULTILINE)
        content = re.sub(r'^endsolid.*$', f'endsolid {patch_name}', content, flags=re.MULTILINE)
        # Write back to file with lowercase name
        with open(new_filepath, 'w') as file:
            file.write(content)
        # If the original file had a different case, remove it
        if filepath != new_filepath:
            os.remove(filepath)
    return sorted(patches)


def perform_regex_replacements(patterns_and_replacements: list, template_path: str, output_path: str):
    # Read the template file
    with open(template_path, 'r') as template_file:
        content = template_file.read()
    # Perform the replacements
    for pattern, replacement in patterns_and_replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    # Write the updated content
    with open(output_path, 'w') as output_file:
        output_file.write(content)


def create_surface_features_dict(patch_names):
    """Creates the surfaceFeaturesDict.gen file."""
    print("Creating surfaceFeaturesDict.gen...")
    template_path = os.path.join(TEMPLATE_SYSTEM_DIR, "surfaceFeaturesDict")  # Template file
    output_path = os.path.join(SYSTEM_DIR, "surfaceFeaturesDict.gen")
    replacement_pattern = r'.*\$STL_FILES\$.*\n'  # Match any line containing $STL_FILES$
    replacement_text = str()
    for patch in patch_names:
        replacement_text += f'    "{patch}.stl"\n'
    perform_regex_replacements([(replacement_pattern, replacement_text)], template_path, output_path)
    print(f"surfaceFeaturesDict.gen created at: {output_path}")


def create_snappy_hex_mesh_dict(patch_names):
    """Creates the snappyHexMeshDict.gen file with proper comment line replacement."""
    print("Creating snappyHexMeshDict.gen...")
    template_path = os.path.join(TEMPLATE_SYSTEM_DIR, "snappyHexMeshDict")
    output_path = os.path.join(SYSTEM_DIR, "snappyHexMeshDict.gen")
    # Prepare replacement blocks
    stl_block, mesh_block, surface_block, = str(), str(), str()
    for patch in patch_names:
        stl_block += f'{" " * 8}{patch}.stl {{type triSurfaceMesh; name {patch}; file "{patch}.stl";}}\n'
        mesh_block += f'{" " * 12}{{file "{patch}.eMesh"; level 3;}}\n'
        patch_type = get_patch_type_from_patch_name(patch)
        if patch_type == 'baffle':
            surface_block += f'{" " * 12}{patch} {{level (0 0); faceZone {patch}Faces; }}\n'
        elif patch_type == 'honeycomb':
            surface_block += (f'{" " * 12}{patch}\n'
                              f'{" " * 16}{{level (0 0);\n'
                              f'{" " * 16}faceZone {patch}Faces;\n'
                              f'{" " * 16}cellZone {patch}Cells;\n'
                              f'{" " * 16}cellZoneInside inside;}}\n')
        elif patch_type in {'wall', 'slip', 'empty', 'symmetry'}:
            surface_block += f'{" " * 12}{patch} {{level (0 0); patchInfo {{type {patch_type};}} }}\n'
        elif patch_type in {'slip'}:
            surface_block += f'{" " * 12}{patch} {{level (0 0); patchInfo {{type wall;}} }}\n'
        else:
            surface_block += f'{" " * 12}{patch} {{level (0 0); patchInfo {{type patch;}} }}\n'
    # Define the patterns to match the entire lines containing the variables
    patterns_and_replacements = [(r'.*\$STL_FILES_AND_GEOMETRIES\$.*\n', stl_block),
                                 (r'.*\$MESH_FEATURES\$.*\n', mesh_block),
                                 (r'.*\$REFINEMENT_SURFACES\$.*\n', surface_block)]
    # Perform the replacements
    perform_regex_replacements(patterns_and_replacements, template_path, output_path)
    print(f"snappyHexMeshDict.gen created at: {output_path}")


def build_zero_file(names: list, field: str, boundary_types: dict, boundary_vals: dict, internal_val=0):
    """Creates a file in the zero directory with grouped patch settings."""
    template_path = os.path.join(TEMPLATE_BOUNDARY_DIR, f"{field}")
    output_path = os.path.join(ZERO_DIR, field)
    # Group patches by type
    patch_groups = {}
    for name in names:
        patch_type = get_patch_type_from_patch_name(name)
        # Overwrite internal cyclicAMI boundaries (i.e. baffleAMI)
        if 'AMI' in name:
            patch_type = 'cyclicAMI'
        if patch_type not in boundary_types:
            boundary_types[patch_type] = get_boundary_type_from_patch_type(patch_type)
        if patch_type not in patch_groups:
            patch_groups[patch_type] = []
        patch_groups[patch_type].append(name)
    boundary_block = str()
    # Grouped patches in regex format using pipe separator
    for patch_type, patches in patch_groups.items():
        # Do not add surfaces associated with honeycombs as boundaries
        if patch_type == 'honeycomb':
            continue
        # Double up cyclic boundaries and baffles
        if patch_type in {'baffle', 'cyclic'}:
            patches = [f"{patch}{ending}" for patch in patches for ending in [0, 1]]
        # Join patches with '|' and wrap in parentheses
        patch_group = f'"{patches[0]}"' if len(patches) == 1 else f'"({"|".join(patches)})"'
        # Add the patch text to the text block
        boundary_block += f'    {patch_group}\n    {{\n'
        boundary_block += f'        type            {boundary_types.get(patch_type, "wall")};\n'
        if patch_type in boundary_vals:
            boundary_block += f'        value           {boundary_vals[patch_type]};\n'
        boundary_block += '    }\n'
    # Define the value block
    internal_field_block = f'internalField   uniform {internal_val};  // Adjust internal field as necessary'
    # Define the patterns to match the entire lines containing the variables
    patterns_and_replacements = [(r'.*\$INTERNAL_FIELD\$.*\n', internal_field_block),
                                 (r'.*\$BOUNDARY_FIELDS\$.*\n', boundary_block)]
    # Perform the replacements
    perform_regex_replacements(patterns_and_replacements, template_path, output_path)
    print(f"snappyHexMeshDict.gen created at: {output_path}")


def create_zero_boundaries(names, fm):
    """Build the zero files for the various fields and boundaries"""
    
    field_configs = {
        "U": {"types": {"wall": "fixedValue"},
              "values": {"inlet": "uniform (0 0 0)", "wall": "uniform (0 0 0)"},
              "internal_field": 0},
              
        "p": {"types": {"inlet": "zeroGradient", "outlet": "fixedValue"},
              "values": {"outlet": "uniform 0"},
              "internal_field": 0},
              
        "k": {"types": {"wall": "kqRWallFunction"},
              "values": {"inlet": "$internalField", "wall": "uniform 0"},
              "internal_field": fm.turb_kinetic_energy.value},
              
        "epsilon": {"types": {"wall": "epsilonWallFunction"},
                   "values": {"inlet": "$internalField", "wall": "uniform 0"},
                   "internal_field": fm.turb_dissipation_rate.value},
                   
        "nut": {"types": {"inlet": "calculated", "outlet": "calculated", "wall": "nutUWallFunction"},
                "values": {"inlet": "uniform 0", "outlet": "uniform 0", "wall": "uniform 0"},
                "internal_field": fm.turb_viscosity.value},
                
        "nuTilda": {"types": {},
                    "values": {"inlet": "uniform 0"},
                    "internal_field": 0},
                    
        "omega": {"types": {"wall": "omegaWallFunction"},
                 "values": {"inlet": "$internalField", "wall": "uniform 1e5"},  # value for wall needs to be high (1e5 or 1e6)
                 "internal_field": fm.specific_dissipation.value},
                 
        "kl": {"types": {"wall": "fixedValue"},
               "values": {"inlet": "uniform 0", "wall": "uniform 0"},
               "internal_field": 0},
               
        "kt": {"types": {"wall": "fixedValue"},
               "values": {"inlet": "uniform 0", "wall": "uniform 0"},
               "internal_field": 0},
               
        "p_rgh": {"types": {"inlet": "fixedFluxPressure", "outlet": "fixedFluxPressure",
                           "wall": "fixedFluxPressure", "inletOutlet": "totalPressure"},
                 "values": {"inlet": "uniform 0", "outlet": "uniform 0",
                           "wall": "uniform 0", "inletOutlet": "uniform 0"},
                 "internal_field": 0},
                 
        "alphawatergen": {"types": {"inletOutlet": "inletOutlet"},
                         "values": {"inlet": "uniform 1", "outlet": "uniform 0", "inletOutlet": "uniform 0"},
                         "internal_field": 0}
    }

    for field_name, config in field_configs.items():
        build_zero_file(names, field_name, config["types"], config["values"], config["internal_field"])


def prepare_files():
    print(f"Processing directory: {CURRENT_DIR}")
    initialisation()
    patch_names = load_and_process_stl_files()
    create_surface_features_dict(patch_names)
    create_snappy_hex_mesh_dict(patch_names)
    arguments = detect_and_parse_arguments(sys)
    flow_metrics = estimate_internal_fields(arguments)
    create_zero_boundaries(patch_names, flow_metrics)


if __name__ == "__main__":
    prepare_files()
