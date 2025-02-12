#!/usr/bin/python

import os
import re
import sys

# Global Variables
PY_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
SKELETON_BOUNDARY_DIR = os.path.join(PY_FILE_PATH, "skeletonsBoundary")
SKELETON_SYSTEM_DIR = os.path.join(PY_FILE_PATH, "skeletonsSystem")
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
                        ('screen', 'baffle'),
                        ('porous', 'baffle'),
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
                                 ('wall', 'zeroGradient')]
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
    output_path = os.path.join(SYSTEM_DIR, "surfaceFeaturesDict.gen")
    skeleton_head_path = os.path.join(SKELETON_SYSTEM_DIR, "surfaceFeaturesHead")
    skeleton_tail_path = os.path.join(SKELETON_SYSTEM_DIR, "surfaceFeaturesTail")
    with open(output_path, 'w') as sfefile:
        # Write the header
        with open(skeleton_head_path) as head:
            sfefile.write(head.read())
        # Write each patch
        print('Detecting the surfaces and features of the following:')
        for patch in patch_names:
            print(f"{patch}.stl")
            sfefile.write(f'    "{patch}.stl"\n')
        # Write the tail
        with open(skeleton_tail_path) as tail:
            sfefile.write(tail.read())


def create_snappy_hex_mesh_dict():
    """Creates the snappyHexMeshDict.gen file."""
    print("Creating snappyHexMeshDict.gen...")
    output_path = os.path.join(SYSTEM_DIR, "snappyHexMeshDict.gen")
    skeleton_head_path = os.path.join(SKELETON_SYSTEM_DIR, "snappyHexMeshHead")
    skeleton_tail_path = os.path.join(SKELETON_SYSTEM_DIR, "snappyHexMeshTail")
    # Write contents of skeleton header
    with open(output_path, 'w') as shm_file, open(skeleton_head_path) as head, open(skeleton_tail_path) as tail:
        shm_file.write(head.read())
        # Write geometry list consisting of .stl files
        for patch in patch_names:
            shm_file.write(f'        {patch}.stl {{type triSurfaceMesh; name {patch}; file "{patch}.stl";}}\n')
        shm_file.write('        // refinementBox {type searchableBox; min (0.0 0.0 0.0); max (1.0 1.0 1.0);}\n')
        shm_file.write('};\n\n')
        # Write blocks for castellated mesh generation
        shm_file.write('// Settings for castellatedMesh generation\n')
        shm_file.write('// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n')
        shm_file.write('castellatedMeshControls\n{\n')
        # Write block for features
        shm_file.write('        features  // OPTIONAL: Refinement of edges (default = {file "name.eMesh"; level 0;}\n')
        shm_file.write('        (\n')
        for patch in patch_names:
            shm_file.write(f'            {{file "{patch}.eMesh"; level 3;}}\n')
        shm_file.write('        );\n\n')
        # Write block for refinement surfaces
        shm_file.write('        refinementSurfaces  // MANDATORY: Definition and refinement of surfaces\n')
        shm_file.write('        { // Refinement levels (min max) are linked to the proximity to a surface\n')
        for patch in patch_names:
            patch_type = get_patch_type_from_patch_name(patch)
            if patch_type == 'baffle':
                shm_file.write(f'            {patch} {{level (0 0); faceZone {patch}Faces; }}\n')
            elif patch_type == 'honeycomb':
                shm_file.write(f'            {patch}\n')
                shm_file.write('                {level (0 0);\n')
                shm_file.write(f'                faceZone {patch}Faces;\n')
                shm_file.write(f'                cellZone {patch}Cells;\n')
                shm_file.write('                cellZoneInside inside;}\n')
            elif patch_type in {'wall', 'slip', 'empty', 'symmetry'}:
                shm_file.write(f'            {patch} {{level (0 0); patchInfo {{type {patch_type};}} }}\n')
            else:
                shm_file.write(f'            {patch} {{level (0 0); patchInfo {{type patch;}} }}\n')
        shm_file.write('        }\n\n')
        # Write contents of skeleton tail
        shm_file.write(tail.read())


def build_zero_file(base_name: str, local_boundary_types: dict, local_boundary_values: dict):
    """Creates a file in the zero directory with grouped patch settings."""
    output_path = os.path.join(ZERO_DIR, base_name)
    skeleton_head_path = os.path.join(SKELETON_BOUNDARY_DIR, f"{base_name}Head")
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
    with open(output_path, 'w') as outfile, open(skeleton_head_path) as head:
        outfile.write(head.read())
        # Write grouped patches using pipe separator
        for patch_type, patches in patch_groups.items():
            # Do not add surfaces associated with baffles or honeycombs as boundaries
            if patch_type in {'baffle', 'honeycomb'}:
                continue
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
