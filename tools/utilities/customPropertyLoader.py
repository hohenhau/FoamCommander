#!/usr/bin/python
import os
import sys

from .fileConstants import CONSTANT_DIR, TEMPLATE_CONSTANT_DIR, BASE_DIR
from .fileHandler import check_and_create_file
from .classFoamDictEditor import FoamDictEditor
from .classFlowMetrics import FlowMetrics


def load_and_update_custom_properties() -> FlowMetrics:
    """Loads metrics from the custom properties file, and uses them to instantiate and calculate flow metrics."""

    # Access and Load custom properties
    file_name = "focoProperties"
    template_file_path = os.path.join(TEMPLATE_CONSTANT_DIR, file_name)
    check_and_create_file(file_directory=CONSTANT_DIR, file_name=file_name, template_file_path=template_file_path)
    file_path = os.path.join(CONSTANT_DIR, file_name)
    fde = FoamDictEditor(file_path)
    custom_properties = fde.load_dict_entries()

    # Match the variables to the spelling within the custom dictionary
    str_directory = "directory"
    str_flow_type = "flowType"
    str_fluid_type = "fluidType"
    str_freestream_velocity = "freestreamVelocity"
    str_freestream_pressure = "freestreamPressure"
    str_temperature_c = "temperature"
    str_density = "density"
    str_hydraulic_diameter = "hydraulicDiameter"
    str_kinematic_viscosity = "nu"

    # Check that basic conditions are met
    specified_directory = custom_properties[str_directory].lower()
    actual_directory = BASE_DIR.split("/")[-1].lower()
    if specified_directory != actual_directory:
        print(f"Directory specified in {file_name} ({specified_directory}) does not match CWD ({actual_directory})")
        sys.exit(1)
    if custom_properties[str_flow_type].lower() != "internal":
        print(f"{custom_properties[str_flow_type]} flows are unsupported. Only internal flows are currently supported")
        sys.exit(1)

    # Instantiate the flow metrics and add the values from the custom dictionary
    flow_metrics = FlowMetrics()
    flow_metrics.fluid_type.kind = custom_properties[str_fluid_type]
    flow_metrics.freestream_velocity.value = custom_properties[str_freestream_velocity]
    flow_metrics.freestream_pressure.value = custom_properties[str_freestream_pressure]
    flow_metrics.temperature_c.value = custom_properties[str_temperature_c]
    flow_metrics.density.value = custom_properties[str_density]
    flow_metrics.hydraulic_diameter.value = custom_properties[str_hydraulic_diameter]

    # Perform calculations to fill in the missing metrics
    flow_metrics.perform_boundary_calculations()

    # Update the custom file with the calculated flow metrics
    fde.set_value(str_fluid_type, flow_metrics.fluid_type.kind)
    fde.set_value(str_freestream_velocity, flow_metrics.freestream_velocity.value)
    fde.set_value(str_freestream_pressure, flow_metrics.freestream_pressure.value)
    fde.set_value(str_temperature_c, flow_metrics.temperature_c.value)
    fde.set_value(str_density, flow_metrics.density.value)
    fde.set_value(str_hydraulic_diameter, flow_metrics.hydraulic_diameter.value)
    fde.set_value(str_kinematic_viscosity, flow_metrics.kinematic_viscosity.value)

    # Ensure existence of transport properties
    file_name = "transportProperties"
    template_file_path = os.path.join(TEMPLATE_CONSTANT_DIR, file_name)
    check_and_create_file(file_directory=CONSTANT_DIR, file_name=file_name, template_file_path=template_file_path)
    file_path = os.path.join(CONSTANT_DIR, file_name)
    fde_nu = FoamDictEditor(file_path)
    fde_nu.overwrite_nu_in_transport_properties(flow_metrics.kinematic_viscosity.value)

    return flow_metrics