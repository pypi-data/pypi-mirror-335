import pyvisa
import logging
import re

# Set up logging for the module
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


#%% INSTRUMENT PARAMETERS
# INSTRUMENT ADDRESS
ADDRESS_LAKESHORE336 = "GPIB0::15::INSTR" 

# INSTRUMENT INITIALISATION
rm = pyvisa.ResourceManager()
LAKESHORE336 = rm.open_resource(ADDRESS_LAKESHORE336)


def command_remote_interface_mode(instrument: pyvisa.resources.Resource, mode: int) -> None:
    """
    Sets the remote interface mode for the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    mode : int
        The mode of the interface command:
        - 0 = Local
        - 1 = Remote
        - 2 = Remote with local lockout.

    Returns:
    --------
    None
        This function does not return any value.

    Raises:
    -------
    ValueError
        If the mode value is not valid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    command_remote_interface_mode(instrument, 1)
    print("Interface mode set to remote.")
    """

    try:
        # Validate mode value
        if mode not in [0, 1, 2]:
            raise ValueError("Invalid mode. Mode must be one of [0, 1, 2].")

        # Convert the mode to string for the command
        mode_str = str(mode)

        # Send the mode command to the instrument
        instrument.write(f'MODE {mode_str}')

        # Log the successful command execution
        logger.info(f"Remote interface mode set to {mode_str}.")

    except ValueError as e:
        logger.error(f"Invalid mode value: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle
        

def query_identification(instrument: pyvisa.resources.Resource) -> tuple[str, str, str, str]:
    """
    Queries the identification of the LakeShore Model 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    Returns:
    --------
    tuple
        A tuple containing the following information:
        - manufacturer (str): Should be "LSCI".
        - model (str): Should be "MODEL336".
        - instrument_serial (str): Serial number and option serial number of the instrument.
        - firmware_version (str): Firmware version of the instrument.

    Raises:
    -------
    ValueError
        If the response format is unexpected or if any required field is missing.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    manufacturer, model, instrument_serial, firmware_version = query_identification(instrument)
    print(f"Manufacturer: {manufacturer}, Model: {model}")
    """

    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Query the instrument's identification
        response = instrument.query('*IDN?')

        # Check for empty response
        if not response.strip():
            raise ValueError("Empty response from instrument")

        # Parse the response using expected format
        try:
            manufacturer, model, instrument_serial, firmware_version = response.split(',')
            manufacturer = manufacturer.strip()
            model = model.strip()
            instrument_serial = instrument_serial.strip()
            firmware_version = firmware_version.strip()

        except ValueError as e:
            logger.error(f"Error parsing response: {e}")
            raise ValueError("Failed to parse instrument identification data.")

        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)
        
        return manufacturer, model, instrument_serial, firmware_version

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Parsing error: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle


def query_temperature(instrument: pyvisa.resources.Resource) -> tuple[float, float, float, float]:
    """
    Queries the measured temperatures from the four channels on the Lakeshore 336 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    Returns:
    --------
    tuple
        A tuple containing the measured temperatures of the four channels in Kelvin (float).

    Raises:
    -------
    ValueError
        If the response format is unexpected or if the number of temperatures is incorrect.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")
    temperatures = query_temperature(instrument)
    print(f"Measured Temperature of channel A: {temperatures[0]} Kelvin")
    """

    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)

        # Query the instrument for the temperatures
        response = instrument.query('KRDG? 0')

        # Check for empty response
        if not response.strip():
            raise ValueError("Empty response from instrument")

        # Use regex to extract all the temperature values in the response
        temperatures = [float(temp) for temp in re.findall(r"([+-]?\d*\.\d+|\d+)", response)]

        # Check if we received exactly four temperatures
        if len(temperatures) != 4:
            raise ValueError(f"Unexpected number of temperatures received. Expected 4, got {len(temperatures)}.")
            
        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)
        
        return tuple(temperatures)

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Parsing error: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle


def query_resistance(instrument: pyvisa.resources.Resource) -> tuple[float,float,float,float]:
    """
    Query the measured resistance of all four channels (A, B, C, D) on the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    Returns:
    --------
    tuple : (float, float, float, float)
        The measured resistance values of channels A, B, C, and D in Ohms.

    Raises:
    -------
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    resistance_a, resistance_b, resistance_c, resistance_d = query_resistance(instrument)
    """

    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Send the query to get resistance values
        answer = instrument.query('SRDG? 0')

        # Ensure we received a valid response
        if not answer or len(answer) < 36:
            raise ValueError("Invalid response received from the instrument.")

        # Parse the received response (split into the four channels)
        resistance_a = float(answer[0:8].strip())
        resistance_b = float(answer[9:17].strip())
        resistance_c = float(answer[18:26].strip())
        resistance_d = float(answer[27:35].strip())

        # Log the successfully retrieved resistance values
        logger.info(f"Successfully retrieved resistance values: A={resistance_a}, B={resistance_b}, C={resistance_c}, D={resistance_d}")

        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)
        
        return resistance_a, resistance_b, resistance_c, resistance_d

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error with the instrument: {e}")
        raise  # Re-raise the VisaIOError to notify the caller
    except ValueError as e:
        logger.error(f"Error parsing response: {e}")
        raise  # Re-raise the ValueError to notify the caller
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise any other exception for the caller to handle


def query_input_reading_status(instrument: pyvisa.resources.Resource) -> str:
    """
    Queries the input reading status from the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    Returns:
    --------
    str
        A string indicating the input reading status:
        - 'valid reading'
        - 'invalid reading'
        - 'temp underrange'
        - 'temp overrange'
        - 'sensor unit zero'
        - 'sensor unit overrange'

    Raises:
    -------
    ValueError
        If the response format is unexpected or if an invalid status code is received.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    status = query_input_reading_status(instrument)
    print(f"Input reading status: {status}")
    """

    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Query the input reading status from the instrument
        response = instrument.query('RDGST?')

        # Check for empty response
        if not response.strip():
            raise ValueError("Empty response from instrument")

        # Parse the first three characters of the response to get the status code
        status_code = int(response[0:3])

        # Map status codes to status messages
        status_mapping = {
            0: 'valid reading',
            1: 'invalid reading',
            16: 'temp underrange',
            32: 'temp overrange',
            64: 'sensor unit zero',
            128: 'sensor unit overrange'
        }

        # Check if the status code is valid
        if status_code not in status_mapping:
            raise ValueError(f"Unexpected status code received: {status_code}")
            
        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)
        
        return status_mapping[status_code]

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Parsing error: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle


def query_pid_parameters(instrument: pyvisa.resources.Resource, output: int) -> tuple[float, float, float]:
    """
    Queries the PID parameters for a specified output channel of the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    output : int
        The channel output (1 = output 1, 2 = output 2).

    Returns:
    --------
    tuple
        A tuple containing the PID parameters:
        - P (float): The proportional parameter.
        - I (float): The integral parameter.
        - D (float): The derivative parameter.

    Raises:
    -------
    ValueError
        If the response format is unexpected or if the PID parameters cannot be parsed.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    p, i, d = query_pid_parameters(instrument, 1)
    print(f"P: {p}, I: {i}, D: {d}")
    """

    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Query the PID parameters from the instrument
        response = instrument.query(f'PID? {output}')

        # Check for empty response
        if not response.strip():
            raise ValueError("Empty response from instrument")

        # Parse the response to extract the PID parameters
        try:
            p = float(response[0:5].strip())
            i = float(response[8:13].strip())
            d = float(response[16:20].strip())
        except ValueError as e:
            logger.error(f"Error parsing PID parameters: {e}")
            raise ValueError("Failed to parse PID parameters from response.")
            
        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)
        
        return p, i, d

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Parsing error: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle


def command_pid_parameters(instrument: pyvisa.resources.Resource, p: float, i: float, d: float, output: int) -> None:
    """
    Sets the PID parameters on a specific output channel of the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    p : float
        The proportional parameter.

    i : float
        The integral parameter.

    d : float
        The derivative parameter.

    output : int
        The channel output (1 = output 1, 2 = output 2).

    Returns:
    --------
    None
        This function does not return any value.

    Raises:
    -------
    ValueError
        If the parameters are not valid or the response from the instrument is unexpected.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    command_pid_parameters(instrument, 1.2, 3.4, 5.6, 1)
    print("PID parameters set successfully.")
    """

    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Validate input parameters
        if not isinstance(p, (float, int)) or not isinstance(i, (float, int)) or not isinstance(d, (float, int)):
            raise ValueError("PID parameters must be numeric (float or int).")
        
        # Convert all parameters to strings for the command
        p_str = str(p)
        i_str = str(i)
        d_str = str(d)
        output_str = str(output)

        # Construct the PID command
        pid_command = f'PID {output_str},{p_str},{i_str},{d_str}'

        # Send the command to the instrument
        instrument.write(pid_command)
        
        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)
        
        # Check if the command is effective
        if query_pid_parameters(instrument, output) == (p,i,d):
            print('New PID parameters successfully configured')
        else:
            print('Failed to configure the new PID parameters')

        logger.info(f"PID parameters set successfully: Output {output}, P: {p}, I: {i}, D: {d}")

    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle
        

def query_heater_setup(instrument: pyvisa.resources.Resource, output: int) -> tuple[int, int, float, int]:
    """
    Queries the heater parameters of the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    output : int
        The output channel to query the heater parameters for:
        - 1 = output 1
        - 2 = output 2

    Returns:
    --------
    tuple
        A tuple containing the following heater parameters:
        - heater_resistance (int): The heater resistance selection:
            - 1 = 25 Ohms
            - 2 = 50 Ohms
        - max_current (int): The maximum current selection:
            - 0 = user-specified
            - 1 = 0.707 A
            - 2 = 1 A
            - 3 = 1.141 A
            - 4 = 2 A
        - max_user_current (float): The maximum current set by the user (in Amperes).
        - current_or_power (int): The current or power display selection:
            - 1 = current
            - 2 = power

    Raises:
    -------
    ValueError
        If the output is invalid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    heater_resistance, max_current, max_user_current, current_or_power = query_heater_setup(instrument, 1)
    print(f"Heater Resistance: {heater_resistance}, Max Current: {max_current}, Max User Current: {max_user_current}, Display Mode: {current_or_power}")
    """
    
    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Validate input parameters
        if output not in [1, 2]:
            raise ValueError("Invalid output. Output must be one of [1, 2].")

        # Query heater setup information
        response = instrument.query(f'HTRSET? {output}')

        # Parse the response to extract the parameters
        heater_resistance = int(response[0:1])
        max_current = int(response[2:3])
        max_user_current = float(response[5:10])
        current_or_power = int(response[11:12])

        # Log the response parsing
        logger.info(f"Heater parameters for output {output}: {response.strip()}")

        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)

        return heater_resistance, max_current, max_user_current, current_or_power

    except ValueError as e:
        logger.error(f"Invalid input value: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle


def command_heater_setup(instrument: pyvisa.resources.Resource, 
                          output: int, 
                          heater_resistance: int, 
                          max_current: int, 
                          max_user_current: float, 
                          current_or_power: int) -> None:
    """
    Sets the heater parameters on the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    output : int
        The output channel to configure the heater for:
        - 1 = output 1
        - 2 = output 2

    heater_resistance : int
        The heater resistance selection:
        - 1 = 25 Ohms
        - 2 = 50 Ohms

    max_current : int
        The maximum current selection:
        - 0 = user-specified
        - 1 = 0.707 A
        - 2 = 1 A
        - 3 = 1.141 A
        - 4 = 2 A

    max_user_current : float
        The maximum current as set by the user (in Amperes).

    current_or_power : int
        Specifies if the output is displayed as current or power:
        - 1 = current
        - 2 = power

    Returns:
    --------
    None
        This function does not return any value.

    Raises:
    -------
    ValueError
        If the output, heater_resistance, max_current, or current_or_power are invalid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    command_heater_setup(instrument, 1, 1, 2, 0.8, 1)
    print("Heater parameters set for output 1.")
    """
    
    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Validate input parameters
        if output not in [1, 2]:
            raise ValueError("Invalid output. Output must be one of [1, 2].")
        if heater_resistance not in [1, 2]:
            raise ValueError("Invalid heater resistance. Must be 1 (25 Ohms) or 2 (50 Ohms).")
        if max_current not in [0, 1, 2, 3, 4]:
            raise ValueError("Invalid max current. Must be one of [0, 1, 2, 3, 4].")
        if current_or_power not in [1, 2]:
            raise ValueError("Invalid current or power selection. Must be 1 (current) or 2 (power).")
        
        # Construct the heater setup command
        command = f'HTRSET {output},{heater_resistance},{max_current},{max_user_current},{current_or_power}'

        # Send the command to the instrument
        instrument.write(command)

        # Log the successful command execution
        logger.info(f"Heater setup command sent for output {output}, resistance {heater_resistance}.")

        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)
        
        # Check if the command is effective
        if query_heater_setup(instrument, output) == (heater_resistance,max_current,max_user_current,current_or_power):
            print('New heater parameters successfully configured')
        else:
            print('Failed to configure the new heater parameters')
            
    except ValueError as e:
        logger.error(f"Invalid input value: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle
        
        
def query_setpoint(instrument: pyvisa.resources.Resource, output: int) -> float:
    """
    Queries the setpoint temperature for a specific output channel on the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    output : int
        The output channel to query the temperature for:
        - 1 = output 1
        - 2 = output 2

    Returns:
    --------
    float
        The setpoint temperature for the specified output channel (in Kelvin).

    Raises:
    -------
    ValueError
        If the output is invalid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    setpoint = query_setpoint(instrument, 1)
    print(f"Setpoint for output 1: {setpoint} K")
    """
    
    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Validate the output parameter
        if output not in [1, 2]:
            raise ValueError("Invalid output. Output must be one of [1, 2].")

        # Convert output to string for the instrument query
        output_str = str(output)

        # Send the query to get the setpoint temperature
        response = instrument.query(f'SETP? {output_str}')

        # Parse the response into a float (assuming the response is a number)
        setpoint = float(response)

        # Log the successful query
        logger.info(f"Setpoint for output {output} is {setpoint} K")

        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)

        return setpoint

    except ValueError as e:
        logger.error(f"Invalid input value: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle

        
def command_setpoint(instrument: pyvisa.resources.Resource, output: int, value: float) -> None:
    """
    Sets the setpoint temperature for a specific output channel on the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    output : int
        The output channel to set the temperature for:
        - 1 = output 1
        - 2 = output 2

    value : float
        The setpoint temperature to be set (in Kelvin).

    Returns:
    --------
    None

    Raises:
    -------
    ValueError
        If the output is invalid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    command_setpoint(instrument, 1, 10.0)
    print("Setpoint for output 1 has been set to 10.0 K")
    """
    
    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Validate the output parameter
        if output not in [1, 2]:
            raise ValueError("Invalid output. Output must be one of [1, 2].")

        # Convert parameters to strings for the instrument command
        output_str = str(output)
        value_str = str(value)

        # Send the command to set the setpoint temperature
        command = f'SETP {output_str},{value_str}'
        instrument.write(command)

        # Log the successful command
        logger.info(f"Setpoint for output {output} has been set to {value} K")

        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)
        
        # Check if the command is effective
        if query_setpoint(instrument, output) == value:
            print('New setpoint value successfully configured')
        else:
            print('Failed to configure the new setpoint value')

    except ValueError as e:
        logger.error(f"Invalid input value: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle
        
    
def query_heater_range(instrument: pyvisa.resources.Resource, output: int) -> int:
    """
    Queries the heater range for a specific output channel on the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    output : int
        The output channel to query the heater range for:
        - 1 = output 1
        - 2 = output 2

    Returns:
    --------
    int
        The heater range value:
        - 0 = Off
        - 1 = Low
        - 2 = Medium
        - 3 = High

    Raises:
    -------
    ValueError
        If the output is invalid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    range_value = query_heater_range(instrument, 1)
    print(f"Heater range for output 1: {range_value}")
    """

    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Validate the output parameter
        if output not in [1, 2]:
            raise ValueError("Invalid output. Output must be one of [1, 2].")

        # Convert output to string for the instrument command
        output_str = str(output)

        # Query the heater range from the instrument
        answer = instrument.query(f'RANGE? {output_str}')

        # Log the successful query execution
        logger.info(f"Heater range for output {output}: {answer}")

        # Convert answer to integer (range value)
        value = int(answer)
        
        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)

        return value

    except ValueError as e:
        logger.error(f"Invalid input value: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle
        
            
def command_heater_range(instrument: pyvisa.resources.Resource, output: int, value: int):
    """
    Sets the heater range for a specific output channel on the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    output : int
        The output channel to configure the heater range for:
        - 1 = output 1
        - 2 = output 2

    value : int
        The desired heater range:
        - 0 = Off
        - 1 = Low
        - 2 = Medium
        - 3 = High

    Returns:
    --------
    None

    Raises:
    -------
    ValueError
        If the output or value is invalid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    command_heater_range(instrument, 1, 2)
    print("Heater range for output 1 set to Medium.")
    """
    
    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Validate the output and value parameters
        if output not in [1, 2]:
            raise ValueError("Invalid output. Output must be one of [1, 2].")
        if value not in [0, 1, 2, 3]:
            raise ValueError("Invalid value. Range must be one of [0, 1, 2, 3].")

        # Convert output and value to strings for the instrument command
        output_str = str(output)
        value_str = str(value)

        # Send the command to set the heater range
        command = f'RANGE {output_str},{value_str}'
        instrument.write(command)

        # Log the successful command execution
        logger.info(f"Heater range for output {output} set to {value_str}.")

        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)

        # Check if the command is effective
        if query_heater_range(instrument, output) == value:
            print('New heater range value successfully configured')
        else:
            print('Failed to configure the new heater range value')

    except ValueError as e:
        logger.error(f"Invalid input value: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle
        
        
def command_autotune(instrument: pyvisa.resources.Resource, output: int, mode: int) -> None:
    """
    Sets the autotune parameters for a specified output channel on the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    output : int
        The output channel for the autotune command:
        - 1 = output 1
        - 2 = output 2
        - 3 = output 3
        - 4 = output 4

    mode : int
        The autotune mode:
        - 0 = P only
        - 1 = P and I
        - 2 = P, I, and D

    Returns:
    --------
    None
        This function does not return any value.

    Raises:
    -------
    ValueError
        If the output or mode values are invalid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    command_autotune(instrument, 2, 1)
    print("Autotune set for output 2 with P and I parameters.")
    """

    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Validate output and mode values
        if output not in [1, 2, 3, 4]:
            raise ValueError("Invalid output. Output must be one of [1, 2, 3, 4].")
        if mode not in [0, 1, 2]:
            raise ValueError("Invalid mode. Mode must be one of [0, 1, 2].")

        # Convert output and mode to strings for the command
        output_str = str(output)
        mode_str = str(mode)

        # Construct the autotune command
        command = f'ATUNE {output_str},{mode_str}'

        # Send the command to the instrument
        instrument.write(command)

        # Log the successful command execution
        logger.info(f"Autotune command set for output {output_str} with mode {mode_str}.")

        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)

    except ValueError as e:
        logger.error(f"Invalid input value: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle


def command_outmode(instrument: pyvisa.resources.Resource, output: int, mode: int, channel: int, powerup: int):
    """
    Setup the output mode for a specific output channel on the LakeShore 336 Cryogenic Temperature Controller.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.

    output : int
        The output channel to configure (1-4):
        - 1 = output 1
        - 2 = output 2
        - 3 = output 3
        - 4 = output 4

    mode : int
        The output mode to configure (0-5):
        - 0 = Off
        - 1 = Closed-loop
        - 2 = Zone
        - 3 = Open loop
        - 4 = Monitor out
        - 5 = Warmup supply

    channel : int
        The channel (0-4):
        - 0 = None
        - 1 = Channel A
        - 2 = Channel B
        - 3 = Channel C
        - 4 = Channel D

    powerup : int
        The powerup status (0-1):
        - 0 = Powerup enable off
        - 1 = Powerup enable on

    Returns:
    --------
    None

    Raises:
    -------
    ValueError
        If any of the input parameters are invalid.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors.

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource('GPIB0::15::INSTR')
    command_outmode(instrument, 1, 1, 1, 0)
    """
    try:
        # Activation of the remote mode 
        command_remote_interface_mode(instrument, 1)
        
        # Validate inputs
        if output not in [1, 2, 3, 4]:
            raise ValueError("Invalid output. Output must be one of [1, 2, 3, 4].")
        if mode not in [0, 1, 2, 3, 4, 5]:
            raise ValueError("Invalid mode. Mode must be one of [0, 1, 2, 3, 4, 5].")
        if channel not in [0, 1, 2, 3, 4]:
            raise ValueError("Invalid channel. Channel must be one of [0, 1, 2, 3, 4].")
        if powerup not in [0, 1]:
            raise ValueError("Invalid powerup. Powerup must be either 0 or 1.")
        
        # Convert inputs to strings
        output_str = str(output)
        mode_str = str(mode)
        channel_str = str(channel)
        powerup_str = str(powerup)

        # Form the OUTMODE command string
        request = f'OUTMODE {output_str},{mode_str},{channel_str},{powerup_str}'

        # Send the command to the instrument
        instrument.write(request)

        # Log the successful execution
        logger.info(f"Successfully set OUTMODE for output {output}: {request}")

        # Desactivation of the remote mode 
        command_remote_interface_mode(instrument, 0)

    except ValueError as e:
        logger.error(f"Invalid input value: {e}")
        raise  # Re-raise the ValueError for the caller to handle
    except pyvisa.VisaIOError as e:
        logger.error(f"Communication error: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the generic exception for the caller to handle
