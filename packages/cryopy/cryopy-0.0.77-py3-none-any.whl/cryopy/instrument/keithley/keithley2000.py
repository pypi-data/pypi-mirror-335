#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa
import logging

# Set up logging for the module
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def query_current(instrument: pyvisa.resources.Resource) -> float:
    """
    Queries the measured current of a given channel on the Keithley 2000 multimeter.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    Returns:
    --------
    float
        The measured current in amperes (A).

    Raises:
    -------
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
        # Construct query command
        command = ':CONF:CURR:DC'
        
        # Send instruction and parse response
        instrument.write(command)
        response = instrument.query(':READ?')
        
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
        