#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyvisa

def query_voltage(instrument: pyvisa.resources.Resource) -> float:
    """
    Queries the measured temperature of a specific channel on the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : int
        The channel number (1 to 16) to query.

    Returns:
    --------
    float
        The measured temperature of the specified channel [Kelvin].

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")
    temperature = query_temperature(instrument, 1)
    print(f"Measured Temperature: {temperature} Ohm")
    """

    # Validate the instrument type
    if not isinstance(instrument, pyvisa.resources.Resource):
        raise ValueError(f"Invalid instrument {instrument}. Please provide a valid PyVISA resource object.")
    
    try:
        response = instrument.query('F1')
        
        # Check for empty response
        if not response.strip():
            raise ValueError("Empty response from instrument")
    
        # Convert the response to a float and return
        return float(response)
    
    except pyvisa.VisaIOError as e:
        print(f"Communication error: {e}")
        raise  # Raise the exception for the caller to handle
    except ValueError as e:
        print(f"Parsing error: {e}")
        raise  # Raise the exception for the caller to handle
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise  # Raise the exception for the caller to handle
        