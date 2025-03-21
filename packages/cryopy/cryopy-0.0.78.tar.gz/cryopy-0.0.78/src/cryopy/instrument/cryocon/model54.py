#!/usr/bin/env python3

import pyvisa
import logging
import numpy as np

# Configure logger
logger = logging.getLogger(__name__)

def query_identification(instrument: pyvisa.resources.Resource) -> tuple[str, str, str, str]:
    """
    Retrieves the identification information of the Cryocon Model 54.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa instrument connection instance.

    Returns:
    --------
    tuple[str, str, str, str]
        A tuple containing:
        - manufacturer (str): Should be "Cryo-con".
        - model (str): Should be "Model 54".
        - serial (str): Instrument-specific serial number.
        - firmware_version (str): Instrument-specific firmware version.

    Raises:
    -------
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    ValueError
        If the response format is unexpected.
    Exception
        For any other unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    manufacturer, model, serial, firmware_version = query_identification(instrument)
    """

    try:
        # Ensure instrument session is open
        if not instrument.session:
            raise pyvisa.VisaIOError("Instrument session is closed.")

        # Query identification string
        answer = instrument.query('*IDN?').strip()

        # Parse response
        parts = answer.split(',')
        if len(parts) < 4:
            raise ValueError(f"Unexpected response format: {answer}")

        manufacturer, model, serial, firmware_version = parts[:4]

        logger.info(f"Queried ID: {manufacturer}, {model}, {serial}, {firmware_version}")
        return manufacturer, model, serial, firmware_version

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle

    except ValueError as e:
        logger.error(f"Invalid response from instrument: {e}")
        raise  # Re-raise ValueError for debugging

    except Exception as e:
        logger.error(f"Unexpected error while querying identification: {e}")
        raise  # Re-raise any other unexpected error


def query_input(instrument: pyvisa.resources.Resource, channel: str) -> float:
    """
    Retrieves the input measurement from a given channel of the Cryocon Model 54.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa instrument connection instance.
    channel : str
        The channel to query ('a', 'b', 'c', or 'd').

    Returns:
    --------
    float
        The measured input value in [K] or [Ohm]. Returns NaN if parsing fails.

    Raises:
    -------
    ValueError
        If the channel is invalid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any other unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    input_value = query_input(instrument, 'a')
    """

    try:
        # Validate channel input
        if channel not in ('a', 'b', 'c', 'd'):
            raise ValueError("Invalid channel. Must be 'a', 'b', 'c', or 'd'.")

        # Ensure instrument session is open
        if not instrument.session:
            raise pyvisa.VisaIOError("Instrument session is closed.")

        # Query instrument for input value
        answer = instrument.query(f'input? {channel}').strip()

        # Convert response to float
        value = float(answer)
        logger.info(f"Queried input from channel {channel}: {value}")
        return value

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle

    except ValueError as e:
        logger.error(f"Invalid response or input error: {e}")
        return np.nan  # Return NaN if parsing fails

    except Exception as e:
        logger.error(f"Unexpected error while querying input: {e}")
        raise  # Re-raise any other unexpected error
        

def control_sensor_unit(instrument: pyvisa.resources.Resource, channel: str, unit: str) -> None:
    """
    Controls the unit of a given channel on the Cryocon Model 54.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa instrument connection instance.
    channel : str
        The channel to configure ('a', 'b', 'c', or 'd').
    unit : str
        The unit to set ('k' for Kelvin, 's' for sensor).

    Raises:
    -------
    ValueError
        If the channel or unit is invalid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any other unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    control_sensor_unit(instrument, 'a', 'k')
    """

    try:
        # Validate channel input
        if channel not in ('a', 'b', 'c', 'd'):
            raise ValueError("Invalid channel. Must be 'a', 'b', 'c', or 'd'.")

        # Validate unit input
        if unit not in ('k', 's'):
            raise ValueError("Invalid unit. Must be 'k' (Kelvin) or 's' (sensor).")

        # Ensure instrument session is open
        if not instrument.session:
            raise pyvisa.VisaIOError("Instrument session is closed.")

        # Send command to configure the unit
        command = f'input {channel}:unit {unit}'
        instrument.write(command)

        logger.info(f"Set unit of channel {channel} to {unit}")

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle

    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise  # Re-raise ValueError for debugging

    except Exception as e:
        logger.error(f"Unexpected error while setting sensor unit: {e}")
        raise  # Re-raise any other unexpected error

