#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa
import logging

# Set up logging for the module
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


#%% INSTRUMENT PARAMETERS
# INSTRUMENT ADDRESS
ADDRESS = "GPIB0::26::INSTR" 

# INSTRUMENT INITIALISATION
rm = pyvisa.ResourceManager()
instrument = rm.open_resource(ADDRESS)



def command_reset(instrument: pyvisa.resources.Resource, channel: str) -> None:
    """
    Resets the parameters of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b'.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_reset(instrument, 'a')
    """
    
    try:
        # Validate channel input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        
        # Construct reset command
        command = f"smu{channel}.reset()"
        
        # Send reset command to instrument
        instrument.write(command)
        
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle



def command_current_measure_autorange(instrument: pyvisa.resources.Resource, channel: str, autorange: str) -> None:
    """
    Enables or disables the autorange of the current measurement for a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    autorange : str
        The autorange status ('ON' or 'OFF').

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', or if autorange is not 'ON' or 'OFF'.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_current_measure_autorange(instrument, 'a', 'ON')
    """
    
    try:
        # Validate inputs
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if autorange not in ('ON', 'OFF'):
            raise ValueError("Invalid autorange status. Must be 'ON' or 'OFF'.")
        
        # Construct autorange command
        command = f"smu{channel}.measure.autorangei=smu{channel}.AUTORANGE_{autorange}"
        
        # Send autorange command to instrument
        instrument.write(command)
        
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle


# %%
def command_voltage_measure_autorange(instrument: pyvisa.resources.Resource, channel: str, autorange: str) -> None:
    """
    Enables or disables the autorange of the voltage measurement for a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    autorange : str
        The autorange status ('ON' or 'OFF').

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', or if autorange is not 'ON' or 'OFF'.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_voltage_measure_autorange(instrument, 'a', 'ON')
    """
    
    try:
        # Validate inputs
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if autorange not in ('ON', 'OFF'):
            raise ValueError("Invalid autorange status. Must be 'ON' or 'OFF'.")
        
        # Construct autorange command
        command = f"smu{channel}.measure.autorangev=smu{channel}.AUTORANGE_{autorange}"
        
        # Send autorange command to instrument
        instrument.write(command)
        
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle


def command_current_measure_range(instrument: pyvisa.resources.Resource, channel: str, range_value: int) -> None:
    """
    Sets the range of the current measurement for a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    range_value : int
        The range value (0 = 100 nA, 1 = 1 uA, 2 = 10 uA, 3 = 100 uA,
                       4 = 1 mA, 5 = 10 mA, 6 = 100 mA, 7 = 1 A, 8 = 3 A).

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', or if range_value is out of range.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_current_measure_range(instrument, 'a', 4)
    """
    
    try:
        # Validate inputs
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if not (0 <= range_value <= 8):
            raise ValueError("Invalid range value. Must be between 0 and 8.")
        
        # Map range index to actual current range values
        intensity_range = ['100e-9', '1e-6', '10e-6', '100e-6', '1e-3', '10e-3', '100e-3', '1', '3']
        selected_range = intensity_range[range_value]
        
        # Construct range command
        command = f"smu{channel}.measure.rangev={selected_range}"
        
        # Send range command to instrument
        instrument.write(command)
        
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle




def query_current(instrument: pyvisa.resources.Resource, channel: str) -> float:
    """
    Queries the measured current of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').

    Returns:
    --------
    float
        The measured current in amperes (A).

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b'.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    current = query_current(instrument, 'a')
    print(f"Measured current: {current} A")
    """
    
    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        
        # Construct query command
        command = f"print(smu{channel}.measure.i())"
        
        # Send query and parse response
        response = instrument.query(command).strip()
        current = float(response)
        
        return current
    
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle
        

def query_resistance(instrument: pyvisa.resources.Resource, channel: str) -> float:
    """
    Queries the measured resistance of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').

    Returns:
    --------
    float
        The measured resistance in ohms (Ohms).

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b'.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    resistance = query_resistance(instrument, 'a')
    print(f"Measured resistance: {current} Ohms")
    """
    
    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        
        # Construct query command
        command = f"print(smu{channel}.measure.r())"
        
        # Send query and parse response
        response = instrument.query(command).strip()
        resistance = float(response)
        
        return resistance
    
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle


def query_voltage(instrument: pyvisa.resources.Resource, channel: str) -> float:
    """
    Queries the measured voltage of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').

    Returns:
    --------
    float
        The measured voltage in volts (V).

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b'.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    voltage = query_voltage(instrument, 'a')
    print(f"Measured voltage: {voltage} V")
    """
    
    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        
        # Construct query command
        command = f"print(smu{channel}.measure.v())"
        
        # Send query and parse response
        response = instrument.query(command).strip()
        voltage = float(response)
        
        return voltage
    
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle


def query_power(instrument: pyvisa.resources.Resource, channel: str) -> float:
    """
    Queries the measured power of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').

    Returns:
    --------
    float
        The measured power in watts (W).

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b'.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    power = query_power(instrument, 'a')
    print(f"Measured power: {power} W")
    """
    
    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        
        # Construct query command
        command = f"print(smu{channel}.measure.p())"
        
        # Send query and parse response
        response = instrument.query(command).strip()
        power = float(response)
        
        return power
    
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle






def command_current_source_autorange(instrument: pyvisa.resources.Resource, channel: str, autorange: str) -> None:
    """
    Enables or disables the autorange of the current source for a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    autorange : str
        The autorange status ('ON' or 'OFF').

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', or if the autorange value is not 'ON' or 'OFF'.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_current_source_autorange(instrument, 'a', 'ON')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if autorange not in ('ON', 'OFF'):
            raise ValueError("Invalid autorange value. Must be 'ON' or 'OFF'.")

        # Construct command
        command = f"smu{channel}.source.autorangei = smu{channel}.AUTORANGE_{autorange}"

        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def command_voltage_source_autorange(instrument: pyvisa.resources.Resource, channel: str, autorange: str) -> None:
    """
    Enables or disables the autorange of the voltage source for a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    autorange : str
        The autorange status ('ON' or 'OFF').

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', or if the autorange value is not 'ON' or 'OFF'.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_voltage_source_autorange(instrument, 'a', 'ON')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if autorange not in ('ON', 'OFF'):
            raise ValueError("Invalid autorange value. Must be 'ON' or 'OFF'.")

        # Construct command
        command = f"smu{channel}.source.autorangev = smu{channel}.AUTORANGE_{autorange}"

        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise
        
        


def command_source(instrument: pyvisa.resources.Resource, channel: str, source: str) -> None:
    """
    Swap the source type between AMPS and VOLTS for a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    source : str
        The source type ('AMPS' or 'VOLTS').

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', or if the source type is not 'AMPS' or 'VOLTS'.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_source(instrument, 'a', 'AMPS')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if source not in ('AMPS', 'VOLTS'):
            raise ValueError("Invalid source type. Must be 'AMPS' or 'VOLTS'.")

        # Construct command
        command = f"smu{channel}.source.func = smu{channel}.OUTPUT_DC{source}"

        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise



def command_source_current_value(instrument: pyvisa.resources.Resource, channel: str, output: float) -> None:
    """
    Define the current value output of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    output : float
        The current output value.

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', and if output if a float
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_source_current_value(instrument, 'a', 'A')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if not isinstance(output,float) :
            raise ValueError("Invalid output value. Must be a float.")

        # Construct command
        command = f"smu{channel}.source.leveli = {output}"

        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def command_source_voltage_value(instrument: pyvisa.resources.Resource, channel: str, output: float) -> None:
    """
    Define the voltage value output of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    output : float
        The voltage output value.

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', and if output if a float
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_voltage_current_value(instrument, 'a', 'A')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if not isinstance(output,float) :
            raise ValueError("Invalid output value. Must be a float.")

        # Construct command
        command = f"smu{channel}.source.levelv = {output}"

        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def command_source_current_limit(instrument: pyvisa.resources.Resource, channel: str, limit: float) -> None:
    """
    Define the current value limit of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    limit : float
        The current output value.

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', and if limit if a float
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_source_current_limit(instrument, 'a', 'A')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if not isinstance(limit,float) :
            raise ValueError("Invalid output value. Must be a float.")

        # Construct command
        command = f"smu{channel}.source.limiti = {limit}"

        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def command_source_voltage_limit(instrument: pyvisa.resources.Resource, channel: str, limit: float) -> None:
    """
    Define the voltage value limit of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    limit : float
        The voltage output value.

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', and if limit if a float
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_voltage_current_limit(instrument, 'a', 'A')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if not isinstance(limit,float) :
            raise ValueError("Invalid output value. Must be a float.")

        # Construct command
        command = f"smu{channel}.source.limitv = {limit}"

        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def command_source_power_limit(instrument: pyvisa.resources.Resource, channel: str, limit: float) -> None:
    """
    Define the power value limit of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    limit : float
        The power output value.

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', and if limit if a float
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_power_current_limit(instrument, 'a', 'A')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if not isinstance(limit,float) :
            raise ValueError("Invalid output value. Must be a float.")

        # Construct command
        command = f"smu{channel}.source.limitp = {limit}"

        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def command_source_status(instrument: pyvisa.resources.Resource, channel: str, status: str) -> None:
    """
    Define the source status of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    status : str
        The status of the channel

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', and if status is not 'ON' or 'OFF'
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_source_status(instrument, 'a', 'OFF')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if status not in ('ON', 'OFF') :
            raise ValueError("Invalid status. Must be 'ON' or 'OFF'.")

        # Construct command
        command = f"smu{channel}.source.output = smu{channel}.OUTPUT_{status}"

        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def command_current_source_range(instrument: pyvisa.resources.Resource, channel: str, range_value: str) -> None:
    """
    Define the current range value of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    range_value : int
        The range value 

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', and if range value is not between 0 and 8
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_current_source_range(instrument, 'a', 'OFF')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if range_value not in range(9) :
            raise ValueError("Invalid range value. Must be between 0 and 8.")
            
        # Make equivalent between range value and current
        current_range = ['100e-9', '1e-6', '10e-6', '100e-6', '1e-3', '10e-3', '100e-3', '1', '3']
        range_value = current_range[range_value]
        
        # Construct command
        command = f"smu{channel}.source.rangei = {range_value}"
        
        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise


def command_voltage_source_range(instrument: pyvisa.resources.Resource, channel: str, range_value: str) -> None:
    """
    Define the voltage range value of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    range_value : int
        The range value 

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', and if range value is not between 0 and 3
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_voltage_source_range(instrument, 'a', 'OFF')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if range_value not in range(4) :
            raise ValueError("Invalid range value. Must be between 0 and 8.")
            
        # Make equivalent between range value and voltage
        voltage_range = ['100e-3', '1', '6', '40']
        range_value = voltage_range[range_value]
        
        # Construct command
        command = f"smu{channel}.source.rangev = {range_value}"
        
        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise



def command_sense_type(instrument: pyvisa.resources.Resource, channel: str, sensor_type: str) -> None:
    """
    Define the type of measurement (local : 2-wire or Remote: 4-wire) of a given channel on the Keithley 2602 SourceMeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : str
        The channel of the instrument ('a' or 'b').
    sensor_type : int
        The range value ('LOCAL' or 'REMOTE')

    Raises:
    -------
    ValueError
        If the channel is not 'a' or 'b', and if sensor type in not 'LOCAL' or 'REMOTE'
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::25::INSTR')
    command_sense_type(instrument, 'a', 'LOCAL')
    """

    try:
        # Validate input
        if channel not in ('a', 'b'):
            raise ValueError("Invalid channel. Must be 'a' or 'b'.")
        if sensor_type not in ('LOCAL','REMOTE') :
            raise ValueError("Invalid sensor type. Must be 'LOCAL' or 'REMOTE'.")
        
        # Construct command
        command = f"smu{channel}.sense = smu{channel}.SENSE_{sensor_type}"
        
        # Send command
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise
