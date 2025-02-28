#!/usr/bin/python

import os
import re
import sys
from ofEstimateInternalFields import estimate_internal_fields
from ofParseArgs import detect_and_parse_arguments

# Global Variables
PY_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_BOUNDARY_DIR = os.path.join(PY_FILE_PATH, "templatesBoundary")
TEMPLATE_CONSTANT_DIR = os.path.join(PY_FILE_PATH, "templatesConstant")
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


def get_patch_type_from_patch_name(input_patch_name: str):
    """Determine the boundary type based the patch name. Needed for: 0/fields (e.g. 0/U)"""
    # Define the common and additional boundary types
    common_patches = ['inlet', 'outlet', 'cyclic', 'empty', 'movingWallVelocity', 'MRFnoSlip', 'slip', 'symmetry']
    common_patch_types = {boundary: boundary for boundary in common_patches}
    common_patch_types['atmosphere'] = 'inletOutlet'
    common_patch_types['mirror'] = 'symmetry'
    common_patch_types['min'] = 'empty'
    common_patch_types['max'] = 'empty'
    common_patch_types['baffle'] = 'baffle'
    common_patch_types['internal'] = 'internal'
    common_patch_types['porous'] = 'internal'
    common_patch_types['screen'] = 'internal'
    common_patch_types['rotating'] = 'rotating'
    common_patch_types['stationary'] = 'movingWallVelocity'
    common_patch_types['NCC'] = 'NCC'
    # Define types that have overlapping patch_names with the common types
    overlapping_patch_types = {'noSlip': 'noSlip',  # Overlaps with slip
                               'symmetryPlane': 'symmetryPlane',  # Overlaps with symmetry
                               'inletOutlet': 'inletOutlet'}  # Overlaps with inlet & outlet
    # Convert all KEYS to lower case
    common_patch_types = {key.lower(): value for key, value in common_patch_types.items()}
    overlapping_patch_types = {key.lower(): value for key, value in overlapping_patch_types.items()}
    # Match the patch name to a type (first try common, then overlapping types)
    input_patch_name_lower = input_patch_name.lower()
    patch_type = 'wall'
    for dictionary in [common_patch_types, overlapping_patch_types]:
        for key, value in dictionary.items():
            if key in input_patch_name_lower:
                patch_type = value
                break
    return patch_type


def get_boundary_type_from_patch_name(input_patch_name: str):
    """Determine the boundary type based the patch name. Needed for: 0/fields (e.g. 0/U)"""
    # Define the common and additional boundary types
    common_boundaries = ['cyclic', 'empty', 'movingWallVelocity', 'MRFnoSlip', 'slip', 'symmetry']
    common_boundary_types = {boundary: boundary for boundary in common_boundaries}
    common_boundary_types['inlet'] = 'fixedValue'
    common_boundary_types['outlet'] = 'zeroGradient'
    common_boundary_types['NCC'] = 'zeroGradient'
    common_boundary_types['wall'] = 'zeroGradient'
    common_boundary_types['movingWallVelocity'] = 'zeroGradient'
    common_boundary_types['MRFnoSlip'] = 'zeroGradient'
    common_boundary_types['baffle'] = 'zeroGradient'
    common_boundary_types['internal'] = 'cyclic'
    common_boundary_types['rotating'] = 'rotating'
    # Define types that have overlapping patch_names with the common types
    overlapping_boundary_types = {'noSlip': 'noSlip',  # Overlaps with slip
                                  'symmetryPlane': 'symmetryPlane',  # Overlaps with symmetry
                                  'inletOutlet': 'inletOutlet'}  # Overlaps with inlet & outlet
    # Convert all KEYS to lower case
    common_boundary_types = {key.lower(): value for key, value in common_boundary_types.items()}
    overlapping_boundary_types = {key.lower(): value for key, value in overlapping_boundary_types.items()}
    # Retrieve the patch type from the name and set default boundary type
    input_patch_type = get_patch_type_from_patch_name(input_patch_name)
    boundary_type = 'zeroGradient'
    for dictionary in [common_boundary_types, overlapping_boundary_types]:
        if input_patch_type.lower() in dictionary:
            boundary_type = dictionary[input_patch_type.lower()]
    return boundary_type


def load_and_process_stl_files():
    """Processes STL files, renaming and extracting patch patch_names."""
    if not os.path.exists(TRI_SURFACE_DIR) or not os.path.isdir(TRI_SURFACE_DIR):
        print(f"Error: Directory '{TRI_SURFACE_DIR}' does not exist.")
        sys.exit(1)  # Terminate program
    stl_files = [f for f in os.listdir(TRI_SURFACE_DIR) if f.lower().endswith(".stl")]
    if not stl_files:
        print("No STL files found. Exiting...")
        sys.exit(1)  # Terminate program
    patches = list()
    print('\nLoading and processing the following .stl files:')
    for filename in stl_files:
        filepath = os.path.join(TRI_SURFACE_DIR, filename)
        new_file_name = f'{filename.split(".")[0]}.{filename.split(".")[1].lower()}'
        new_filepath = os.path.join(TRI_SURFACE_DIR, new_file_name)
        patch_name = re.split(r"\.", filename)[0]
        if patch_name not in patches:
            print(f"- {patch_name}")
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


def replace_snappy_hex_mesh_dict(patch_names):
    """Function to find the replacement pattern and text for a specific template"""
    stl_block, mesh_block, surface_block, layer_block = str(), str(), str(), str()
    for name in patch_names:
        stl_block += f'{" " * 8}{name}.stl {{type triSurfaceMesh; name {name}; file "{name}.stl";}}\n'
        mesh_block += f'{" " * 12}{{file "{name}.eMesh"; level 3;}}\n'
        # Check if the patch is actually a zone and process it as such (includes NCC zones!)
        if 'zone' in name.lower() or 'region' in name.lower() or 'honeycomb' in name.lower():
            surface_block += (f'{" " * 12}{name}\n'
                              f'{" " * 16}{{level (0 0);\n'
                              f'{" " * 16}faceZone {name}Faces;\n'
                              f'{" " * 16}cellZone {name}Cells;\n'
                              f'{" " * 16}cellZoneInside inside;}}\n')
            continue
        patch_type = get_patch_type_from_patch_name(name)
        print(f'Matched {name} with {patch_type}')
        if patch_type in {'baffle', 'internal'}:  # faceType options are {internal, baffle, and boundary}
            surface_block += f'{" " * 12}{name} {{level (0 0); faceZone {name}Faces; faceType {patch_type};}}\n'
            layer_block += f'{" " * 8}{name}{{nSurfaceLayers 0;}}  // Stops layers from disrupting baffle surface\n'
        elif patch_type in {'wall', 'patch', 'symmetry', 'symmetryPlane', 'empty', 'cyclic', 'wedge'}:
            surface_block += f'{" " * 12}{name} {{level (0 0); patchInfo {{type {patch_type};}} }}\n'
        elif patch_type in {'inlet', 'outlet', 'inletOutlet', 'NCC'}:
            surface_block += f'{" " * 12}{name} {{level (0 0); patchInfo {{type patch;}} }}\n'
        else:
            surface_block += f'{" " * 12}{name} {{level (0 0); patchInfo {{type wall;}} }}\n'
    # Define the patterns to match the entire lines containing the variables
    patterns_and_replacements = [(r'.*\$STL_FILES_AND_GEOMETRIES\$.*\n', stl_block),
                                 (r'.*\$MESH_FEATURES\$.*\n', mesh_block),
                                 (r'.*\$REFINEMENT_SURFACES\$.*\n', surface_block),
                                 (r'.*\$SURFACE_LAYERS\$.*\n', layer_block)]
    return patterns_and_replacements


def replace_create_baffles_dict(patch_names):
    """Function to find the replacement pattern and text for a specific template"""
    replacement_text = str()
    for patch_name in patch_names:
        patch_type = get_patch_type_from_patch_name(patch_name)
        if patch_type not in {'baffle', 'internal', 'cyclic', 'NCC'}:
            continue
        baffle_type = 'patch' if patch_type == 'NCC' else 'cyclic'
        replacement_text += (f'{" " * 4}{patch_name}Group\n'
                             f'{" " * 4}{{\n'
                             f'{" " * 8}type        faceZone;\n'
                             f'{" " * 8}zoneName    {patch_name}Faces;\n'
                             f'{" " * 8}patches\n'
                             f'{" " * 8}{{\n'
                             f'{" " * 12}master\n'
                             f'{" " * 12}{{\n'
                             f'{" " * 16}type            {baffle_type};\n'
                             f'{" " * 16}name            {patch_name};\n'
                             f'{" " * 16}neighbourPatch  {patch_name}_slave;\n'
                             f'{" " * 12}}}\n'
                             f'{" " * 12}slave\n'
                             f'{" " * 12}{{\n'
                             f'{" " * 16}type            {baffle_type};\n'
                             f'{" " * 16}name            {patch_name}_slave;\n'
                             f'{" " * 16}neighbourPatch  {patch_name};\n'
                             f'{" " * 12}}}\n'
                             f'{" " * 8}}}\n'
                             f'{" " * 4}}}\n')
    # Bundle the replacement text and pattern
    replacement_pattern = r'.*\$BAFFLE_DEFINITIONS\$.*\n'
    return [(replacement_pattern, replacement_text)]


def replace_surface_features_dict(patch_names):
    """Function to find the replacement pattern and text for a specific template"""
    replacement_text = str()
    for patch in patch_names:
        replacement_text += f'    "{patch}.stl"\n'
    # Bundle the replacement text and pattern
    replacement_pattern = r'.*\$STL_FILES\$.*\n'
    return [(replacement_pattern, replacement_text)]


def replace_create_ncc_dict(patch_names):
    """Function to find the replacement pattern and text for a specific template"""
    replacement_text = str()
    for patch_name in patch_names:
        if 'NCC' not in patch_name.upper():
            continue
        replacement_text += (f'{" " * 4}{patch_name}_Group\n'
                             f'{" " * 4}{{\n'
                             f'{" " * 8}patches         ({patch_name} {patch_name}_slave);\n'
                             f'{" " * 8}transform       none;  // Options {{none, rotational, & translational}}\n'
                             f'{" " * 4}}}\n')
    # Bundle the replacement text and pattern
    replacement_pattern = r'.*\$NCC_DEFINITIONS\$.*\n'
    return [(replacement_pattern, replacement_text)]


def replace_zero_boundaries(patch_names, boundary_types, boundary_values, internal_field):
    """Function to find the replacement pattern and text for a specific template"""

    # Group patches by type
    patch_groups = {}
    for patch_name in patch_names:
        patch_type = get_patch_type_from_patch_name(patch_name)
        # It the patch type is not specified, get the type
        if patch_type not in boundary_types:
            boundary_types[patch_type] = get_boundary_type_from_patch_name(patch_name)
        # If this is the first patch of its type, start a group
        if patch_type not in patch_groups:
            patch_groups[patch_type] = []
        patch_groups[patch_type].append(patch_name)

    boundary_block = str()
    for patch_type, patch_group in patch_groups.items():
        # Double up cyclic boundaries, baffles, and NCCs
        if patch_type in {'baffle', 'cyclic', 'NCC'}:
            patch_group = [f"{patch}{ending}" for patch in patch_group for ending in ['', '_slave']]
        # Join patches with '|' and wrap in parentheses
        group_name = f'"{patch_group[0]}"' if len(patch_group) == 1 else f'"({"|".join(patch_group)})"'
        # Add the patch text to the text block
        boundary_block += f'    {group_name}\n    {{\n'
        # Take care of special if-statement based types and values
        if '#ifeq' in boundary_types[patch_type]:
            boundary_block += boundary_types[patch_type]
            continue
        # Add the patch type and value to the block
        boundary_block += f'        type            {boundary_types[patch_type]};\n'
        if patch_type in boundary_values:
            boundary_block += f'        value           {boundary_values[patch_type]};\n'
        boundary_block += '    }\n'
        # Define the value block   float('%.*g' % (3, internal_field))
        internal_field_block = f"internalField   uniform {float('%.*g' % (3, internal_field))}; // Adjust to simulation"
        # Define the patterns to match the entire lines containing the variables
        patterns_and_replacements = [(r'.*\$INTERNAL_FIELD\$.*\n', internal_field_block),
                                     (r'.*\$BOUNDARY_FIELDS\$.*\n', boundary_block)]
        return patterns_and_replacements


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


def generate_dict(patch_names, template_name, template_dir, output_name, output_dir, replace_function):
    """Create various dict.gen files"""
    template_path = os.path.join(template_dir, template_name)  # Template file
    output_path = os.path.join(output_dir, output_name)
    print(f"\nCreating system/{output_name}...")
    patterns_and_replacements = replace_function(patch_names)
    perform_regex_replacements(patterns_and_replacements, template_path, output_path)
    print(f"{output_name} created at: {output_path}")


def generate_zero_file(patch_names: list, field: str, boundary_dict: dict):
    """Creates a file in the zero directory with grouped patch settings."""
    template_path = os.path.join(TEMPLATE_BOUNDARY_DIR, f"{field}")
    output_path = os.path.join(ZERO_DIR, field)
    boundary_types = boundary_dict['types']
    boundary_vals = boundary_dict['values']
    internal_field = boundary_dict['internal_field']

    # Ensure there is an entry for walls
    if 'wall' not in boundary_types:
        boundary_types['wall'] = get_boundary_type_from_patch_name('wall')

    # Copy wall entry to pseudo walls
    for pseudo_wall in ['MRFnoSlip', 'movingWallVelocity', 'rotating']:
        if pseudo_wall not in boundary_types:
            boundary_types[pseudo_wall] = boundary_types['wall']
            if pseudo_wall not in boundary_vals and 'wall' in boundary_vals:
                boundary_vals[pseudo_wall] = boundary_vals['wall']

    # Filter out any "patches" that are actually regions, but are not an NCC region
    excluded = ('zone', 'region', 'honeycomb')
    filtered_names = [i for i in patch_names if 'ncc' in i.lower() or not any(word in i.lower() for word in excluded)]

    patterns_and_replacements = replace_zero_boundaries(filtered_names, boundary_types, boundary_vals, internal_field)
    perform_regex_replacements(patterns_and_replacements, template_path, output_path)
    print(f"Field {field} created at: {output_path}")


def generate_all_zero_file(patch_names, fm):
    """Build the zero files for the various fields and boundaries"""

    rotating_u_types = (f'{" " * 8}#include "../system/fvSchemes"\n'
                        f'{" " * 8}#ifeq $ddtSchemes.default steadyState\n'
                        f'{" " * 12}type        MRFnoSlip;\n'
                        f'{" " * 8}#else\n'
                        f'{" " * 12}type        movingWallVelocity;\n'
                        f'{" " * 12}value       uniform (0 0 0);\n'
                        f'{" " * 8}#endif\n'
                        f'{" " * 4}}}\n')

    field_dicts = {
        'U': {'types': {'wall': 'fixedValue', 'MRFnoSlip': 'MRFnoSlip', 'movingWallVelocity': 'movingWallVelocity',
                        'NCC': 'movingWallSlipVelocity', 'rotating': rotating_u_types},
              'values': {'inlet': 'uniform (0 0 0)', 'wall': 'uniform (0 0 0)',
                         'movingWallVelocity': 'uniform (0 0 0)', 'NCC': 'uniform (0 0 0)'},
              'internal_field': 0},

        'p': {'types': {'inlet': 'zeroGradient', 'outlet': 'fixedValue'},
              'values': {'outlet': '$internalField'},
              'internal_field': 0},

        'epsilon': {'types': {'wall': 'epsilonWallFunction'},
                    'values': {'inlet': '$internalField', 'wall': '$internalField'},
                    'internal_field': fm.turb_dissipation_rate.value},

        'k': {'types': {'wall': 'kqRWallFunction'},
              'values': {'inlet': '$internalField', 'wall': '$internalField'},
              'internal_field': fm.turb_kinetic_energy.value},

        'nut': {'types': {'inlet': 'calculated', 'outlet': 'calculated', 'NCC': 'calculated',
                          'wall': 'nutUWallFunction'},
                'values': {'inlet': '$internalField', 'outlet': '$internalField', 'NCC': '$internalField',
                           'wall': '$internalField'},
                'internal_field': fm.turb_viscosity.value},

        'nuTilda': {'types': {},
                    'values': {'inlet': 'uniform 0'},
                    'internal_field': 0},

        'omega': {'types': {'wall': 'epsilonWallFunction'},
                  'values': {'inlet': '$internalField', 'wall': 'uniform 1e5'},
                  # value for wall needs to be high (1e5 or 1e6)
                  'internal_field': fm.specific_dissipation.value},

        'kl': {'types': {'wall': 'fixedValue'},
               'values': {'inlet': 'uniform 0', 'wall': 'uniform 0'},
               'internal_field': 0},

        'kt': {'types': {'wall': 'fixedValue'},
               'values': {'inlet': 'uniform 0', 'wall': 'uniform 0'},
               'internal_field': 0},

        'p_rgh': {'types': {'inlet': 'fixedFluxPressure', 'outlet': 'fixedFluxPressure',
                            'wall': 'fixedFluxPressure', 'inletOutlet': 'totalPressure'},
                  'values': {'inlet': 'uniform 0', 'outlet': 'uniform 0',
                             'wall': 'uniform 0', 'inletOutlet': 'uniform 0'},
                  'internal_field': 0},

        'alphawatergen': {'types': {'inletOutlet': 'inletOutlet'},
                          'values': {'inlet': 'uniform 1', 'outlet': 'uniform 0', 'inletOutlet': 'uniform 0'},
                          'internal_field': 0}
    }

    for field_name, field_dict in field_dicts.items():
        generate_zero_file(patch_names, field_name, field_dict)


if __name__ == "__main__":
    print(f"\nPreparing case in directory: {CURRENT_DIR}")
    initialisation()
    patch_names = load_and_process_stl_files()

    generate_dict(patch_names, 'snappyHexMeshTemplate', TEMPLATE_SYSTEM_DIR,
                  'snappyHexMeshDict', SYSTEM_DIR, replace_snappy_hex_mesh_dict)

    generate_dict(patch_names, 'surfaceFeaturesTemplate', TEMPLATE_SYSTEM_DIR,
                  'surfaceFeaturesDict', SYSTEM_DIR, replace_surface_features_dict)

    generate_dict(patch_names, 'createBafflesTemplate', TEMPLATE_SYSTEM_DIR,
                  'createBafflesDict', SYSTEM_DIR, replace_create_baffles_dict)

    generate_dict(patch_names, 'createNonConformalCouplesTemplate', TEMPLATE_SYSTEM_DIR,
                  'createNonConformalCouplesDict', SYSTEM_DIR, replace_create_ncc_dict)

    arguments = detect_and_parse_arguments(sys)
    flow_metrics = estimate_internal_fields(arguments)
    generate_all_zero_file(patch_names, flow_metrics)
