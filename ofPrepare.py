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


def get_patch_type(input_name: str):
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
        'cyclic': 'cyclic'}
    for patch_name, patch_type in patch_mappings.items():
        if patch_name in input_name:
            return patch_type
    return 'wall'


def build_zero_file(base_name: str, types: dict, values: dict):
    """Creates a file in the zero directory with grouped patch settings."""
    output_path = os.path.join(ZERO_DIR, base_name)
    skeleton_head_path = os.path.join(SKELETON_DIR, f"{base_name}Head")
    
    # Ensure common patch types exist
    types['symmetry'] = 'symmetry'
    types['slip'] = 'slip'
    
    # Group patches by type
    patch_groups = {}
    for patch in patch_names:
        patch_type = get_patch_type(patch)
        if patch_type not in patch_groups:
            patch_groups[patch_type] = []
        patch_groups[patch_type].append(patch)
    
    # Write the header
    with open(output_path, 'w') as outfile, open(skeleton_head_path) as f:
        outfile.write(f.read())
    
        # Write grouped patches
        for patch_type, patches in patch_groups.items():
            patch_regex = f'("{'|'.join(patches)}")'  # Regex grouping in OpenFOAM format
            outfile.write(f'    {patch_regex}\n    {{\n')
            outfile.write(f'        type    {types.get(patch_type, "wall")};\n')
            if patch_type in values:
                outfile.write(f'        value   {values[patch_type]};\n')
            outfile.write('    }\n')
    
        outfile.write('}\n')


def process_stl_files():
    """Processes STL files, renaming and extracting patch names."""
    patches = list()
    for filename in os.listdir(TRI_SURFACE_DIR):
        if filename.lower().endswith(".stl"):
            filepath = os.path.join(TRI_SURFACE_DIR, filename)
            patch_name = re.split(r"\.", filename)[0]
            if get_patch_type(patch_name) != "screen" and patch_name not in patches:
                print(f"Match: {patch_name}")
                patches.append(patch_name)
            with open(filepath) as file, open(filepath + ".tmp", "w") as out_file:
                for line in file:
                    if re.match(r"endsolid", line):
                        out_file.write(f"endsolid {patch_name}\n")
                    elif re.match(r"solid", line):
                        out_file.write(f"solid {patch_name}\n")
                    else:
                        out_file.write(line)
            os.rename(filepath + ".tmp", filepath.lower())  # Convert STL to lowercase
    return patches


def create_surface_feature_extract_dict():
    """Creates the surfaceFeatureExtractDict file."""
    output_path = os.path.join(SYSTEM_DIR, "surfaceFeatureExtractDict.x")
    skeleton_head_path = os.path.join(SKELETON_DIR, "surfaceFeatureExtractHead")
    skeleton_part_path = os.path.join(SKELETON_DIR, "surfaceFeatureExtractPart")
    with open(output_path, 'w') as sfefile, open(skeleton_head_path) as f:
        sfefile.write(f.read())
    for patch in patch_names:
        print(f"{patch}.stl")
        sfefile.write(f"{patch}.stl\n")
        with open(skeleton_part_path) as f:
            sfefile.write(f.read())


def create_snappy_hex_mesh_dict():
    """Creates the snappyHexMeshDict.x file."""
    output_path = os.path.join(SYSTEM_DIR, "snappyHexMeshDict.x")
    skeleton_head_path = os.path.join(SKELETON_DIR, "snappyHexMeshHead")
    skeleton_tail_path = os.path.join(SKELETON_DIR, "snappyHexMeshTail")

    # Write contents of skeleton header
    with open(output_path, 'w') as shm_file, open(skeleton_head_path) as skeleton_head:
        shm_file.write(skeleton_head.read())

    # Write geometry list consisting of .stl files
    for patch in patch_names:
        shm_file.write(f'        {patch}.stl {{type triSurfaceMesh; name {patch};}}\n')
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
        patch_type = get_patch_type(patch)
        patch_type = 'patch' if patch_type in {'inlet', 'outlet', 'slip', 'cyclic'} else patch_type
        shm_file.write(f'            {patch} {{level (0 0); patchInfo {{type {patch_type};}} }}\n')
    # Write example layout of honeycomb
    shm_file.write('            // honeycombA\n')
    shm_file.write('            //    {level (4 4);\n')
    shm_file.write('            //    faceZone honeycombFacesA;\n')
    shm_file.write('            //    cellZone honeycombCellsA;\n')
    shm_file.write('            //    cellZoneInside inside;}\n')
    shm_file.write('        }\n\n')

    # Write contents of skeleton tail
    with open(skeleton_tail_path) as skeleton_tail:
        shm_file.write(skeleton_tail.read())


if __name__ == "__main__":
    print(f"Processing directory: {CURRENT_DIR}")
    patch_names = process_stl_files()

    print("Creating surfaceFeatureExtractDict...")
    create_surface_feature_extract_dict()

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


# Additional files required for multiphase simulations

# Initial conditions for p_rgh (pressure considering gravity and buoyancy) used in multiphase simulations
p_rghTypeDict = {"inlet": "fixedFluxPressure",
                 "outlet": "fixedFluxPressure",
                 "wall": "fixedFluxPressure",
                 "inletOutlet": "totalPressure"}
p_rghValueDict = {"inlet": "uniform 0", "outlet": "uniform 0", "wall": "uniform 0", "inletOutlet": "uniform 0"}
buildZeroFile("p_rgh", p_rghTypeDict, p_rghValueDict)

# Initial conditions for alpha.water (volumetric fraction of water) used in multiphase simulations
# new 0 file is in alpha.water.orig - when using in simulation make sure to copy over to new file "alpha.water" 
# alpha.water is changed during simulation and so the .orig file is retained to run future sims.
alphawaterorigTypeDict = {"inlet": "fixedValue",
                          "outlet": "zeroGradient",
                          "wall": "zeroGradient",
                          "inletOutlet": "inletOutlet"}
alphawaterorigValueDict = {"inlet": "uniform 1", "outlet": "uniform 0", "inletOutlet": "uniform 0"}
buildZeroFile("alphawaterorig", alphawaterorigTypeDict, alphawaterorigValueDict)
