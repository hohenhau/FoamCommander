#!/usr/bin/python

import os
from .prepareReplacer import *
from .classFlowMetrics import FlowMetrics


def generate_dict(patch_names, template_name, template_dir, output_name, output_dir, replace_function):
    """Create various dict.gen files"""
    output_name = f'{output_name}.gen'
    print(f"\nCreating system/{output_name}...")
    template_path = os.path.join(template_dir, template_name)  # Template file
    output_path = os.path.join(output_dir, output_name)
    patterns_and_replacements = replace_function(patch_names)
    if any([replacement for pattern, replacement in patterns_and_replacements]):
        perform_regex_replacements(patterns_and_replacements, str(template_path), output_path)
        print(f"{output_name} created at: {output_path}")
    else:
        print(f"Could not generate suitable inputs for {output_name}")


def generate_dynamic_mesh_dict(patch_names: list, template_dir: str, output_name: str, output_dir: str):
    """Create various dict.gen files"""
    output_name = f'{output_name}.gen'
    print(f"\nCreating system/{output_name}...")
    output_path = os.path.join(output_dir, output_name)
    patterns_and_replacements, template_name = replace_dynamic_sliding_mesh(patch_names)
    template_path = os.path.join(template_dir, template_name)  # Template file
    if any([replacement for pattern, replacement in patterns_and_replacements]):
        perform_regex_replacements(patterns_and_replacements, str(template_path), output_path)
        print(f"{output_name} created at: {output_path}")
    else:
        print(f"Could not generate suitable inputs for {output_name}")


def generate_zero_file(patch_names: list, template_dir: str, zero_dir: str, field: str, boundary_dict: dict):
    """Creates a file in the zero directory with grouped patch settings."""
    template_path = os.path.join(template_dir, f"{field}")
    output_path = os.path.join(zero_dir, field)
    boundary_types = boundary_dict['types']
    boundary_vals = boundary_dict['values']
    internal_field = boundary_dict['internal_field']

    # Ensure there is an entry for walls
    if 'wall' not in boundary_types:
        boundary_types['wall'] = get_boundary_type_from_patch_name('wall')

    # Copy wall entry to pseudo walls
    for pseudo_wall in ['MRFnoSlip', 'movingWallVelocity', 'stationary', 'rotating']:
        if pseudo_wall not in boundary_types:
            boundary_types[pseudo_wall] = boundary_types['wall']
            if pseudo_wall not in boundary_vals and 'wall' in boundary_vals:
                boundary_vals[pseudo_wall] = boundary_vals['wall']

    # Create a fan condition for internal fan faces for the pressure field
    for j in (i for i in patch_names if "fan" in i.lower() and field == "p"
                                        and get_boundary_type_from_patch_name(i) == "cyclic"):
        boundary_types[j] = (f'{" " * 8}type            fanPressureJump;  // Units are pressure(Pa) / density (rho)\n'
                             f'{" " * 8}patchType       cyclic;\n'
                             f'{" " * 8}value           uniform 0;\n'
                             f'{" " * 8}jump            uniform 0;\n'
                             f'{" " * 8}reverse         false;\n'
                             f'{" " * 8}jumpTable       constant 2.0;  // Options {{constant, polynomial}}\n')

    # Create a porous condition for internal porous faces for the pressure field
    for j in (i for i in patch_names if "porous" in i.lower() and field == "p"
                                        and get_boundary_type_from_patch_name(i) == "cyclic"):
        boundary_types[j] = (f'{" " * 8}type            porousBafflePressure;\n'
                             f'{" " * 8}patchType       cyclic;\n'
                             f'{" " * 8}value           uniform 0;\n'
                             f'{" " * 8}jump            uniform 0;\n'
                             f'{" " * 8}uniformJump     false;\n'
                             f'{" " * 8}D               7000000;  // Darcy coefficient\n'
                             f'{" " * 8}I               240;      // Inertial coefficient\n'
                             f'{" " * 8}length          0.002;    // Scaling of pressure drop\n')

    # Create a velocity condition for rotating surfaces in the velocity field
    for j in (i for i in patch_names if field == "U" and get_boundary_type_from_patch_name(i) == "rotating"):
        boundary_types[j] = (f'{" " * 8}#include "../system/fvSchemes"\n'
                             f'{" " * 8}#ifeq $ddtSchemes/default steadyState\n'
                             f'{" " * 12}type        MRFnoSlip;\n'
                             f'{" " * 8}#else\n'
                             f'{" " * 12}type        movingWallVelocity;\n'
                             f'{" " * 12}value       uniform (0 0 0);\n'
                             f'{" " * 8}#endif\n')

    # Filter out any "patches" that are actually regions, but are not an NCC type region
    excluded = ('zone', 'region', 'honeycomb')
    filtered_names = [i for i in patch_names if 'ncc' in i.lower() or not any(word in i.lower() for word in excluded)]

    patterns_and_replacements = replace_zero_boundaries(filtered_names, boundary_types, boundary_vals, internal_field)
    perform_regex_replacements(patterns_and_replacements, template_path, output_path)
    print(f"Field {field} created at: {output_path}")


def generate_all_zero_files(patch_names: list, template_dir: str, zero_dir: str, fm:FlowMetrics):
    """Build the zero files for the various fields and boundaries"""

    field_dicts = {
        'U': {'types': {'wall': 'fixedValue', 'MRFnoSlip': 'MRFnoSlip', 'movingWallVelocity': 'movingWallVelocity',
                        'NCC': 'movingWallSlipVelocity'},
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
                  'internal_field': fm.turb_spec_dissip_rate.value},

        'pointDisplacement': {'types': {'inlet': 'fixedValue', 'outlet': 'fixedValue', 'wall': 'fixedValue',
                                        'rotating': 'calculated', 'stationary': 'calculated'},
                              'values': {'inlet': '$internalField', 'outlet': '$internalField',
                                         'wall': '$internalField',
                                         'rotating': 'uniform (0 0 0)', 'stationary': 'uniform (0 0 0)'},
                              'internal_field': 0},

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

    print('\nGenerating fields in 0/')
    for field_name, field_dict in field_dicts.items():
        generate_zero_file(patch_names, template_dir, zero_dir, field_name, field_dict)

