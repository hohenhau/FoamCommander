import argparse
import subprocess


# Custom formatter to adjust column widths
class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, 
            max_help_position=30,  # Width allocated for argument names
            width=100              # Total terminal width
            **kwargs
        )

def detect_and_parse_arguments(sys):
    """Parse command line arguments with improved help formatting."""
    parser = argparse.ArgumentParser(
        description="Flow metrics calculation for CFD simulation",
        formatter_class=CustomHelpFormatter,  # Use the custom formatter
        usage=argparse.SUPPRESS               # Suppress the "usage" line
    )

    # Define arguments with suppressed metavar
    args_list = [
        ("-hydraulic_diameter", "Hydraulic diameter"),
        ("-free_stream_velocity", "Free stream velocity"),
        ("-kinematic_viscosity", "Kinematic viscosity"),
        ("-reynolds_number", "Reynolds number"),
        ("-turb_intensity", "Turbulence intensity"),
        ("-turb_kinetic_energy", "Turbulence kinetic energy"),
        ("-turb_length_scale", "Turbulence length scale"),
        ("-turb_dissipation_rate", "Turbulence dissipation rate"),
        ("-specific_dissipation", "Specific dissipation rate"),
        ("-turb_viscosity", "Turbulent viscosity"),
    ]

    for arg, help_text in args_list:
        parser.add_argument(arg, type=float, help=help_text, metavar='')

    args, unknown_args = parser.parse_known_args()
    if unknown_args:
        print(f"Warning: Ignoring unknown arguments: {unknown_args}")
    return args


def run_script_with_arguments(args, script_name):
    """Run the script with parsed arguments"""
    command = [script_name]
    # Add arguments to the command
    for key, value in vars(args).items():
        if value is not None:
            command.extend([f"-{key}", str(value)])
    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("Error:", result.stderr)
    return result
