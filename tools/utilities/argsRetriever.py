from tools.utilities.classFoamDictEditor import ClassFoamDictEditor
from tools.utilities.classFlowMetrics import FlowMetrics


def get_positive_metric_input(prompt: str):
    while True:
        try:
            metric = float(input(prompt))
            if metric <= 0:
                raise ValueError("Value must be positive")
            return metric
        except ValueError as e:
            print(f"Invalid input: {e}")


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