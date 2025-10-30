#!/usr/bin/python


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
        self.perform_boundary_calculations()

    def collect_inputs(self):
        """Get input values for any missing flow metrics"""
        if self.hydraulic_diameter.value is None:
            self.hydraulic_diameter.value = self.get_metric("Enter the hydraulic diameter (m): ")

        if self.free_stream_velocity.value is None:
            self.free_stream_velocity.value = self.get_metric("Enter the free stream velocity (m/s): ")

        if self.kinematic_viscosity.value is None:
            print("Typical values for Kinematic viscosity (m²/s):\n  - Water: 0.000001\n  - Air: 0.0000148")
            self.kinematic_viscosity.value = self.get_metric("Enter the kinematic viscosity (m²/s): ")


    def perform_boundary_calculations(self):
        """Perform calculations only if the value is missing."""
        calculations = [(self.reynolds_number, self.calc_reynolds_number),
                        (self.turb_intensity, self.calc_turb_intensity),
                        (self.turb_kinetic_energy, self.calc_turb_kinetic_energy),
                        (self.turb_length_scale, self.calc_turb_length_scale),
                        (self.turb_dissipation_rate, self.calc_turb_dissipation_rate),
                        (self.specific_dissipation, self.calc_specific_turb_dissipation_rate),
                        (self.turb_viscosity, self.calc_turb_viscosity_epsilon)]
        for flow_metric, calc_function in calculations:
            if flow_metric.value is None:
                flow_metric.value = calc_function()


    def __repr__(self):
        """Custom print method for easy visualization of results"""
        print('\nResulting flow metrics:')
        return "\n".join(
            f"{attr} ({getattr(self, attr).symbol}): {float('%.*g' % (3, getattr(self, attr).value))}"
            for attr in vars(self) if isinstance(getattr(self, attr), FlowMetric)
        )

    # ------------------- Calculation Methods -------------------

    def calc_reynolds_number(
            self,
            length:float | None = None,
            velocity: float | None = None,
            kinematic_viscosity:float | None = None) -> float:
        """Calculates the Reynolds Number from kinematic_viscosity, velocity, and length scale"""
        length = self.hydraulic_diameter.value if length is None else length
        velocity = self.free_stream_velocity.value if velocity is None else velocity
        kinematic_viscosity = self.kinematic_viscosity.value if kinematic_viscosity is None else kinematic_viscosity
        return length * velocity / kinematic_viscosity


    def calc_turb_intensity(self, reynolds_number:float | None=None) -> float:
        """Calculates the turbulent intensity from the Reynold's number"""
        turb_coefficient = 0.16
        reynolds_number = self.reynolds_number.value if reynolds_number is None else reynolds_number
        return turb_coefficient * reynolds_number ** (-1 / 8)


    def calc_turb_kinetic_energy(self, velocity:float | None=None, turb_intensity:float | None=None) -> float:
        """Calculates the turbulent kinetic energy from velocity and turbulent intensity"""
        velocity = self.free_stream_velocity.value if velocity is None else velocity
        turb_intensity = self.turb_intensity.value if turb_intensity is None else turb_intensity
        return (3 / 2) * (velocity * turb_intensity) ** 2


    def calc_turb_length_scale(self, hydraulic_diameter: float | None=None) -> float:
        """Calculates the turbulent length scale from the hydraulic diameter"""
        coefficient_for_pipe_flow = 0.07
        hydraulic_diameter = self.hydraulic_diameter.value if hydraulic_diameter is None else hydraulic_diameter
        return hydraulic_diameter * coefficient_for_pipe_flow


    def calc_turb_dissipation_rate(
            self,
            turb_kinetic_energy: float | None=None,
            turb_length_scale: float | None=None) -> float:
        """Calculates turbulent dissipation rate from turbulent kinetic energy and turbulent length scale"""
        model_function = 0.09
        turb_kinetic_energy = self.turb_kinetic_energy.value if turb_kinetic_energy is None else turb_kinetic_energy
        turb_length_scale = self.turb_length_scale.value if turb_length_scale is None else turb_length_scale
        return model_function ** (3 / 4) * turb_kinetic_energy ** (3 / 2) / turb_length_scale


    def calc_specific_turb_dissipation_rate(
            self,
            turb_kinetic_energy: float | None=None,
            turb_length_scale: float | None=None) -> float:
        """Calculates specific turbulent dissipation rate from turbulent kinetic energy and turbulent length scale"""
        model_function = 0.09
        turb_kinetic_energy = self.turb_kinetic_energy.value if turb_kinetic_energy is None else turb_kinetic_energy
        turb_length_scale = self.turb_length_scale.value if turb_length_scale is None else turb_length_scale
        return turb_kinetic_energy ** 0.5 / (model_function ** (1 / 4) * turb_length_scale)


    def calc_turb_viscosity_epsilon(
            self,
            turb_kinetic_energy: float | None=None,
            turb_dis_rate: float | None=None) -> float:
        """Calculates turbulent viscosity from turbulent kinetic energy and turbulent dissipation rate"""
        model_function = 0.09
        turb_kinetic_energy = self.turb_kinetic_energy.value if turb_kinetic_energy is None else turb_kinetic_energy
        turb_dis_rate = self.turb_dissipation_rate.value if turb_dis_rate is None else turb_dis_rate
        return model_function * turb_kinetic_energy ** 2 / turb_dis_rate


    @staticmethod
    def get_metric(prompt: str):
        while True:
            try:
                metric = float(input(prompt))
                if metric <= 0:
                    raise ValueError("Value must be positive")
                return metric
            except ValueError as e:
                print(f"Invalid input: {e}")