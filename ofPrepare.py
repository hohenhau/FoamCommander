#!/usr/bin/python

import os
import re
import sys
import shutil
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


def copy_files_from_templates():
    set_constraint_types_path = os.path.join(TEMPLATE_CONSTANT_DIR, "setConstraintTypes")
    set_constraint_types_target = os.path.join(CURRENT_DIR, "constant")
    # Copy the setConstraintTypes file from template to the target directory
    try:
        shutil.copy(set_constraint_types_path, set_constraint_types_target)
        print(f"Successfully copied 'setConstraintTypes' to {set_constraint_types_target}")
    except Exception as e:
        print(f"Error copying 'setConstraintTypes': {e}")
        sys.exit(1)


def get_patch_type_from_patch_name(input_patch_name: str):
    """Determine the boundary type based the patch name. Needed for: 0/fields (e.g. 0/U)"""
    # Define the common and additional boundary types (baffle and cellSelector are custom)
    common_patches = ['inlet', 'outlet', 'cyclic', 'empty', 'movingWallVelocity', 'MRFnoSlip', 'slip', 'symmetry']
    common_patch_types = {boundary: boundary for boundary in common_patches}
    common_patch_types['atmosphere'] = 'inletOutlet'
    common_patch_types['mirror'] = 'symmetry'
    common_patch_types['min'] = 'empty'
    common_patch_types['max'] = 'empty'
    common_patch_types['baffle'] = 'baffle'
    common_patch_types['porous'] = 'baffle'
    common_patch_types['screen'] = 'baffle'
    common_patch_types['cellSelector'] = 'cellSelector'
    common_patch_types['honeycomb'] = 'cellSelector'
    common_patch_types['rotating'] = 'rotating'
    # Define types that have overlapping names with the common types
    overlapping_patch_types = {'noSlip': 'noSlip',  # Overlaps with slip
                               'symmetryPlane': 'symmetryPlane',  # Overlaps with symmetry
                               'inletOutlet': 'inletOutlet',  # Overlaps with inlet & outlet
                               'nonRotating': 'movingWallVelocity'}  # Overlaps with rotating
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
    common_boundary_types['wall'] = 'zeroGradient'
    common_boundary_types['movingWallVelocity'] = 'zeroGradient'
    common_boundary_types['MRFnoSlip'] = 'zeroGradient'
    common_boundary_types['baffle'] = 'cyclic'
    common_boundary_types['rotating'] = 'rotating'
    # Define types that have overlapping names with the common types
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
    if 'NCC' in input_patch_name:  # Useful for assigning Non-conformal Coupling surfaces
        boundary_type = 'cyclic'
    return boundary_type


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
    print('Found the following stl files:')
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


def create_create_baffles_dict(patch_names):
    """Creates the createBafflesCyclics.gen file."""
    print("Creating createBafflesCyclics.gen...")
    template_name = 'createBafflesCyclics'
    template_path = os.path.join(TEMPLATE_SYSTEM_DIR, template_name)  # Template file
    output_path = os.path.join(SYSTEM_DIR, f'{template_name}.gen')
    replacement_pattern = r'.*\$CYCLIC_BAFFLES\$.*\n'  # Match any line containing $STL_FILES$
    replacement_text = str()
    for patch in patch_names:
        patch_type = get_patch_type_from_patch_name(patch)
        if patch_type not in {'baffle', 'cyclic'}:
            continue
        print(f'Creating baffle entry for {patch} in system/{template_name}')
        replacement_text += (f'{" " * 4}{patch}Group\n'
                             f'{" " * 4}{{\n'
                             f'{" " * 8}type        faceZone;\n'
                             f'{" " * 8}zoneName    {patch}Faces;\n'
                             f'{" " * 8}patches\n'
                             f'{" " * 8}{{\n'
                             f'{" " * 12}master\n'
                             f'{" " * 12}{{\n'
                             f'{" " * 16}type            cyclic;\n'
                             f'{" " * 16}name            {patch};\n'
                             f'{" " * 16}neighbourPatch  {patch}_slave;\n'
                             f'{" " * 12}}}\n'
                             f'{" " * 12}slave\n'
                             f'{" " * 12}{{\n'
                             f'{" " * 16}type            cyclic;\n'
                             f'{" " * 16}name            {patch}_slave;\n'
                             f'{" " * 16}neighbourPatch  {patch};\n'
                             f'{" " * 12}}}\n'
                             f'{" " * 8}}}\n'
                             f'{" " * 4}}}\n')
    # Define the patterns to match the entire lines containing the variables
    patterns_and_replacements = [(r'.*\$CYCLIC_BAFFLES\$.*\n', replacement_text)]
    # Perform the replacements
    perform_regex_replacements(patterns_and_replacements, template_path, output_path)
    print(f"snappyHexMeshDict.gen created at: {output_path}")


def create_snappy_hex_mesh_dict(patch_names):
    """Creates the snappyHexMeshDict.gen file with proper comment line replacement."""
    print("Creating snappyHexMeshDict.gen...")
    template_path = os.path.join(TEMPLATE_SYSTEM_DIR, "snappyHexMeshDict")
    output_path = os.path.join(SYSTEM_DIR, "snappyHexMeshDict.gen")
    # Prepare replacement blocks
    stl_block, mesh_block, surface_block, layer_block = str(), str(), str(), str()
    for patch in patch_names:
        stl_block += f'{" " * 8}{patch}.stl {{type triSurfaceMesh; name {patch}; file "{patch}.stl";}}\n'
        mesh_block += f'{" " * 12}{{file "{patch}.eMesh"; level 3;}}\n'
        patch_type = get_patch_type_from_patch_name(patch)
        print(f'Matched {patch} with {patch_type}')
        if patch_type == 'baffle':  # Options for faceType are {internal, baffle, and boundary}
            surface_block += f'{" " * 12}{patch} {{level (0 0); faceZone {patch}Faces; faceType internal;}}\n'
            layer_block += f'{" " * 8}{patch}{{nSurfaceLayers 0;}}  // Stops layers from disrupting baffle surface\n'
        elif patch_type == 'cellSelector':
            surface_block += (f'{" " * 12}{patch}\n'
                              f'{" " * 16}{{level (0 0);\n'
                              f'{" " * 16}faceZone {patch}Faces;\n'
                              f'{" " * 16}cellZone {patch}Cells;\n'
                              f'{" " * 16}cellZoneInside inside;}}\n')
        elif patch_type in {'wall', 'patch', 'symmetry', 'symmetryPlane', 'empty', 'cyclic', 'wedge'}:
            surface_block += f'{" " * 12}{patch} {{level (0 0); patchInfo {{type {patch_type};}} }}\n'
        elif patch_type in {'inlet', 'outlet', 'inletOutlet'}:
            surface_block += f'{" " * 12}{patch} {{level (0 0); patchInfo {{type patch;}} }}\n'
        else:
            surface_block += f'{" " * 12}{patch} {{level (0 0); patchInfo {{type wall;}} }}\n'
    # Define the patterns to match the entire lines containing the variables
    patterns_and_replacements = [(r'.*\$STL_FILES_AND_GEOMETRIES\$.*\n', stl_block),
                                 (r'.*\$MESH_FEATURES\$.*\n', mesh_block),
                                 (r'.*\$REFINEMENT_SURFACES\$.*\n', surface_block),
                                 (r'.*\$SURFACE_LAYERS\$.*\n', layer_block)]
    # Perform the replacements
    perform_regex_replacements(patterns_and_replacements, template_path, output_path)
    print(f"snappyHexMeshDict.gen created at: {output_path}")


def build_zero_file(names: list, field: str, local_boundary_types: dict, boundary_vals: dict, internal_val=0):
    """Creates a file in the zero directory with grouped patch settings."""
    template_path = os.path.join(TEMPLATE_BOUNDARY_DIR, f"{field}")
    output_path = os.path.join(ZERO_DIR, field)

    # Ensure there is an entry for walls
    if 'wall' not in local_boundary_types:
        local_boundary_types['wall'] = get_boundary_type_from_patch_name('wall')

    # Copy wall entry to pseudo walls
    for pseudo_wall in ['MRFnoSlip', 'movingWallVelocity', 'rotating']:
        if pseudo_wall not in local_boundary_types:
            local_boundary_types[pseudo_wall] = local_boundary_types['wall']
            if pseudo_wall not in boundary_vals and 'wall' in boundary_vals:
                boundary_vals[pseudo_wall] = boundary_vals['wall']

    # Group patches by type
    patch_groups = {}
    for name in names:
        patch_type = get_patch_type_from_patch_name(name)
        # It the patch type is not specified, get the type
        if patch_type not in local_boundary_types:
            local_boundary_types[patch_type] = get_boundary_type_from_patch_name(name)
        # If this is the first patch of its type, start a group
        if patch_type not in patch_groups:
            patch_groups[patch_type] = []
        patch_groups[patch_type].append(name)
    boundary_block = str()
    # Grouped patches in regex format using pipe separator
    for patch_type, patch_group in patch_groups.items():
        # Do not add surfaces associated with honeycombs or cell selectors as boundaries
        if patch_type in {'cellSelector'}:
            print(f'Not processing {patch_type} as an external boundary or baffle')
            continue
        # Double up cyclic boundaries and baffles
        if patch_type in {'baffle', 'cyclic'}:
            patch_group = [f"{patch}{ending}" for patch in patch_group for ending in ['', '_slave']]
        # Join patches with '|' and wrap in parentheses
        group_name = f'"{patch_group[0]}"' if len(patch_group) == 1 else f'"({"|".join(patch_group)})"'
        # Add the patch text to the text block
        boundary_block += f'    {group_name}\n    {{\n'
        # Take care of the special rotating if statement
        if patch_type in boundary_vals and '$timeScheme' in boundary_vals[patch_type]:
            boundary_block += boundary_vals[patch_type]
            continue
        # Add the patch type and value to the block
        boundary_block += f'        type            {local_boundary_types[patch_type]};\n'
        if patch_type in boundary_vals:
            boundary_block += f'        value           {boundary_vals[patch_type]};\n'
        boundary_block += '    }\n'
        # Define the value block   float('%.*g' % (3, internal_val))
        internal_field_block = f"internalField   uniform {float('%.*g' % (3, internal_val))};  // Adjust to simulation"
        # Define the patterns to match the entire lines containing the variables
        patterns_and_replacements = [(r'.*\$INTERNAL_FIELD\$.*\n', internal_field_block),
                                     (r'.*\$BOUNDARY_FIELDS\$.*\n', boundary_block)]
        # Perform the replacements
        perform_regex_replacements(patterns_and_replacements, template_path, output_path)
        print(f"snappyHexMeshDict.gen created at: {output_path}")


def create_zero_boundaries(names, fm):
    """Build the zero files for the various fields and boundaries"""

    rotating_u_value = (f'{" " * 8}timeScheme      ${{${{FOAM_CASE}} /system/fvSchemes!ddtSchemes/default}};\n'
                        f'{" " * 8}#ifeq $timeScheme steadyState\n'
                        f'{" " * 12}type            MRFnoSlip;\n'
                        f'{" " * 8}#else\n'
                        f'{" " * 12}type            movingWallVelocity;\n'
                        f'{" " * 8}#endif\n'
                        f'{" " * 12}value           uniform (0 0 0);\n'
                        f'{" " * 4}}}\n')

    field_configs = {
        'U': {'types': {'wall': 'fixedValue', 'MRFnoSlip': 'MRFnoSlip', 'movingWallVelocity': 'movingWallVelocity'},
              'values': {'inlet': 'uniform (0 0 0)', 'wall': 'uniform (0 0 0)', 'rotating': rotating_u_value,
                         'movingWallVelocity': 'uniform (0 0 0)'},
              'internal_field': 0},

        'p': {'types': {'inlet': 'zeroGradient', 'outlet': 'fixedValue'},
              'values': {'outlet': 'uniform 0'},
              'internal_field': 0},

        'k': {'types': {'wall': 'kqRWallFunction'},
              'values': {'inlet': '$internalField', 'wall': 'uniform 0'},
              'internal_field': fm.turb_kinetic_energy.value},

        'epsilon': {'types': {'wall': 'epsilonWallFunction'},
                    'values': {'inlet': '$internalField', 'wall': 'uniform 0'},
                    'internal_field': fm.turb_dissipation_rate.value},

        'nut': {'types': {'inlet': 'calculated', 'outlet': 'calculated', 'wall': 'nutUWallFunction'},
                'values': {'inlet': 'uniform 0', 'outlet': 'uniform 0', 'wall': 'uniform 0'},
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

    for field_name, config in field_configs.items():
        build_zero_file(names, field_name, config["types"], config["values"], config["internal_field"])


def prepare_files():
    print(f"Processing directory: {CURRENT_DIR}")
    initialisation()
    copy_files_from_templates()
    patch_names = load_and_process_stl_files()
    create_surface_features_dict(patch_names)
    create_snappy_hex_mesh_dict(patch_names)
    create_create_baffles_dict(patch_names)
    arguments = detect_and_parse_arguments(sys)
    flow_metrics = estimate_internal_fields(arguments)
    create_zero_boundaries(patch_names, flow_metrics)


if __name__ == "__main__":
    prepare_files()

