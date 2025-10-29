#!/usr/bin/python

def calc_kinematic_viscosity_air(temp_c: float, press_pa: float | None=None, press_atmos: float | None=None) -> float:
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


print(calc_kinematic_viscosity_air(20, 100))