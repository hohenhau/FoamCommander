#!/usr/bin/python

import stl_formatter
from estimateInternalFields import estimate_flow_metrics
from utilities.argsParser import detect_and_parse_arguments
from utilities.prepareGenerator import *
from utilities.prepareInitiator import *

# Global Variables
PY_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_BOUNDARY_DIR = os.path.join(PY_FILE_PATH, "templatesBoundary")
TEMPLATE_CONSTANT_DIR = os.path.join(PY_FILE_PATH, "templatesConstant")
TEMPLATE_SYSTEM_DIR = os.path.join(PY_FILE_PATH, "templatesSystem")
CURRENT_DIR = os.getcwd()
TRI_SURFACE_DIR = os.path.join(CURRENT_DIR, "constant", "triSurface")
ZERO_DIR = os.path.join(CURRENT_DIR, "0.gen")
SYSTEM_DIR = os.path.join(CURRENT_DIR, "system")
CONSTANT_DIR = os.path.join(CURRENT_DIR, "constant")


if __name__ == "__main__":
    print(f"\nPreparing case in directory: {CURRENT_DIR}")
    initialisation(TRI_SURFACE_DIR, ZERO_DIR)
    arguments = detect_and_parse_arguments()
    stl_formatter.format_stl_files()
    flow_metrics = estimate_flow_metrics(arguments)
    patch_names = load_stl_files(TRI_SURFACE_DIR)
    generate_all_zero_files(patch_names, TEMPLATE_SYSTEM_DIR, ZERO_DIR, flow_metrics)

    generate_dict(patch_names, 'snappyHexMeshTemplate', TEMPLATE_SYSTEM_DIR,
                  'snappyHexMeshDict', SYSTEM_DIR, replace_snappy_hex_mesh_dict)

    generate_dict(patch_names, 'surfaceFeaturesTemplate', TEMPLATE_SYSTEM_DIR,
                  'surfaceFeaturesDict', SYSTEM_DIR, replace_surface_features_dict)

    generate_dict(patch_names, 'createBafflesTemplate', TEMPLATE_SYSTEM_DIR,
                  'createBafflesDict', SYSTEM_DIR, replace_create_baffles_dict)

    generate_dict(patch_names, 'createNonConformalCouplesTemplate', TEMPLATE_SYSTEM_DIR,
                  'createNonConformalCouplesDict', SYSTEM_DIR, replace_create_ncc_dict)

    generate_dict(patch_names, 'decomposeParTemplate', TEMPLATE_SYSTEM_DIR,
                  'decomposeParDict', SYSTEM_DIR, replace_decompose_par_dict)

    generate_dict(patch_names, 'MRFPropertiesTemplate', TEMPLATE_CONSTANT_DIR,
                  'MRFProperties', CONSTANT_DIR, replace_mrf_properties)

    generate_dict(patch_names, 'fvModelsTemplate', TEMPLATE_CONSTANT_DIR,
                  'fvModels', CONSTANT_DIR, replace_fv_models)

    generate_dynamic_mesh_dict(patch_names, TEMPLATE_CONSTANT_DIR,
                               'dynamicMeshDict', CONSTANT_DIR)

    print('\nCompleted preparation!\n\n')
