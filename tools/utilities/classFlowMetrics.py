#!/usr/bin/python

from argsRetriever import get_positive_metric_input

class FlowMetric:
    """A class to define the attributes of a flow metric"""
    def __init__(self, name: str, symbol: str, value: float = None, unit: str = None, prompt: str = None):
        self.description = name
        self.symbol = symbol
        self.value = value
        self.unit = unit
        self.prompt = prompt


class FlowMetrics:
    """A class to contain all flow metrics"""

    def __init__(self, args=None):
        # Initialize all metrics as FlowMetric objects
        self.hydraulic_diameter =    FlowMetric(name="Hydraulic Diameter", symbol="D_h", unit="m")
        self.free_stream_velocity =  FlowMetric(name="Freestream Velocity", symbol="U_inf", unit="m/s")
        self.kinematic_viscosity =   FlowMetric(name="Kinematic Viscosity", symbol="nu", unit="m²/s")
        self.reynolds_number =       FlowMetric(name="Reynolds Number", symbol="Re", unit="dimensionless")
        self.turb_intensity =        FlowMetric(name="Turbulence Intensity", symbol="I", unit="dimensionless")
        self.turb_kinetic_energy =   FlowMetric(name="Turbulence Kinetic Energy", symbol="k", unit="m²/s²")
        self.turb_length_scale =     FlowMetric(name="Turbulence Length Scale", symbol="l_t", unit="m")
        self.turb_dissipation_rate = FlowMetric(name="Turbulence Dissipation Rate", symbol="epsilon", unit="m²/s²")
        self.specific_dissipation =  FlowMetric(name="Specific Dissipation Rate", symbol="omega", unit="1/s")
        self.turb_viscosity =        FlowMetric(name="Turbulent Viscosity", symbol="nu_t", unit="m²/s")

        self.kinematic_viscosity.prompt = ("Typical values for kinematic viscosity (m²/s):\n"
                                           "  - Water: 0.000001\n  - Air: 0.0000148")

        if args is not None:
            self.initialise_user_arguments(args)
        self.perform_boundary_calculations()


    def initialise_user_arguments(self, args):
        # Initialise the user arguments
        self.hydraulic_diameter.value     = args.hydraulic_diameter
        self.free_stream_velocity.value   = args.free_stream_velocity
        self.kinematic_viscosity.value    = args.kinematic_viscosity
        self.reynolds_number.value        = args.reynolds_number
        self.turb_intensity.value         = args.turb_intensity
        self.turb_kinetic_energy.value    = args.turb_kinetic_energy
        self.turb_length_scale.value      = args.turb_length_scale
        self.turb_dissipation_rate.value  = args.turb_dissipation_rate
        self.specific_dissipation.value   = args.specific_dissipation
        self.turb_viscosity.value         = args.turb_viscosity


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


    @staticmethod
    def retrieve_vals(func_arg: float | None, class_arg: FlowMetric | None):
        """Method to prioritise and retrieve flow metrics"""
        if func_arg is not None:
            return func_arg
        elif class_arg is not None and class_arg.value is not None:
            return class_arg.value
        else:
            if class_arg.prompt is not None:
                print(class_arg.prompt)
            return get_positive_metric_input(prompt=f"Enter the {class_arg.description} ({class_arg.unit}): ")


    def calc_reynolds_number(
            self,
            turb_length_scale:float | None = None,
            free_stream_velocity: float | None = None,
            kinematic_viscosity:float | None = None) -> float:
        """Calculates the Reynolds Number from kinematic_viscosity, velocity, and length scale"""
        turb_length_scale = self.retrieve_vals(func_arg=turb_length_scale, class_arg=self.turb_length_scale)
        free_stream_velocity = self.retrieve_vals(func_arg=free_stream_velocity, class_arg=self.free_stream_velocity)
        kinematic_viscosity = self.retrieve_vals(func_arg=kinematic_viscosity, class_arg=self.kinematic_viscosity)
        return turb_length_scale * free_stream_velocity / kinematic_viscosity


    def calc_turb_intensity(self, reynolds_number:float | None=None) -> float:
        """Calculates the turbulent intensity from the Reynold's number"""
        turb_coefficient = 0.16
        reynolds_number = self.retrieve_vals(func_arg=reynolds_number, class_arg=self.reynolds_number)
        return turb_coefficient * reynolds_number ** (-1 / 8)


    def calc_turb_kinetic_energy(
            self,
            free_stream_velocity:float | None=None,
            turb_intensity:float | None=None) -> float:
        """Calculates the turbulent kinetic energy from velocity and turbulent intensity"""
        free_stream_velocity = self.retrieve_vals(func_arg=free_stream_velocity, class_arg=self.free_stream_velocity)
        turb_intensity = self.retrieve_vals(func_arg=turb_intensity, class_arg=self.turb_intensity)
        return (3 / 2) * (free_stream_velocity * turb_intensity) ** 2


    def calc_turb_length_scale(self, hydraulic_diameter: float | None=None) -> float:
        """Calculates the turbulent length scale from the hydraulic diameter"""
        coefficient_for_pipe_flow = 0.07
        hydraulic_diameter = self.retrieve_vals(func_arg=hydraulic_diameter, class_arg=self.hydraulic_diameter)
        return hydraulic_diameter * coefficient_for_pipe_flow


    def calc_turb_dissipation_rate(
            self,
            turb_kinetic_energy: float | None=None,
            turb_length_scale: float | None=None) -> float:
        """Calculates turbulent dissipation rate from turbulent kinetic energy and turbulent length scale"""
        model_function = 0.09
        turb_kinetic_energy = self.retrieve_vals(func_arg=turb_kinetic_energy, class_arg=self.turb_kinetic_energy)
        turb_length_scale = self.retrieve_vals(func_arg=turb_length_scale, class_arg=self.turb_length_scale)
        return model_function ** (3 / 4) * turb_kinetic_energy ** (3 / 2) / turb_length_scale


    def calc_specific_turb_dissipation_rate(
            self,
            turb_kinetic_energy: float | None=None,
            turb_length_scale: float | None=None) -> float:
        """Calculates specific turbulent dissipation rate from turbulent kinetic energy and turbulent length scale"""
        model_function = 0.09
        turb_kinetic_energy = self.retrieve_vals(func_arg=turb_kinetic_energy, class_arg=self.turb_kinetic_energy)
        turb_length_scale = self.retrieve_vals(func_arg=turb_length_scale, class_arg=self.turb_length_scale)
        return turb_kinetic_energy ** 0.5 / (model_function ** (1 / 4) * turb_length_scale)


    def calc_turb_viscosity_epsilon(
            self,
            turb_kinetic_energy: float | None=None,
            turb_dis_rate: float | None=None) -> float:
        """Calculates turbulent viscosity from turbulent kinetic energy and turbulent dissipation rate"""
        model_function = 0.09
        turb_kinetic_energy = self.retrieve_vals(func_arg=turb_kinetic_energy, class_arg=self.turb_kinetic_energy)
        turb_dis_rate = self.retrieve_vals(func_arg=turb_dis_rate, class_arg=self.turb_dis_rate)
        return model_function * turb_kinetic_energy ** 2 / turb_dis_rate


    @staticmethod
    def calc_kinematic_viscosity_air(temp_c: float, press_pa: float | None = None,
                                     press_atmos: float | None = None) -> float:
        """Compute kinematic viscosity of air (ν) from temperature (C) and pressure (Pa or atmospheres)"""

        # Validate pressure inputs
        if press_pa is not None and press_atmos is not None:
            raise ValueError("Specify pressure in either pascals OR atmospheres, not both.")
        if press_pa is None and press_atmos is None:
            raise ValueError("Must specify pressure in either pascals or atmospheres.")

        # Convert pressure if needed
        if press_atmos is not None:
            press_pa = press_atmos * 101325.0

        # Celsius to Kelvin conversion
        c_to_k = 273.15
        temp_k = temp_c + c_to_k

        # Specific gas constant for dry air - J/(kg·K)
        r_air = 287.058

        # Use Sutherland's law for dynamic viscosity and ideal gas relation for density.
        # Sutherland constants for air
        mu_0 = 1.716e-5  # reference dynamic viscosity at temp_0 (Pa·s)
        temp_0 = c_to_k  # reference temperature (K)
        c_sutherland = 111.0  # Sutherland constant (K)

        # Dynamic viscosity via Sutherland's law
        mu = mu_0 * ((temp_k / temp_0) ** 1.5) * (temp_0 + c_sutherland) / (temp_k + c_sutherland)

        # Density from ideal gas equation
        rho = press_pa / (r_air * temp_k)

        # Kinematic viscosity
        return mu / rho


    @staticmethod
    def calc_kinematic_viscosity_water(temp_c: float) -> float:
        """Compute kinematic viscosity of liquid water (ν) from temperature (C)"""

        # Check that the temperature is between 0 and 100 Celsius
        if not 0 < temp_c < 100:
            raise ValueError('Temperature must be between 0 and 100')

        # Dynamic viscosity approximation for water (Pa·s)
        mu = 2.414e-5 * 10 ** (247.8 / (temp_c + 133.15))

        # Density approximation for water (kg/m^3)
        rho = 1000 * (1 - (temp_c + 288.9414) / (508929.2 * (temp_c + 68.12963)) * (temp_c - 3.9863) ** 2)

        # Kinematic viscosity
        return mu / rho