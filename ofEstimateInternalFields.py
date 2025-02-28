#!/usr/bin/python

import sys
from ofParseArgs import detect_and_parse_arguments


class FlowMetric:
    """A class to define the attributes of a flow metric"""
    def __init__(self, name: str, symbol: str, value: float = None):
        self.description = name
        self.symbol = symbol
        self.value = value


class FlowMetrics:
    """A class to contain all flow metrics"""

    def __init__(self, args):
        # Initialize all metrics as FlowMetric objects
        self.hydraulic_diameter = FlowMetric("Hydraulic Diameter", "D_h", args.hydraulic_diameter)
        self.free_stream_velocity = FlowMetric("Free Stream Velocity", "U_inf", args.free_stream_velocity)
        self.kinematic_viscosity = FlowMetric("Kinematic Viscosity", "nu", args.kinematic_viscosity)
        self.reynolds_number = FlowMetric("Reynolds Number", "Re", args.reynolds_number)
        self.turb_intensity = FlowMetric("Turbulence Intensity", "I", args.turb_intensity)
        self.turb_kinetic_energy = FlowMetric("Turbulence Kinetic Energy", "k", args.turb_kinetic_energy)
        self.turb_length_scale = FlowMetric("Turbulence Length Scale", "l_t", args.turb_length_scale)
        self.turb_dissipation_rate = FlowMetric("Turbulence Dissipation Rate", "epsilon", args.turb_dissipation_rate)
        self.specific_dissipation = FlowMetric("Specific Dissipation Rate", "omega", args.specific_dissipation)
        self.turb_viscosity = FlowMetric("Turbulent Viscosity", "nu_t", args.turb_viscosity)

        self.collect_inputs()
        self.perform_calculations()

    def collect_inputs(self):
        """Get input values for any missing flow metrics"""
        if self.hydraulic_diameter.value is None:
            self.hydraulic_diameter.value = self.get_metric("Enter the hydraulic diameter (m): ")

        if self.free_stream_velocity.value is None:
            self.free_stream_velocity.value = self.get_metric("Enter the free stream velocity (m/s): ")

        if self.kinematic_viscosity.value is None:
            print("Typical values for Kinematic viscosity (m²/s):\n  - Water: 0.000001\n  - Air: 0.0000148")
            self.kinematic_viscosity.value = self.get_metric("Enter the kinematic viscosity (m²/s): ")

    def perform_calculations(self):
        """Perform calculations only if the value is missing"""

        if self.reynolds_number.value is None:
            self.reynolds_number.value = self.calc_reynolds_number(self.hydraulic_diameter.value,
                                                                   self.free_stream_velocity.value,
                                                                   self.kinematic_viscosity.value)

        if self.turb_intensity.value is None:
            self.turb_intensity.value = self.calc_turb_intensity(self.reynolds_number.value)

        if self.turb_kinetic_energy.value is None:
            self.turb_kinetic_energy.value = self.calc_turb_kinetic_energy(self.free_stream_velocity.value,
                                                                           self.turb_intensity.value)

        if self.turb_length_scale.value is None:
            self.turb_length_scale.value = self.calc_turb_length_scale(self.hydraulic_diameter.value)

        if self.turb_dissipation_rate.value is None:
            self.turb_dissipation_rate.value = self.calc_turb_dissipation_rate(self.turb_kinetic_energy.value,
                                                                               self.turb_length_scale.value)

        if self.specific_dissipation.value is None:
            self.specific_dissipation.value = self.calc_specific_turb_dissipation_rate(self.turb_kinetic_energy.value,
                                                                                       self.turb_length_scale.value)

        if self.turb_viscosity.value is None:
            self.turb_viscosity.value = self.calc_turb_viscosity_epsilon(self.turb_kinetic_energy.value,
                                                                         self.turb_dissipation_rate.value)

    def __repr__(self):
        """Custom print method for easy visualization of results"""
        print('\nResulting flow metrics:')
        return "\n".join(
            f"{attr} ({getattr(self, attr).symbol}): {float('%.*g' % (3, getattr(self, attr).value))}"
            for attr in vars(self) if isinstance(getattr(self, attr), FlowMetric)
        )

    # ------------------- Calculation Methods -------------------

    def calc_reynolds_number(self, length: float, velocity: float, kinematic_viscosity: float):
        return length * velocity / kinematic_viscosity

    def calc_turb_intensity(self, reynolds_number: float):
        turb_coefficient = 0.16
        return turb_coefficient * reynolds_number ** (-1 / 8)

    def calc_turb_kinetic_energy(self, velocity: float, turb_intensity: float):
        return (3 / 2) * (velocity * turb_intensity) ** 2

    def calc_turb_length_scale(self, hydraulic_diameter: float):
        coefficient_for_pipe_flow = 0.07
        return hydraulic_diameter * coefficient_for_pipe_flow

    def calc_turb_dissipation_rate(self, turbulent_kinetic_energy: float, turbulent_length_scale: float):
        model_function = 0.09
        return model_function ** (3 / 4) * turbulent_kinetic_energy ** (3 / 2) / turbulent_length_scale

    def calc_specific_turb_dissipation_rate(self, turbulent_kinetic_energy: float, turbulent_length_scale: float):
        model_function = 0.09
        return turbulent_kinetic_energy ** 0.5 / (model_function ** (1 / 4) * turbulent_length_scale)

    def calc_turb_viscosity_epsilon(self, turb_kinetic_energy: float, turb_dissipation_rate: float):
        model_function = 0.09
        return model_function * turb_kinetic_energy ** 2 / turb_dissipation_rate

    def get_metric(self, prompt: str):
        while True:
            try:
                metric = float(input(prompt))
                if metric <= 0:
                    raise ValueError("Value must be positive")
                return metric
            except ValueError as e:
                print(f"Invalid input: {e}")


def estimate_internal_fields(args=None):
    """
    Creates flow metrics for CFD simulation. Uses arguments passed externally if available,
    otherwise calls detect_and_parse_arguments to get arguments.

    :param args: Arguments passed externally (if any)
    :return: FlowMetrics object
    """
    # If args are not passed, use the detect_and_parse_arguments function to retrieve them
    if not args:
        args = detect_and_parse_arguments(sys)  # This will handle the argument parsing

    # Create FlowMetrics object using the arguments
    flow_metrics = FlowMetrics(args)
    print(flow_metrics)
    return flow_metrics


if __name__ == "__main__":
    estimate_internal_fields()
