#!/usr/bin/python

import os
import re
import sys

# Global Variables
PY_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
SKELETON_DIR = os.path.join(PY_FILE_PATH, "skeletons")
CURRENT_DIR = os.getcwd() if len(sys.argv) == 1 else sys.argv[-1]
TRI_SURFACE_DIR = os.path.join(CURRENT_DIR, "constant", "triSurface")
ZERO_DIR = os.path.join(CURRENT_DIR, "0.gen")
SYSTEM_DIR = os.path.join(CURRENT_DIR, "system")

# Ensure directories exist
os.makedirs(ZERO_DIR, exist_ok=True)


def get_patch_type_for_meshing(input_name: str):
    """Determine the patch type based on keywords in the name."""
    patch_mappings = {
        'symmetry': 'symmetry',
        'mirror': 'symmetry',
        'screen': 'screen',
        'baffle': 'screen',
        'inlet': 'inlet',
        'outlet': 'outlet',
        'min': 'empty',
        'max': 'empty',
        'slip': 'slip',
        'atmosphere': 'inletOutlet',
        'cyclicAMI': 'cyclicAMI',
        'porous': 'cyclic',
        'cyclic': 'cyclic'}
    for patch_name, patch_type in patch_mappings.items():
        if patch_name.lower() in input_name.lower():
            return patch_type
    return 'wall'


def build_zero_file(base_name: str, types: dict, values: dict):
    """Creates a file in the zero directory with grouped patch settings."""
    output_path = os.path.join(ZERO_DIR, base_name)
    skeleton_head_path = os.path.join(SKELETON_DIR, f"{base_name}Head")

    # Ensure common patch types exist
    types['cyclic'] = 'cyclic'
    types['cyclicAMI'] = 'cyclicAMI'
    types['empty'] = 'empty'
    types['slip'] = 'slip'
    types['symmetry'] = 'symmetry'

    # Group patches by type
    patch_groups = {}
    for patch in patch_names:
        patch_type = get_patch_type_for_meshing(patch)
        if patch_type not in patch_groups:
            patch_groups[patch_type] = []
        patch_groups[patch_type].append(patch)

    # Write the header
    with open(output_path, 'w') as outfile, open(skeleton_head_path) as head:
        outfile.write(head.read())
        # Write grouped patches using pipe separator
        for patch_type, patches in patch_groups.items():
            # Join patches with '|' and wrap in parentheses
            patch_group = f'"{patches[0]}"' if len(patches) == 1 else f'"({"|".join(patches)})"'
            outfile.write(f'    {patch_group}\n    {{\n')
            outfile.write(f'        type            {types.get(patch_type, "wall")};\n')
            if patch_type in values:
                outfile.write(f'        value           {values[patch_type]};\n')
            outfile.write('    }\n')
        outfile.write('    "(minX|maxX|minY|maxY|minZ|maxZ)"\n')
        outfile.write('    {\n        type            empty;\n    }\n')
        outfile.write('}\n')


def process_stl_files():
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
        if get_patch_type_for_meshing(patch_name) != "screen" and patch_name not in patches:
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
    return patches


def create_surface_features_dict():
    """Creates the surfaceFeaturesDict.gen file."""
    output_path = os.path.join(SYSTEM_DIR, "surfaceFeaturesDict.gen")
    skeleton_head_path = os.path.join(SKELETON_DIR, "surfaceFeaturesHead")
    skeleton_tail_path = os.path.join(SKELETON_DIR, "surfaceFeaturesTail")
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
    output_path = os.path.join(SYSTEM_DIR, "snappyHexMeshDict.gen")
    skeleton_head_path = os.path.join(SKELETON_DIR, "snappyHexMeshHead")
    skeleton_tail_path = os.path.join(SKELETON_DIR, "snappyHexMeshTail")

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
        shm_file.write('        refinementSurfaces  // MANDATORY: Definition and refinement of surfaces\n        {\n')
        for patch in patch_names:
            patch_type = get_patch_type_for_meshing(patch)
            patch_type = 'patch' if patch_type in {'inlet', 'outlet', 'slip', 'cyclic'} else patch_type
            shm_file.write(f'            {patch} {{level (0 0); patchInfo {{type {patch_type};}} }}\n')
        # Write example layout of honeycomb
        shm_file.write('            // honeycombExample\n')
        shm_file.write('            //    {level (4 4);\n')
        shm_file.write('            //    faceZone honeycombFacesA;\n')
        shm_file.write('            //    cellZone honeycombCellsA;\n')
        shm_file.write('            //    cellZoneInside inside;}\n')
        shm_file.write('        }\n\n')

        # Write contents of skeleton tail
        shm_file.write(tail.read())


if __name__ == "__main__":
    print(f"Processing directory: {CURRENT_DIR}")
    patch_names = process_stl_files()

    print("Creating surfaceFeatureExtractDict...")
    create_surface_features_dict()

    print("Creating snappyHexMeshDict...")
    create_snappy_hex_mesh_dict()

    # Initial conditions U (velocity)
    UTypeDict = {"inlet": "fixedValue",
                 "outlet": "zeroGradient",
                 "wall": "fixedValue"}
    UValueDict = {"inlet": "uniform (0 0 0)", "wall": "uniform (0 0 0)"}
    build_zero_file("U", UTypeDict, UValueDict)

    # Initial conditions for p (pressure)
    pTypeDict = {"inlet": "zeroGradient",
                 "outlet": "fixedValue",
                 "wall": "zeroGradient"}
    pValueDict = {"outlet": "uniform 103"}
    build_zero_file("p", pTypeDict, pValueDict)

    # Initial conditions for k (turbulent kinetic energy) used in k-ε, k-ω, and LES models
    kTypeDict = {"inlet": "fixedValue",
                 "outlet": "zeroGradient",
                 "wall": "kqRWallFunction"}
    kValueDict = {"inlet": "uniform 0.0503", "wall": "uniform 0.0503"}
    build_zero_file("k", kTypeDict, kValueDict)

    # Initial conditions for ε (rate of dissipation of turbulent kinetic energy) used in k-ε models
    epsilonTypeDict = {"inlet": "fixedValue",
                       "outlet": "zeroGradient",
                       "wall": "epsilonWallFunction"}
    epsilonValueDict = {"inlet": "uniform 2.67", "wall": "uniform 2.67"}
    build_zero_file("epsilon", epsilonTypeDict, epsilonValueDict)

    # Initial conditions nu_t (turbulent kinematic viscosity) used in k-ε, k-ω, Spalart-Allmaras, and LES models
    nutTypeDict = {"inlet": "calculated",
                   "outlet": "calculated",
                   "wall": "nutUWallFunction"}
    nutValueDict = {"inlet": "uniform 0", "outlet": "uniform 0", "wall": "uniform 0"}
    build_zero_file("nut", nutTypeDict, nutValueDict)

    # Initial conditions for nu_tilda (turbulent kinematic viscosity) used Spalart-Allmaras models
    nuTildaTypeDict = {"inlet": "fixedValue",
                       "outlet": "zeroGradient",
                       "wall": "zeroGradient"}
    nuTildaValueDict = {"inlet": "uniform 0"}
    build_zero_file("nuTilda", nuTildaTypeDict, nuTildaValueDict)

    # Initial conditions for ω (specific turbulence dissipation rate) used in k-ω turbulence models
    omegaTypeDict = {"inlet": "fixedValue",
                     "outlet": "zeroGradient",
                     "wall": "zeroGradient"}
    omegaValueDict = {"inlet": "$internalField"}
    build_zero_file("omega", omegaTypeDict, omegaValueDict)

    # Initial conditions for kl (Turbulent Kinetic Energy per Unit Mass) used low-Re-number models or LES hybrid models
    klTypeDict = {"inlet": "fixedValue",
                  "outlet": "zeroGradient",
                  "wall": "fixedValue"}
    klValueDict = {"inlet": "uniform 0", "wall": "uniform 0"}
    build_zero_file("kl", klTypeDict, klValueDict)

    # Initial conditions for kt (Turbulent Thermal Energy) used in Turbulent heat transfer modeling (HVAC, combustion)
    ktTypeDict = {"inlet": "fixedValue",
                  "outlet": "zeroGradient",
                  "wall": "fixedValue"}
    ktValueDict = {"inlet": "uniform 0", "wall": "uniform 0"}
    build_zero_file("kt", ktTypeDict, ktValueDict)

    # Initial conditions for p_rgh (pressure considering gravity and buoyancy) used in multiphase simulations
    p_rghTypeDict = {"inlet": "fixedFluxPressure",
                     "outlet": "fixedFluxPressure",
                     "wall": "fixedFluxPressure",
                     "inletOutlet": "totalPressure"}
    p_rghValueDict = {"inlet": "uniform 0", "outlet": "uniform 0", "wall": "uniform 0", "inletOutlet": "uniform 0"}
    build_zero_file("p_rgh", p_rghTypeDict, p_rghValueDict)

    # Initial conditions for alpha.water (volumetric fraction of water) used in multiphase simulations
    # The new 0 file is in alpha.water.orig - when using in simulation make sure to copy over to new file "alpha.water"
    # The "alpha.water" file is changed during simulations so the "alpha.water.orig" file is retained to run future sims
    alpha_water_type_dict = {"inlet": "fixedValue",
                             "outlet": "zeroGradient",
                             "wall": "zeroGradient",
                             "inletOutlet": "inletOutlet"}
    alpha_water_value_dict = {"inlet": "uniform 1", "outlet": "uniform 0", "inletOutlet": "uniform 0"}
    build_zero_file("alphawaterorig", alpha_water_type_dict, alpha_water_value_dict)
