import argparse
import subprocess


def detect_and_parse_arguments(sys):
    """Parse command line arguments with custom validation and allow unknown arguments."""

    # Instantiate the parser with suppressed usage and custom help formatting
    parser = argparse.ArgumentParser(
        description="Flow metrics calculation for CFD simulation",
        formatter_class=argparse.RawTextHelpFormatter,
        usage=argparse.SUPPRESS  # This removes the usage line
    )

    # Define arguments with empty metavar to hide uppercase placeholders
    parser.add_argument("-hydraulic_diameter", type=float, help="Hydraulic diameter", metavar='')
    parser.add_argument("-free_stream_velocity", type=float, help="Free stream velocity", metavar='')
    parser.add_argument("-kinematic_viscosity", type=float, help="Kinematic viscosity", metavar='')
    parser.add_argument("-reynolds_number", type=float, help="Reynolds number", metavar='')
    parser.add_argument("-turb_intensity", type=float, help="Turbulence intensity", metavar='')
    parser.add_argument("-turb_kinetic_energy", type=float, help="Turbulence kinetic energy", metavar='')
    parser.add_argument("-turb_length_scale", type=float, help="Turbulence length scale", metavar='')
    parser.add_argument("-turb_dissipation_rate", type=float, help="Turbulence dissipation rate", metavar='')
    parser.add_argument("-specific_dissipation", type=float, help="Specific dissipation rate", metavar='')
    parser.add_argument("-turb_viscosity", type=float, help="Turbulent viscosity", metavar='')

    # Parse known arguments
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
