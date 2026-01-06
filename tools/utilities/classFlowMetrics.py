#!/usr/bin/python

import sys
from .argsRetriever import get_positive_metric_input, get_valid_text_input

class FlowMetric:
    """A class to define the attributes of a flow metric"""
    def __init__(self, name: str, kind: str = None, symbol: str = None, value: float = None, unit: str = None, prompt: str = None):
        self.name = name
        self.kind = kind
        self.symbol = symbol
        self.value = value
        self.unit = unit
        self.prompt = prompt


class FlowMetrics:
    """A class to contain all flow metrics"""

    def __init__(self, args=None):
        # Initialize all metrics as FlowMetric objects
        self.fluid_type =            FlowMetric(name="Type of Fluid")
        self.hydraulic_diameter =    FlowMetric(name="Hydraulic Diameter", symbol="D_h", unit="m")
        self.freestream_velocity =   FlowMetric(name="Freestream Velocity", symbol="U_inf", unit="m/s")
        self.freestream_pressure =   FlowMetric(name="Freestream Pressure", symbol="P_inf", unit="Pa")
        self.kinematic_viscosity =   FlowMetric(name="Kinematic Viscosity", symbol="nu", unit="m²/s")
        self.reynolds_number =       FlowMetric(name="Reynolds Number", symbol="Re", unit="dimensionless")
        self.temperature =           FlowMetric(name="Temperature", symbol="T", unit="°C")
        self.turb_intensity =        FlowMetric(name="Turbulence Intensity", symbol="I", unit="dimensionless")
        self.turb_kinetic_energy =   FlowMetric(name="Turbulence Kinetic Energy", symbol="k", unit="m²/s²")
        self.turb_length_scale =     FlowMetric(name="Turbulence Length Scale", symbol="l_t", unit="m")
        self.turb_dissipation_rate = FlowMetric(name="Turbulence Dissipation Rate", symbol="epsilon", unit="m²/s²")
        self.turb_spec_dissip_rate = FlowMetric(name="Specific Dissipation Rate", symbol="omega", unit="1/s")
        self.turb_viscosity =        FlowMetric(name="Turbulent Viscosity", symbol="nu_t", unit="m²/s")

        self.fluid_type.prompt = "Supported Fluids are: [water, air]"
        self.freestream_pressure.prompt = "Typical atmospheric pressure is 101325 Pa"
        self.kinematic_viscosity.prompt = "Typical kinematic viscosity (m/s) is: \n- Water: 0.000001\n- Air: 0.0000148"

        if args is not None:
            self.initialise_user_arguments(args)
        self.perform_boundary_calculations()


    def initialise_user_arguments(self, args):
        # Initialise the user arguments
        self.hydraulic_diameter.value     = args.hydraulic_diameter
        self.freestream_velocity.value    = args.freestream_velocity
        self.kinematic_viscosity.value    = args.kinematic_viscosity
        self.reynolds_number.value        = args.reynolds_number
        self.turb_intensity.value         = args.turb_intensity
        self.turb_kinetic_energy.value    = args.turb_kinetic_energy
        self.turb_length_scale.value      = args.turb_length_scale
        self.turb_dissipation_rate.value  = args.turb_dissipation_rate
        self.turb_spec_dissip_rate.value  = args.turb_spec_dissip_rate
        self.turb_viscosity.value         = args.turb_viscosity


    def perform_boundary_calculations(self):
        """Perform calculations only if the value is missing."""
        calculations = [(self.reynolds_number, self.calc_reynolds_number),
                        (self.turb_intensity, self.calc_turb_intensity),
                        (self.turb_kinetic_energy, self.calc_turb_kinetic_energy),
                        (self.turb_length_scale, self.calc_turb_length_scale),
                        (self.turb_dissipation_rate, self.calc_turb_dissipation_rate),
                        (self.turb_spec_dissip_rate, self.calc_specific_turb_dissipation_rate),
                        (self.turb_viscosity, self.calc_turb_viscosity_epsilon)]
        for flow_metric, calc_function in calculations:
            if flow_metric.value is None:
                flow_metric.value = calc_function()


    def __repr__(self):
        """Custom string representation for easy visualization of results"""
        lines = []
        for attr in vars(self):
            metric = getattr(self, attr)
            if isinstance(metric, FlowMetric):
                # Handle None values to avoid TypeError during formatting
                formatted_val = "None" if metric.value is None else f"{metric.value: .3g}"
                lines.append(f"{attr} ({metric.symbol}): {formatted_val}")
        return "\n".join(lines)


    # ------------------- Selection Methods -------------------

    @staticmethod
    def choose_val(func_arg: float | None, flow_metric: FlowMetric | None):
        """Method to prioritise and retrieve flow metrics"""
        if func_arg is not None:
            return func_arg
        elif flow_metric is not None and flow_metric.value is not None:
            return flow_metric.value
        else:
            if flow_metric.prompt is not None:
                print(flow_metric.prompt)
            user_input = get_positive_metric_input(prompt=f"Enter the {flow_metric.name} ({flow_metric.unit}): ")
            flow_metric.value = user_input
            return user_input


    @staticmethod
    def choose_kind(func_arg: float | None, flow_metric: FlowMetric | None):
        """Method to prioritise and retrieve flow metrics"""
        if func_arg is not None:
            return func_arg
        elif flow_metric is not None and flow_metric.kind is not None:
            return flow_metric.kind
        else:
            if flow_metric.prompt is not None:
                print(flow_metric.prompt)
            user_input = get_valid_text_input(prompt=f"Enter the {flow_metric.name}: ").lower()
            flow_metric.kind = user_input
            return user_input


    # ------------------- Calculation Methods -------------------

    def calc_kinematic_viscosity(
            self, fluid_type: float | None = None,
            temperature: float | None = None,
            freestream_pressure: float | None = None) -> float:
        """Calculates the kinematic viscosity based on the type of fluid and temperature"""
        fluid_type = self.choose_kind(func_arg=fluid_type, flow_metric=self.fluid_type)
        temperature = self.choose_val(func_arg=temperature, flow_metric=self.temperature)
        if fluid_type.lower == "water":
            kinematic_viscosity = self.calc_kinematic_viscosity_water(temperature)
        elif fluid_type.lower() == "air":
            freestream_pressure = self.choose_val(func_arg=freestream_pressure, flow_metric=self.freestream_pressure)
            kinematic_viscosity = self.calc_kinematic_viscosity_air(temp_c=temperature, press_pa=freestream_pressure)
        else:
            sys.exit(f"Invalid fluid type: {fluid_type}")
        return kinematic_viscosity


    def calc_reynolds_number(
            self,
            hydraulic_diameter:float | None = None,
            free_stream_velocity: float | None = None,
            kinematic_viscosity:float | None = None) -> float:
        """Calculates the Reynolds Number from kinematic_viscosity, velocity, and length scale"""
        hydraulic_diameter = self.choose_val(func_arg=hydraulic_diameter, flow_metric=self.hydraulic_diameter)
        free_stream_velocity = self.choose_val(func_arg=free_stream_velocity, flow_metric=self.freestream_velocity)
        kinematic_viscosity = self.choose_val(func_arg=kinematic_viscosity, flow_metric=self.kinematic_viscosity)
        return  hydraulic_diameter * free_stream_velocity / kinematic_viscosity


    def calc_turb_intensity(self, reynolds_number:float | None=None) -> float:
        """Calculates the turbulent intensity from the Reynold's number"""
        turb_coefficient = 0.16
        reynolds_number = self.choose_val(func_arg=reynolds_number, flow_metric=self.reynolds_number)
        return turb_coefficient * reynolds_number ** (-1 / 8)


    def calc_turb_kinetic_energy(
            self,
            free_stream_velocity:float | None=None,
            turb_intensity:float | None=None) -> float:
        """Calculates the turbulent kinetic energy from velocity and turbulent intensity"""
        free_stream_velocity = self.choose_val(func_arg=free_stream_velocity, flow_metric=self.freestream_velocity)
        turb_intensity = self.choose_val(func_arg=turb_intensity, flow_metric=self.turb_intensity)
        return (3 / 2) * (free_stream_velocity * turb_intensity) ** 2


    def calc_turb_length_scale(self, hydraulic_diameter: float | None=None) -> float:
        """Calculates the turbulent length scale from the hydraulic diameter"""
        coefficient_for_pipe_flow = 0.07
        hydraulic_diameter = self.choose_val(func_arg=hydraulic_diameter, flow_metric=self.hydraulic_diameter)
        return hydraulic_diameter * coefficient_for_pipe_flow


    def calc_turb_dissipation_rate(
            self,
            turb_kinetic_energy: float | None=None,
            turb_length_scale: float | None=None) -> float:
        """Calculates turbulent dissipation rate from turbulent kinetic energy and turbulent length scale"""
        model_function = 0.09
        turb_kinetic_energy = self.choose_val(func_arg=turb_kinetic_energy, flow_metric=self.turb_kinetic_energy)
        turb_length_scale = self.choose_val(func_arg=turb_length_scale, flow_metric=self.turb_length_scale)
        return model_function ** (3 / 4) * turb_kinetic_energy ** (3 / 2) / turb_length_scale


    def calc_specific_turb_dissipation_rate(
            self,
            turb_kinetic_energy: float | None=None,
            turb_length_scale: float | None=None) -> float:
        """Calculates specific turbulent dissipation rate from turbulent kinetic energy and turbulent length scale"""
        model_function = 0.09
        turb_kinetic_energy = self.choose_val(func_arg=turb_kinetic_energy, flow_metric=self.turb_kinetic_energy)
        turb_length_scale = self.choose_val(func_arg=turb_length_scale, flow_metric=self.turb_length_scale)
        return turb_kinetic_energy ** 0.5 / (model_function ** (1 / 4) * turb_length_scale)


    def calc_turb_viscosity_epsilon(
            self,
            turb_kinetic_energy: float | None=None,
            turb_dissipation_rate: float | None=None) -> float:
        """Calculates turbulent viscosity from turbulent kinetic energy and turbulent dissipation rate"""
        model_function = 0.09
        turb_kinetic_energy = self.choose_val(func_arg=turb_kinetic_energy, flow_metric=self.turb_kinetic_energy)
        turb_dissipation_rate = self.choose_val(func_arg=turb_dissipation_rate, flow_metric=self.turb_dissipation_rate)
        return model_function * turb_kinetic_energy ** 2 / turb_dissipation_rate


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