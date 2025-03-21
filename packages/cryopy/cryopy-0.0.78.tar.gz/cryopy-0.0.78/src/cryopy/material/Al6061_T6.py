import numpy as np
from cryopy.material import plot


def molar_mass() -> float:
    """
    Returns the molar mass of Aluminium 6061-T6.

    Returns:
    --------
    float
        The molar mass in kg/mol.
    """
    return 0.027  # kg/mol


def molar_volume(temperature: float) -> float:
    """
    Computes the molar volume of Aluminium 6061-T6.

    Parameters:
    -----------
    temperature : float
        The temperature of the material in Kelvin (K).

    Returns:
    --------
    float
        The molar volume in m³/mol.

    Raises:
    -------
    ValueError
        If the temperature is out of the valid range for `density()`.
    """

    try:
        result = molar_mass() / density(temperature)
    except ValueError as e:
        raise ValueError(f"Invalid temperature: {temperature}K. {e}")

    return result



def plot_molar_volume(grid: bool = True, xscale: str = 'linear', yscale: str = 'linear') -> None:
    """
    Plots the molar volume of Aluminium 6061-T6 as a function of temperature.

    Parameters:
    -----------
    grid : bool, optional
        Whether to display a grid on the plot (default is True).

    xscale : str, optional
        Scale type for the x-axis ('linear' or 'log', default is 'linear').

    yscale : str, optional
        Scale type for the y-axis ('linear' or 'log', default is 'linear').

    Returns:
    --------
    None
        Displays the  plot.
    """
    
    ARRAY_x = np.arange(4,300,0.1)
    ARRAY_y = [molar_volume(temperature) for temperature in ARRAY_x]
    
    plot(ARRAY_x = ARRAY_x,
         ARRAY_y = ARRAY_y,
         xlabel = 'Temperature [K]',
         ylabel = r'Molar volume [m$^{3}$.mol$^{-1}$]',
         grid = True,
         xscale = 'log',
         yscale = 'linear',
         title = 'Molar volume of Al6061-T6 against the temperature')
    
    
def specific_heat(temperature: float, unit: str) -> float:
    """
    Computes the specific heat of Aluminium 6061-T6 in either 'mol' or 'kg' units.

    Valid temperature range: 3K to 300K.

    Reference:
    https://trc.nist.gov/cryogenics/materials/6061%20Aluminum/6061_T6Aluminum_rev.htm

    Parameters:
    -----------
    temperature : float
        The temperature of the material in Kelvin (K).
        Must be within the range [3, 300].

    unit : str
        The unit of specific heat, either 'mol' or 'kg'.

    Returns:
    --------
    float
        The specific heat in either [J/(mol·K)] or [J/(kg·K)], depending on the unit.

    Raises:
    -------
    ValueError
        If the temperature is out of range.
        If the unit is not 'mol' or 'kg'.
    """
    
    # Validate input
    if not (3 <= temperature <= 300):
        raise ValueError(f"Temperature {temperature}K is out of the valid range [3, 300]K.")
    
    if unit not in {'mol', 'kg'}:
        raise ValueError(f"Invalid unit '{unit}'. Expected 'mol' or 'kg'.")

    # Polynomial coefficients
    coefficients = np.array([46.6467, -314.292, 866.662, -1298.3, 
                             1162.27, -637.795, 210.351, -38.3094, 2.96344])

    # Compute specific heat
    log_temp = np.log10(temperature)
    result = sum(coeff * (log_temp ** i) for i, coeff in enumerate(coefficients))
    
    return 10 ** result


def plot_specific_heat(grid: bool = True, xscale: str = 'linear', yscale: str = 'linear') -> None:
    """
    Plots the specific heat of Aluminium 6061-T6 as a function of temperature.

    Parameters:
    -----------
    grid : bool, optional
        Whether to display a grid on the plot (default is True).

    xscale : str, optional
        Scale type for the x-axis ('linear' or 'log', default is 'linear').

    yscale : str, optional
        Scale type for the y-axis ('linear' or 'log', default is 'linear').

    Returns:
    --------
    None
        Displays the  plot.
    """
    
    ARRAY_x = np.arange(3,300,0.1)
    ARRAY_y = [specific_heat(temperature,'kg') for temperature in ARRAY_x]
    
    plot(ARRAY_x = ARRAY_x,
         ARRAY_y = ARRAY_y,
         xlabel = 'Temperature [K]',
         ylabel = r'Specific heat [J.kg$^{-1}$.K$^{-1}$]',
         grid = True,
         xscale = 'log',
         yscale = 'log',
         title = 'Specific heat of Al6061-T6 against the temperature')
    
    ARRAY_y = [specific_heat(temperature,'mol') for temperature in ARRAY_x]
    
    plot(ARRAY_x = ARRAY_x,
         ARRAY_y = ARRAY_y,
         xlabel = 'Temperature [K]',
         ylabel = r'Specific heat [J.mol$^{-1}$.K$^{-1}$]',
         grid = True,
         xscale = 'log',
         yscale = 'log',
         title = 'Specific heat of Al6061-T6 against the temperature')


def linear_thermal_expansion(temperature: float) -> float:
    """
    Computes the linear thermal expansion of Aluminium 6061-T6.

    Valid temperature range: 4K to 300K.

    Reference:
    https://trc.nist.gov/cryogenics/materials/304LStainless/304LStainless_rev.htm

    Parameters:
    -----------
    temperature : float
        The temperature of the material in Kelvin (K).
        Must be within the range [4, 300].

    Returns:
    --------
    float
        The linear thermal expansion (unitless).

    Raises:
    -------
    ValueError
        If the temperature is out of range.
    """

    # Validate input
    if not (4 <= temperature <= 300):
        raise ValueError(f"Temperature {temperature}K is out of the valid range [4, 300]K.")

    # Polynomial coefficients
    coefficients = np.array([-4.1277e2, -3.0389e-1, 8.7696e-3, -9.9821e-6, 0])

    # Compute linear thermal expansion
    result = sum(coeff * (temperature ** i) for i, coeff in enumerate(coefficients))

    return result * 1e-5


def plot_linear_thermal_expansion(grid: bool = True, xscale: str = 'linear', yscale: str = 'linear') -> None:
    
    """
    Plots the linear thermal expansion of Aluminium 6061-T6 as a function of temperature.

    Parameters:
    -----------
    grid : bool, optional
        Whether to display a grid on the plot (default is True).

    xscale : str, optional
        Scale type for the x-axis ('linear' or 'log', default is 'linear').

    yscale : str, optional
        Scale type for the y-axis ('linear' or 'log', default is 'linear').

    Returns:
    --------
    None
        Displays the  plot.
    """
    
    ARRAY_x = np.arange(4,300,0.1)
    ARRAY_y = [linear_thermal_expansion(temperature) for temperature in ARRAY_x]
    
    plot(ARRAY_x = ARRAY_x,
         ARRAY_y = ARRAY_y,
         xlabel = 'Temperature [K]',
         ylabel = r'Linear thermal expansion [1]',
         grid = True,
         xscale = 'log',
         yscale = 'linear',
         title = 'Linear thermal expansion of Al6061-T6 against the temperature')


def young_modulus(temperature: float) -> float:
    """
    Computes the Young's modulus of Aluminium 6061-T6.

    Valid temperature range: 0K to 295K.

    Reference:
    https://trc.nist.gov/cryogenics/materials/5083%20Aluminum/5083Aluminum_rev.htm

    Parameters:
    -----------
    temperature : float
        The temperature of the material in Kelvin (K).
        Must be within the range [0, 295].

    Returns:
    --------
    float
        The Young's modulus in Pascals (Pa).

    Raises:
    -------
    ValueError
        If the temperature is out of range.
    """

    # Validate input
    if not (0 <= temperature <= 295):
        raise ValueError(f"Temperature {temperature}K is out of the valid range [0, 295]K.")

    # Polynomial coefficients
    coefficients = np.array([7.771221e1, 1.030646e-2, -2.924100e-4, 
                             8.993600e-7, -1.070900e-9])

    # Compute Young's modulus
    result = sum(coeff * (temperature ** i) for i, coeff in enumerate(coefficients))

    return result * 1e9  # Convert to Pascals



def plot_young_modulus(grid: bool = True, xscale: str = 'linear', yscale: str = 'linear') -> None:
    """
    Plots the Young modulus of Aluminium 6061-T6 as a function of temperature.

    Parameters:
    -----------
    grid : bool, optional
        Whether to display a grid on the plot (default is True).

    xscale : str, optional
        Scale type for the x-axis ('linear' or 'log', default is 'linear').

    yscale : str, optional
        Scale type for the y-axis ('linear' or 'log', default is 'linear').

    Returns:
    --------
    None
        Displays the  plot.
    """
    
    ARRAY_x= np.arange(0,295,0.1)
    ARRAY_y = [young_modulus(temperature) for temperature in ARRAY_x]
    
    plot(ARRAY_x = ARRAY_x,
         ARRAY_y = ARRAY_y,
         xlabel = 'Temperature [K]',
         ylabel = r'Young modulus [Pa]',
         grid = True,
         xscale = 'log',
         yscale = 'linear',
         title = 'Young modulus of Al6061-T6 against the temperature')



def density(temperature: float) -> float:
    """
    Computes the density of Aluminium 6061-T6 as a function of temperature.

    Parameters:
    -----------
    temperature : float
        The temperature of the material in Kelvin (K).

    Returns:
    --------
    float
        The density in kg/m³.

    Raises:
    -------
    ValueError
        If the temperature is out of the valid range for `linear_thermal_expansion()`.
    """

    try:
        expansion_coefficient = (linear_thermal_expansion(temperature) + 1) ** 3
    except ValueError as e:
        raise ValueError(f"Invalid temperature: {temperature}K. {e}")

    density_293K = 2701  # Reference density at 293K in kg/m³

    return density_293K / expansion_coefficient  # Inverse relation due to expansion


def plot_density(grid: bool = True, xscale: str = 'linear', yscale: str = 'linear') -> None:
    """
    Plots the density of Aluminium 6061-T6 as a function of temperature.

    Parameters:
    -----------
    grid : bool, optional
        Whether to display a grid on the plot (default is True).

    xscale : str, optional
        Scale type for the x-axis ('linear' or 'log', default is 'linear').

    yscale : str, optional
        Scale type for the y-axis ('linear' or 'log', default is 'linear').

    Returns:
    --------
    None
        Displays the  plot.
    """
    
    ARRAY_x= np.arange(4,300,0.1)
    ARRAY_y = [density(temperature) for temperature in ARRAY_x]
    
    plot(ARRAY_x = ARRAY_x,
         ARRAY_y = ARRAY_y,
         xlabel = 'Temperature [K]',
         ylabel = r'Density [kg.m$^{-3}$]',
         grid = grid,
         xscale = xscale,
         yscale = yscale,
         title = 'Density of Al6061-T6 against the temperature')


def thermal_conductivity(temperature: float, source: str = 'NIST') -> float:
    """
    Computes the thermal conductivity of Aluminium 6061-T6.

    Parameters:
    -----------
    temperature : float
        The temperature of the material in Kelvin (K).

    source : string
        The data origin, could be 'NIST', 'BARUCCI' or 'SAUVAGE'
    Returns:
    --------
    float
        The thermal conductivity in W/(m·K).

    Raises:
    -------
    ValueError
        If the temperature is out of range.
    """
    # Validate input

    if source == 'NIST':
    
        if not (3 <= temperature <= 300):
            raise ValueError(f"Temperature {temperature}K is out of the valid range [3, 300]K.")
        
        # Polynomial coefficients
        coefficients = np.array([0.07918, 1.0967, -0.07277, 0.08084, 0.02803, 
                                 -0.09464, 0.04179, -0.00571])
    
        # Compute thermal conductivity
        log_temp = np.log10(temperature)
        result = sum(coeff * (log_temp ** i) for i, coeff in enumerate(coefficients))
    
        return 10 ** result  # Convert from log scale
    
    if source == 'BARUCCI':
    
        if not (4.2 <= temperature <= 70):
            raise ValueError(f"Temperature {temperature}K is out of the valid range [4.2, 70]K.")
        
        result = temperature / (0.445 + 4.9e-7 * temperature ** 3)
    
        return result

    if source == 'SAUVAGE':
    
        if not (3 <= temperature <= 300):
            raise ValueError(f"Temperature {temperature}K is out of the valid range [3, 300]K.")
        
        # Polynomial coefficients
        coefficients = np.array([2.39703410e-01, 1.88576787e+00, -4.39839595e-01, 9.53687043e-02,
                    2.05443158e-03, -2.89908152e-03, -1.33420775e-04, 1.14453429e-04,
                    -8.72830666e-06])
    
        # Compute thermal conductivity
        result = np.polynomial.chebyshev.chebval(np.log(temperature), coefficients)
    
        return np.exp(result)
    

def plot_thermal_conductivity(grid: bool = True, xscale: str = 'log', yscale: str = 'log') -> None:
    
    """
    Plots the thermal conductivity of Aluminium 6061-T6 as a function of temperature.

    Parameters:
    -----------
    grid : bool, optional
        Whether to display a grid on the plot (default is True).

    xscale : str, optional
        Scale type for the x-axis ('linear' or 'log', default is 'linear').

    yscale : str, optional
        Scale type for the y-axis ('linear' or 'log', default is 'linear').

    Returns:
    --------
    None
        Displays the  plot.
    """
    
    ARRAY_x= np.arange(4,300,0.1)
    ARRAY_y = [thermal_conductivity(temperature) for temperature in ARRAY_x]
    
    plot(ARRAY_x = ARRAY_x,
         ARRAY_y = ARRAY_y,
         xlabel = 'Temperature [K]',
         ylabel = r'Thermal conductivity [W.m$^{-1}$.K$^{-1}$]',
         grid = grid,
         xscale = xscale,
         yscale = yscale,
         title = 'Thermal conductivity of Al6061-T6 against the temperature')
    
    



