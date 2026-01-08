#!/usr/bin/python

import stl_formatter
from estimateInternalFields import estimate_flow_metrics
from utilities.commandLineArgsParser import detect_and_parse_arguments
from utilities.prepareGenerator import *
from utilities.prepareInitiator import *
from utilities.customPropertyLoader import load_and_update_custom_properties
from utilities.fileConstants import TEMPLATE_BOUNDARY_DIR, TEMPLATE_CONSTANT_DIR, TEMPLATE_SYSTEM_DIR
from utilities.fileConstants import BASE_DIR, TRI_SURFACE_DIR, ZERO_DIR, SYSTEM_DIR, CONSTANT_DIR


if __name__ == "__main__":
    print(f"\nPreparing case in directory: {BASE_DIR}")
    initialisation(TRI_SURFACE_DIR, ZERO_DIR)
    arguments = detect_and_parse_arguments()
    stl_formatter.format_stl_files()
    flow_metrics = load_and_update_custom_properties()
    patch_names = load_stl_files(TRI_SURFACE_DIR)
    generate_all_zero_files(patch_names, TEMPLATE_BOUNDARY_DIR, ZERO_DIR, flow_metrics)

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
