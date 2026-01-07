#!/usr/bin/python
from numpy.f2py.auxfuncs import throw_error
import sys

from .classFoamDictEditor import ClassFoamDictEditor
from .classFlowMetrics import FlowMetrics, FlowMetric
from .userInputParser import get_positive_metric_input


def initiate_flow_metrics_from_custom_properties(file_path: str):

    custom_properties = ClassFoamDictEditor(file_path).load_dict_entries()

    if custom_properties["flowType"].lower == "external":
        print("external flows are currently not supported")
        sys.exit(1)

    # Match the variables to the spelling within the custom dictionary
    str_fluid_type = "fluidType"
    str_freestream_velocity = "freestreamVelocity"
    str_freestream_pressure = "freestreamPressure"
    str_temperature = "temperature"
    str_hydraulic_diameter = "hydraulicDiameter"

    # Instantiate the flow metrics and add the values from the custom dictionary
    flow_metrics = FlowMetrics()
    flow_metrics.fluid_type.kind = custom_properties[str_fluid_type]
    flow_metrics.freestream_velocity.value = custom_properties[str_freestream_velocity]
    flow_metrics.freestream_pressure.value = custom_properties[str_freestream_pressure]
    flow_metrics.temperature_c.value = custom_properties[str_temperature]
    flow_metrics.hydraulic_diameter.value = custom_properties[str_hydraulic_diameter]





def check_or_add_custom_properties(dictionary: dict, key: str, message: str) -> dict:
    if key not in dictionary:
        print(message)
        value = get_positive_metric_input(message)
        dictionary[key] = value
    return dictionary


def collect_inputs(self, custom_properties_file: str):
    """Get input values for any missing flow metrics"""

    fde = ClassFoamDictEditor(custom_properties_file)
    entries = fde.load_dict_entries()

    metrics = [("temperature", "Enter the temperature (°C)"),
               ("hydraulicDiameter", "Enter the hydraulic diameter (m)"),
               ("freestreamVelocity", "Enter the free stream velocity (m/s)")]


    for metric, message in metrics:
        if metric not in entries:
            value = get_positive_metric_input(message)
            entries[metric] = value



#  TODO:
# def load_custom_properties(custom_file: str, template_file: str, transport_file: str, constant_dir: str):
#
#     1) Check if custom_file exists
#     1a) If yes, import properties
#     1b) If no, generate from template
#
#     2) Check that the base directory for custom file matches the current base directory
#     2a) If yes, proceed
#     2B) If no, exit
#
#     3) Check if the "nu" value from the custom file matched that from the transport file
#     3a) if yes, proceed
#     3b) if no, ask if it should be overwritten
#     3bi) if yes overwrite
#     3bii) if no, exit