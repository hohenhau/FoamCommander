#!/usr/bin/python

import os
import re
import sys

# Global Variables
PY_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_BOUNDARY_DIR = os.path.join(PY_FILE_PATH, "templatesBoundary")
TEMPLATE_SYSTEM_DIR = os.path.join(PY_FILE_PATH, "templatesSystem")
CURRENT_DIR = os.getcwd() if len(sys.argv) == 1 else sys.argv[-1]
TRI_SURFACE_DIR = os.path.join(CURRENT_DIR, "constant", "triSurface")
ZERO_DIR = os.path.join(CURRENT_DIR, "0.gen")
SYSTEM_DIR = os.path.join(CURRENT_DIR, "system")

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
        if get_patch_type_from_patch_name(patch_name) != "screen" and patch_name not in patches:
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


def create_surface_features_dict():
    """Creates the surfaceFeaturesDict.gen file."""
    print("Creating surfaceFeaturesDict.gen...")
    template_path = os.path.join(TEMPLATE_SYSTEM_DIR, "surfaceFeaturesDict")  # Template file
    output_path = os.path.join(SYSTEM_DIR, "surfaceFeaturesDict.gen")
    replacement_pattern = r'^\s*\$STL_FILES\$.*$'
    replacement_text = '\n'
    for patch in patch_names:
        replacement_text += f'    "{patch}.stl"\n'
    with open(template_path, 'r') as template_file, open(output_path, 'w') as output_file:
        updated_content = template_file.read()
        updated_content = re.sub(replacement_pattern, replacement_text, updated_content, flags=re.MULTILINE)
        output_file.write(updated_content)
    print(f"snappyHexMeshDict.gen created at: {output_path}")


def create_snappy_hex_mesh_dict():
    """Creates the snappyHexMeshDict.gen file."""
    print("Creating snappyHexMeshDict.gen...")
    template_path = os.path.join(TEMPLATE_SYSTEM_DIR, "snappyHexMeshDict")  # Template file
    output_path = os.path.join(SYSTEM_DIR, "snappyHexMeshDict.gen")
    stl_block, surface_block, mesh_block = '\n', '\n', '\n'
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
        else:
            surface_block += f'{" " * 12}{patch} {{level (0 0); patchInfo {{type patch;}} }}\n'
    replacements = [(stl_block.rstrip(), r'^\s*\$STL_FILES_AND_GEOMETRIES\$.*$'),
                    (mesh_block.rstrip(), r'^\s*\$MESH_FEATURES\$.*$'),
                    (surface_block.rstrip(), r'^\s*\$REFINEMENT_SURFACES\$.*$')]
    with open(template_path, 'r') as template_file, open(output_path, 'w') as output_file:
        updated_content = template_file.read()
        for replacement_text, pattern in replacements:
            updated_content = re.sub(pattern, replacement_text, updated_content, flags=re.MULTILINE)
        output_file.write(updated_content)
    print(f"snappyHexMeshDict.gen created at: {output_path}")


def build_zero_file(base_name: str, local_boundary_types: dict, local_boundary_values: dict):
    """Creates a file in the zero directory with grouped patch settings."""
    output_path = os.path.join(ZERO_DIR, base_name)
    template_head_path = os.path.join(TEMPLATE_BOUNDARY_DIR, f"{base_name}Head")
    # Group patches by type
    patch_groups = {}
    for patch_name in patch_names:
        patch_type = get_patch_type_from_patch_name(patch_name)
        if patch_type not in local_boundary_types:
            local_boundary_types[patch_type] = get_boundary_type_from_patch_type(patch_type)
        if patch_type not in patch_groups:
            patch_groups[patch_type] = []
        patch_groups[patch_type].append(patch_name)
    # Write the header
    with open(output_path, 'w') as outfile, open(template_head_path) as head:
        outfile.write(head.read())
        # Write grouped patches using pipe separator
        for patch_type, patches in patch_groups.items():
            # Do not add surfaces associated with baffles or honeycombs as boundaries
            if patch_type == 'honeycomb':
                continue
            if patch_type in {'baffle', 'cyclic'}:
                patches = [f"{char}{i}" for char in patches for i in [0, 1]]
            # Join patches with '|' and wrap in parentheses
            patch_group = f'"{patches[0]}"' if len(patches) == 1 else f'"({"|".join(patches)})"'
            outfile.write(f'    {patch_group}\n    {{\n')
            outfile.write(f'        type            {local_boundary_types.get(patch_type, "wall")};\n')
            if patch_type in local_boundary_values:
                outfile.write(f'        value           {local_boundary_values[patch_type]};\n')
            outfile.write('    }\n')
        outfile.write('    "(minX|maxX|minY|maxY|minZ|maxZ)"\n')
        outfile.write('    {\n        type            zeroGradient;\n    }\n')
        outfile.write('}\n')


def create_zero_files():
    """Build the zero files for the various fields and boundaries"""
    # Initial conditions U (velocity)
    u_boundary_types = {"wall": "fixedValue"}
    u_boundary_values = {"inlet": "uniform (0 0 0)", "wall": "uniform (0 0 0)"}
    build_zero_file("U", u_boundary_types, u_boundary_values)

    # Initial conditions for p (pressure)
    p_boundary_types = {"inlet": "zeroGradient",
                        "outlet": "fixedValue"}
    p_boundary_values = {"outlet": "uniform 0"}
    build_zero_file("p", p_boundary_types, p_boundary_values)

    # Initial conditions for k (turbulent kinetic energy) used in k-ε, k-ω, and LES models
    k_boundary_types = {"wall": "kqRWallFunction"}
    k_boundary_values = {"inlet": "uniform 0.05", "wall": "uniform 0.05"}
    build_zero_file("k", k_boundary_types, k_boundary_values)

    # Initial conditions for ε (rate of dissipation of turbulent kinetic energy) used in k-ε models
    epsilon_boundary_types = {"wall": "epsilonWallFunction"}
    epsilon_boundary_values = {"inlet": "uniform 2.7", "wall": "uniform 2.7"}
    build_zero_file("epsilon", epsilon_boundary_types, epsilon_boundary_values)

    # Initial conditions nu_t (turbulent kinematic viscosity) used in k-ε, k-ω, Spalart-Allmaras, and LES models
    nut_boundary_types = {"inlet": "calculated",
                          "outlet": "calculated",
                          "wall": "nutUWallFunction"}
    nut_boundary_values = {"inlet": "uniform 0", "outlet": "uniform 0", "wall": "uniform 0"}
    build_zero_file("nut", nut_boundary_types, nut_boundary_values)

    # Initial conditions for nu_tilda (turbulent kinematic viscosity) used Spalart-Allmaras models
    nuTilda_boundary_types = {}
    nuTilda_boundary_values = {"inlet": "uniform 0"}
    build_zero_file("nuTilda", nuTilda_boundary_types, nuTilda_boundary_values)

    # Initial conditions for ω (specific turbulence dissipation rate) used in k-ω turbulence models
    omega_boundary_types = {}
    omega_boundary_values = {"inlet": "$internalField"}
    build_zero_file("omega", omega_boundary_types, omega_boundary_values)

    # Initial conditions for kl (Turbulent Kinetic Energy per Unit Mass) used low-Re-number models or LES hybrid models
    kl_boundary_types = {"wall": "fixedValue"}
    kl_boundary_values = {"inlet": "uniform 0", "wall": "uniform 0"}
    build_zero_file("kl", kl_boundary_types, kl_boundary_values)

    # Initial conditions for kt (Turbulent Thermal Energy) used in Turbulent heat transfer modeling (HVAC, combustion)
    kt_boundary_types = {"wall": "fixedValue"}
    kt_boundary_values = {"inlet": "uniform 0", "wall": "uniform 0"}
    build_zero_file("kt", kt_boundary_types, kt_boundary_values)

    # Initial conditions for p_rgh (pressure considering gravity and buoyancy) used in multiphase simulations
    p_rgh_boundary_types = {"inlet": "fixedFluxPressure",
                            "outlet": "fixedFluxPressure",
                            "wall": "fixedFluxPressure",
                            "inletOutlet": "totalPressure"}
    p_rgh_boundary_values = {"inlet": "uniform 0", "outlet": "uniform 0", "wall": "uniform 0",
                             "inletOutlet": "uniform 0"}
    build_zero_file("p_rgh", p_rgh_boundary_types, p_rgh_boundary_values)

    # Initial conditions for alpha.water (volumetric fraction of water) used in multiphase simulations
    # The new 0 file is in alpha.watergen - when using in simulation make sure to copy over to new file "alpha.water"
    # The "alpha.water" file is changed during simulations so the "alpha.watergen" file is retained to run future sims
    alpha_water_type_dict = {"inletOutlet": "inletOutlet"}
    alpha_water_value_dict = {"inlet": "uniform 1", "outlet": "uniform 0", "inletOutlet": "uniform 0"}
    build_zero_file("alphawatergen", alpha_water_type_dict, alpha_water_value_dict)


if __name__ == "__main__":
    print(f"Processing directory: {CURRENT_DIR}")
    patch_names = load_and_process_stl_files()
    create_surface_features_dict()
    create_snappy_hex_mesh_dict()
    create_zero_files()
