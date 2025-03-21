# -*- coding: utf-8 -*-

import pyvisa


def command_cls(instrument: pyvisa.resources.Resource) -> str:
    """
    ========== DESCRIPTION ==========

    This function clears the status register and resets all errors on the Lakeshore 370.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- str --
        A confirmation message

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Clear the status register
    success = command_cls(instrument)
    if success:
        print("Status cleared successfully.")
    else:
        print("Failed to clear status.")
    """

    try:
        # Send the CLS command to clear the status
        instrument.write("CLS")
    except pyvisa.VisaIOError as e:
        # Handle any errors that occur during communication
        print(f"Error executing CLS command: {e}")
        return False  # Return False if an error occurred
    print("Interface successfully cleaned")
    
    

def query_ese(instrument: pyvisa.resources.Resource) -> int:
    """
    ========== DESCRIPTION ==========

    This function queries the current status of the event status register (ESE) on the Lakeshore 370.
    
    The ESE register provides information about specific conditions in the instrument, such as 
    whether an error has occurred or whether a measurement is complete.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- int --
        The current value of the event status register (ESE). The value is typically a bitfield 
        representing various instrument states (refer to the instrument manual for specific details).

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the event status register
    ese_value = query_ese(instrument)
    print(f"ESE value: {ese_value}")
    """

    try:
        # Send the ESE? query to get the current event status register value
        response = instrument.query("*ESE?")
        ese_value = int(response)  # Convert the response to an integer
        return ese_value
    except pyvisa.VisaIOError as e:
        # Handle any errors that occur during communication
        print(f"Error querying ESE register: {e}")
        return -1  # Return -1 to indicate an error occurred
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred while querying ESE: {e}")
        return -1  # Return -1 to indicate an error occurred


def command_ese(instrument: pyvisa.resources.Resource, ese_value: int) -> bool:
    """
    ========== DESCRIPTION ==========

    This function sets the event status enable register (ESE) on the Lakeshore 370. 
    The ESE register is used to specify which events will cause an interrupt when they occur.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    <ese_value>
        -- int --
        The value to set for the event status enable register. This value determines which events 
        will be enabled for the interrupt mechanism. The value should typically be an integer value 
        representing a bitfield.

    ========== OUTPUT ==========

    Returns:
        -- bool --
        True if the command was successfully sent, False if an error occurred.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Set the ESE register value
    success = command_ese(instrument, 15)  # Example value to enable specific events
    if success:
        print("ESE register set successfully.")
    else:
        print("Failed to set the ESE register.")
    """

    try:
        # Send the *ESE command to set the event status enable register
        instrument.write(f"*ESE {ese_value}")
        return True  # Return True to indicate successful command execution
    except pyvisa.VisaIOError as e:
        # Handle any errors that occur during communication
        print(f"Error executing *ESE command: {e}")
        return False  # Return False if an error occurred
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred while executing *ESE: {e}")
        return False  # Return False if an error occurred


def query_esr(instrument: pyvisa.resources.Resource) -> int:
    """
    ========== DESCRIPTION ==========

    This function queries the Event Status Register (ESR) of the Lakeshore 370.
    The ESR indicates which events have occurred and are stored in the register.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- int --
        The value of the Event Status Register, representing the events that have occurred.
        The value will be a bitfield that indicates the specific events.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the ESR register
    esr_value = query_esr(instrument)
    print(f"Event Status Register: {esr_value}")
    """

    try:
        # Send the ESR? command to query the event status register
        response = instrument.query("ESR?")
        esr_value = int(response)  # Convert the response to an integer
        return esr_value  # Return the value of the ESR
    except pyvisa.VisaIOError as e:
        # Handle any errors that occur during communication
        print(f"Error querying ESR: {e}")
        return -1  # Return -1 to indicate an error in querying the ESR
    except ValueError as e:
        # Handle errors related to parsing the response
        print(f"Error parsing ESR response: {e}")
        return -1  # Return -1 to indicate a parsing error
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred while querying ESR: {e}")
        return -1  # Return -1 to indicate an unexpected error

def query_idn(instrument: pyvisa.resources.Resource) -> str:
    """
    ========== DESCRIPTION ==========

    This function queries the instrument's identification string using the IDN? command.
    The IDN? command returns the manufacturer, model number, and serial number of the instrument.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- str --
        The identification string of the instrument, which typically includes:
        Manufacturer, Model, Serial Number, and Firmware version.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the instrument ID
    idn_string = query_idn(instrument)
    print(f"Instrument ID: {idn_string}")
    """

    try:
        # Send the IDN? command to query the instrument identification
        response = instrument.query("IDN?")
        return response  # Return the IDN string received from the instrument
    except pyvisa.VisaIOError as e:
        # Handle any errors that occur during communication
        print(f"Error querying IDN: {e}")
        return "Error: Communication Failure"  # Return a default error message
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred while querying IDN: {e}")
        return "Error: Unexpected Failure"  # Return a default error message


def command_opc(instrument: pyvisa.resources.Resource) -> bool:
    """
    ========== DESCRIPTION ==========

    This function sends the OPC (Operation Complete) command to the instrument, 
    which tells the instrument to complete its current operation.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- bool --
        True if the OPC command was sent successfully, False if an error occurred.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Send the OPC command
    success = command_opc(instrument)
    if success:
        print("Operation complete command sent successfully.")
    else:
        print("Failed to send operation complete command.")
    """
    
    try:
        # Send the OPC command to indicate that the operation is complete
        instrument.write("OPC")
        return True  # Return True if the command is successfully sent
    except pyvisa.VisaIOError as e:
        # Handle any errors that occur during communication
        print(f"Error sending OPC command: {e}")
        return False  # Return False if an error occurred
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred while sending OPC: {e}")
        return False  # Return False in case of an unexpected error

def query_opc(instrument: pyvisa.resources.Resource) -> bool:
    """
    ========== DESCRIPTION ==========

    This function queries the status of the Operation Complete (OPC) on the Lakeshore 370.
    It returns True if the operation is complete (OPC = 1) and False if not (OPC = 0).

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- bool --
        True if the operation is complete (OPC = 1), False if not (OPC = 0).

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the OPC status
    is_complete = query_opc(instrument)
    if is_complete:
        print("Operation is complete.")
    else:
        print("Operation is not complete.")
    """
    
    try:
        # Query the OPC status
        response = instrument.query("OPC?")
        
        # Convert the response to a boolean
        return bool(int(response))
    except pyvisa.VisaIOError as e:
        # Handle any errors that occur during communication
        print(f"Error querying OPC status: {e}")
        return False  # Return False if an error occurred
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred while querying OPC: {e}")
        return False  # Return False in case of an unexpected error


def query_sre(instrument: pyvisa.resources.Resource) -> int:
    """
    ========== DESCRIPTION ==========

    This function queries the status of the Service Request Enable (SRE) on the Lakeshore 370.
    It returns the current status of the SRE register.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- int --
        The current status of the SRE register.
        (0 = Disable, 1 = Enable)

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the SRE status
    sre_status = query_sre(instrument)
    if sre_status == 0:
        print("Service Request Enable is disabled.")
    elif sre_status == 1:
        print("Service Request Enable is enabled.")
    """
    
    try:
        # Query the SRE status
        response = instrument.query("SRE?")
        
        # Return the response as an integer (0 or 1)
        return int(response)
    except pyvisa.VisaIOError as e:
        # Handle any errors that occur during communication
        print(f"Error querying SRE status: {e}")
        return -1  # Return -1 if an error occurred
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred while querying SRE: {e}")
        return -1  # Return -1 in case of an unexpected error




def command_sre(instrument: pyvisa.resources.Resource, sre_value: int) -> bool:
    """
    ========== DESCRIPTION ==========

    This function enables or disables the Service Request Enable (SRE) on the Lakeshore 370 by setting
    the SRE register. The SRE register controls whether the instrument can generate service requests.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    <sre_value>
        -- int --
        The value to set the SRE register:
        (0 = Disable, 1 = Enable)

    ========== OUTPUT ==========

    Returns:
        -- bool --
        `True` if the command was successfully executed, `False` if there was an error.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Command to enable the SRE
    success = command_sre(instrument, 1)
    if success:
        print("Service Request Enable is now enabled.")
    else:
        print("Failed to enable Service Request.")
    """
    
    try:
        # Send the command to set the SRE register
        instrument.write(f"SRE {sre_value}")
        
        # Return True if the command is successful
        return True
    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error sending SRE command: {e}")
        return False  # Return False if there was an error
    except Exception as e:
        # Handle other unexpected errors
        print(f"An unexpected error occurred while setting SRE: {e}")
        return False  # Return False if an unexpected error occurred


def command_rst(instrument: pyvisa.resources.Resource) -> bool:
    """
    ========== DESCRIPTION ==========

    This function sends the RST (Reset) command to the Lakeshore 370, which resets the instrument to its
    default settings. The reset command clears all settings, including the error register and status registers.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- bool --
        `True` if the command was successfully executed, `False` if there was an error.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Command to reset the instrument
    success = command_rst(instrument)
    if success:
        print("Instrument reset successfully.")
    else:
        print("Failed to reset the instrument.")
    """
    
    try:
        # Send the RST command to reset the instrument
        instrument.write("RST")
        
        # Return True if the command was successful
        return True
    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error sending RST command: {e}")
        return False  # Return False if there was a communication error
    except Exception as e:
        # Handle other unexpected errors
        print(f"An unexpected error occurred while resetting the instrument: {e}")
        return False  # Return False if there was an unexpected error


def query_stb(instrument: pyvisa.resources.Resource) -> int:
    """
    ========== DESCRIPTION ==========

    This function queries the status byte (STB) from the Lakeshore 370. The status byte contains 
    information about the current state of the instrument and any errors that may have occurred.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- int --
        The status byte returned by the instrument.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the status byte
    status_byte = query_stb(instrument)
    print(f"Status Byte: {status_byte}")
    """
    
    try:
        # Send the query for the status byte
        answer = instrument.query("STB?")
        
        # Convert the response to an integer (status byte)
        status_byte = int(answer)
        
        # Return the status byte
        return status_byte
    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error querying STB: {e}")
        return -1  # Return -1 if there was a communication error
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while querying STB: {e}")
        return -1  # Return -1 if there was an unexpected error


def query_tst(instrument: pyvisa.resources.Resource) -> int:
    """
    ========== DESCRIPTION ==========

    This function queries the test status (TST?) from the Lakeshore 370. The TST? command returns
    the test status, indicating if a test has completed or if there is an ongoing test.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- int --
        The test status (0 = No test in progress, 1 = Test in progress).

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the test status
    test_status = query_tst(instrument)
    if test_status == 0:
        print("No test in progress.")
    elif test_status == 1:
        print("Test in progress.")
    else:
        print("Failed to query test status.")
    """
    
    try:
        # Send the query for the test status
        answer = instrument.query("TST?")
        
        # Convert the response to an integer (test status)
        test_status = int(answer)
        
        # Return the test status
        return test_status
    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error querying TST: {e}")
        return -1  # Return -1 if there was a communication error
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while querying TST: {e}")
        return -1  # Return -1 if there was an unexpected error


def query_wai(instrument: pyvisa.resources.Resource) -> int:
    """
    ========== DESCRIPTION ==========

    This function queries the WAI (Wait to continue) status from the Lakeshore 370. The WAI? command
    returns whether the instrument is still processing or has finished its operation. The function
    waits for the instrument to be ready before proceeding.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- int --
        The status of the operation (1 = Ready, 0 = Busy).

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the WAI status
    wai_status = query_wai(instrument)
    if wai_status == 1:
        print("Instrument is ready.")
    elif wai_status == 0:
        print("Instrument is still busy.")
    else:
        print("Failed to query WAI status.")
    """
    
    try:
        # Send the query for WAI status
        answer = instrument.query("WAI?")
        
        # Convert the response to an integer (ready or busy)
        wai_status = int(answer)
        
        # Return the WAI status
        return wai_status
    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error querying WAI: {e}")
        return -1  # Return -1 if there was a communication error
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while querying WAI: {e}")
        return -1  # Return -1 if there was an unexpected error

        

def query_alarm(instrument: pyvisa.resources.Resource) -> int:
    """
    ========== DESCRIPTION ==========

    This function queries the ALARM status of the Lakeshore 370. The ALARM? command returns the current
    alarm status of the instrument, indicating if any alarms are triggered.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- int --
        The alarm status (1 = Alarm triggered, 0 = No alarm).

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the ALARM status
    alarm_status = query_alarm(instrument)
    if alarm_status == 1:
        print("Alarm triggered.")
    elif alarm_status == 0:
        print("No alarm.")
    else:
        print("Failed to query ALARM status.")
    """
    
    try:
        # Send the query for ALARM status
        answer = instrument.query("ALARM?")
        
        # Convert the response to an integer (1 for alarm, 0 for no alarm)
        alarm_status = int(answer)
        
        # Return the alarm status
        return alarm_status
    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error querying ALARM: {e}")
        return -1  # Return -1 if there was a communication error
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while querying ALARM: {e}")
        return -1  # Return -1 if there was an unexpected error

def command_alarm(instrument: pyvisa.resources.Resource, enable: bool) -> None:
    """
    ========== DESCRIPTION ==========

    This function controls the ALARM setting of the Lakeshore 370. It can enable or disable the alarm
    based on the input parameter.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    <enable>
        -- bool --
        If True, the alarm is enabled (set to 1).
        If False, the alarm is disabled (set to 0).

    ========== OUTPUT ==========

    Returns:
        -- None --
        None

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Enable the alarm
    command_alarm(instrument, True)
    print("Alarm enabled.")
    
    # Disable the alarm
    command_alarm(instrument, False)
    print("Alarm disabled.")
    """
    
    try:
        # Send the command to control the alarm (set to 1 for enable, 0 for disable)
        alarm_status = 1 if enable else 0
        instrument.write(f"ALARM {alarm_status}")
        print("ALARM status successfully updated.")
    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error controlling ALARM: {e}")
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while controlling ALARM: {e}")


def query_alarm_status(instrument: pyvisa.resources.Resource) -> int:
    """
    ========== DESCRIPTION ==========

    This function queries the current ALARMST status of the Lakeshore 370. The ALARMST command returns 
    the alarm status, indicating whether any alarms are active.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- int --
        The alarm status:
        - 0 = No alarm active
        - 1 = Alarm active

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the alarm status
    alarm_status = query_alarm_status(instrument)
    if alarm_status == 0:
        print("No alarm is active.")
    else:
        print("An alarm is active.")
    """
    
    try:
        # Query the ALARMST status
        answer = instrument.query("ALARMST?")
        
        # Convert the answer to an integer (0 or 1)
        alarm_status = int(answer)
        
        print(f"Current alarm status: {'Active' if alarm_status == 1 else 'Inactive'}")
        return alarm_status
    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error querying ALARMST: {e}")
        return -1  # Return -1 to indicate failure
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while querying ALARMST: {e}")
        return -1  # Return -1 to indicate failure




def command_alarm_reset(instrument: pyvisa.resources.Resource) -> bool:
    """
    ========== DESCRIPTION ==========

    This function sends the ALARMST command to reset or clear the active alarms on the Lakeshore 370.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- bool --
        True if the command was successful, False otherwise.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Send the ALARMST command to reset alarms
    success = command_alarm_reset(instrument)
    if success:
        print("Alarms reset successfully.")
    else:
        print("Failed to reset alarms.")
    """
    
    try:
        # Send the ALARMST command to reset the alarms
        instrument.write("ALARMST")
        
        print("Alarms reset successfully.")
        return True
    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error executing ALARMST command: {e}")
        return False  # Return False if an error occurred
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while sending ALARMST command: {e}")
        return False  # Return False if an error occurred


def command_analog(
    instrument: pyvisa.resources.Resource, 
    analog_channel: int, 
    polarity: int, 
    mode: int, 
    channel: int, 
    source: int, 
    high_value: float, 
    low_value: float, 
    manual_value: float
) -> bool:
    """
    ========== DESCRIPTION ==========

    This function sends the ANALOG command to configure the analog output on the Lakeshore 370
    with the provided parameters, such as polarity, mode, source, and values for the analog output.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.
    
    <analog_channel>
        -- int --
        The analog channel to configure (1-16).

    <polarity>
        -- int --
        The polarity of the analog output. (0 = Negative, 1 = Positive)

    <mode>
        -- int --
        The mode of operation for the analog output. (Example: 0 = Off, 1 = On, other modes)

    <channel>
        -- int --
        The channel number for the analog output (1-16).

    <source>
        -- int --
        The source used for the analog output (0 = Internal, 1 = External).

    <high_value>
        -- float --
        The high range value for the analog output.

    <low_value>
        -- float --
        The low range value for the analog output.

    <manual_value>
        -- float --
        The manual output value to set.

    ========== OUTPUT ==========

    Returns:
        -- bool --
        True if the command was successful, False otherwise.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Send the ANALOG command with all parameters
    success = command_analog(instrument, 1, 1, 1, 1, 0, 10.0, 1.0, 5.0)
    if success:
        print("Analog output configured successfully.")
    else:
        print("Failed to configure analog output.")
    """

    try:
        # Format the ANALOG command with the required parameters
        command = f"ANALOG {analog_channel},{polarity},{mode},{channel},{source},{high_value:.2f},{low_value:.2f},{manual_value:.2f}"
        
        # Send the command to the instrument
        instrument.write(command)

        # Confirmation message
        print(f"Analog output on channel {analog_channel} configured with polarity {polarity}, mode {mode}, source {source}, "
              f"high value {high_value}, low value {low_value}, manual value {manual_value}.")
        
        return True
    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error executing ANALOG command: {e}")
        return False  # Return False if an error occurred
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while sending ANALOG command: {e}")
        return False  # Return False if an error occurred


def query_analog(
    instrument: pyvisa.resources.Resource, 
    analog_channel: int
) -> tuple:
    """
    ========== DESCRIPTION ==========

    This function queries the current configuration of an analog channel on the Lakeshore 370.
    It retrieves the bipolar enable, mode, channel, source, high value, low value, and manual value for the given analog channel.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    <analog_channel>
        -- int --
        The analog channel to query (1-16).

    ========== OUTPUT ==========

    Returns:
        -- tuple --
        A tuple containing the current settings for the analog channel in the following order:
        (bipolar_enable, mode, channel, source, high_value, low_value, manual_value)

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the analog configuration for channel 1
    analog_settings = query_analog(instrument, 1)
    if analog_settings:
        print("Analog channel 1 settings:", analog_settings)
    else:
        print("Failed to query analog settings.")
    """

    try:
        # Send the ANALOG? command to the instrument to query the configuration for the specified channel
        response = instrument.query(f"ANALOG? {analog_channel}")
        
        # Parse the response (assuming the format: bipolar_enable, mode, channel, source, high_value, low_value, manual_value)
        response_data = response.split(',')

        # Extract individual values from the response
        bipolar_enable = int(response_data[0])  # 0 or 1 for bipolar enable
        mode = int(response_data[1])            # Mode (e.g., 0 = voltage, 1 = current)
        channel = int(response_data[2])         # Channel number (1-16)
        source = int(response_data[3])          # Source (0 = internal, 1 = external)
        high_value = float(response_data[4])    # High value for the analog output
        low_value = float(response_data[5])     # Low value for the analog output
        manual_value = float(response_data[6])  # Manual value for the analog output

        # Return the individual values as a tuple
        return bipolar_enable, mode, channel, source, high_value, low_value, manual_value

    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error querying ANALOG? command: {e}")
        return None  # Return None if an error occurred
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while querying ANALOG? command: {e}")
        return None  # Return None if an error occurred



def query_aout(
    instrument: pyvisa.resources.Resource, 
    aout_channel: int
) -> float:
    """
    ========== DESCRIPTION ==========

    This function queries the current percentage output of a specified analog output channel on the Lakeshore 370.
    The output value is provided as a percentage (0 to 100%).

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    <aout_channel>
        -- int --
        The analog output channel to query (1-16).

    ========== OUTPUT ==========

    Returns:
        -- float --
        The current percentage output of the specified analog output channel.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the analog output percentage for channel 1
    aout_percentage = query_aout(instrument, 1)
    if aout_percentage is not None:
        print(f"Analog output channel 1 percentage: {aout_percentage}%")
    else:
        print("Failed to query analog output percentage.")
    """

    try:
        # Send the AOUT? query command to get the percentage output of the specified channel
        response = instrument.query(f"AOUT? {aout_channel}")

        # Convert the response to a float representing the output percentage (0-100)
        output_percentage = float(response)

        # Return the output percentage
        return output_percentage

    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error querying AOUT? command: {e}")
        return None  # Return None if an error occurred
    except ValueError as e:
        # Handle invalid response parsing
        print(f"Invalid response received while querying AOUT? command: {e}")
        return None  # Return None if an error occurred
    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while querying AOUT? command: {e}")
        return None  # Return None if an error occurred


def command_baud_rate(
    instrument: pyvisa.resources.Resource, 
    baud_rate: int
) -> bool:
    """
    ========== DESCRIPTION ==========

    This function sets the baud rate for serial communication with the Lakeshore 370.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    <baud_rate>
        -- int --
        The baud rate to set for the instrument (e.g., 9600, 19200, 38400, etc.).

    ========== OUTPUT ==========

    Returns:
        -- bool --
        True if the baud rate was successfully set, False otherwise.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Set the baud rate to 19200
    success = command_baud_rate(instrument, 19200)
    if success:
        print("Baud rate set successfully.")
    else:
        print("Failed to set baud rate.")
    """

    try:
        # Send the BAUD command with the desired baud rate
        instrument.write(f"BAUD {baud_rate}")
        return True

    except pyvisa.VisaIOError as e:
        # Handle any errors during communication
        print(f"Error executing BAUD command: {e}")
        return False

    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while executing BAUD command: {e}")
        return False


def query_baud_rate(
    instrument: pyvisa.resources.Resource
) -> int:
    """
    ========== DESCRIPTION ==========

    This function queries the current baud rate for serial communication with the Lakeshore 370.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- int --
        The current baud rate of the instrument.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the current baud rate
    current_baud_rate = query_baud_rate(instrument)
    if current_baud_rate:
        print(f"Current baud rate: {current_baud_rate}")
    else:
        print("Failed to query baud rate.")
    """

    try:
        # Send the BAUD? query command to get the current baud rate
        response = instrument.query("BAUD?")
        
        # Convert the response to an integer and return it
        baud_rate = int(response)
        return baud_rate

    except pyvisa.VisaIOError as e:
        # Handle communication errors
        print(f"Error querying BAUD? command: {e}")
        return None  # Return None if there is a communication error

    except ValueError as e:
        # Handle invalid response parsing
        print(f"Invalid response received while querying BAUD? command: {e}")
        return None  # Return None if there is a response parsing error

    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while querying BAUD? command: {e}")
        return None  # Return None if there is an unexpected error


def command_beep(instrument: pyvisa.resources.Resource) -> bool:
    """
    ========== DESCRIPTION ==========

    This function commands the Lakeshore 370 to beep.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- bool --
        True if the command was successfully sent, False otherwise.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Command the beep
    if command_beep(instrument):
        print("Beep command sent successfully.")
    else:
        print("Failed to send beep command.")
    """

    try:
        # Send the BEEP command to the instrument
        instrument.write("BEEP")
        return True  # Return True if the beep command was sent successfully

    except pyvisa.VisaIOError as e:
        # Handle any communication errors
        print(f"Error sending BEEP command: {e}")
        return False  # Return False if there is a communication error

    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while sending BEEP command: {e}")
        return False  # Return False if there is an unexpected error


def query_beep(instrument: pyvisa.resources.Resource) -> bool:
    """
    ========== DESCRIPTION ==========

    This function queries the beep status of the Lakeshore 370.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- bool --
        True if the beep is enabled, False if it is disabled.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the beep status
    if query_beep(instrument):
        print("Beep is enabled.")
    else:
        print("Beep is disabled.")
    """

    try:
        # Query the BEEP status from the instrument
        answer = instrument.query("BEEP?")
        
        # The answer will typically be '1' for enabled and '0' for disabled
        if answer.strip() == '1':
            return True  # Beep is enabled
        else:
            return False  # Beep is disabled

    except pyvisa.VisaIOError as e:
        # Handle any communication errors
        print(f"Error querying BEEP status: {e}")
        return False  # Return False if there is a communication error

    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred while querying BEEP status: {e}")
        return False  # Return False if there is an unexpected error



def command_brightness(instrument: pyvisa.resources.Resource, brightness: int) -> str:
    """
    ========== DESCRIPTION ==========

    This function sets the brightness level of the display on the Lakeshore 370.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    <brightness>
        -- int --
        The brightness level to set (0 to 100).

    ========== OUTPUT ==========

    Returns:
        -- str --
        A confirmation message indicating whether the brightness was set successfully.

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Set the brightness to 50
    command_brightness(instrument, 50)
    print("Brightness set to 50.")
    """

    try:
        # Ensure the brightness value is within the valid range (0 to 100)
        if not (0 <= brightness <= 100):
            raise ValueError("Brightness must be between 0 and 100.")

        # Send the BRIGT command with the desired brightness level
        instrument.write(f"BRIGT {brightness}")
        return f"Brightness successfully set to {brightness}."

    except pyvisa.VisaIOError as e:
        # Handle any errors that occur during communication
        print(f"Error executing BRIGT command: {e}")
        return "Failed to set brightness due to communication error."
    
    except ValueError as e:
        # Handle invalid brightness values
        print(f"Invalid brightness value: {e}")
        return "Failed to set brightness. Please provide a value between 0 and 100."
    
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return "Failed to set brightness due to an unexpected error."


def query_brightness(instrument: pyvisa.resources.Resource) -> int:
    """
    ========== DESCRIPTION ==========

    This function queries the current brightness level of the display on the Lakeshore 370.

    ========== INPUT ==========

    <instrument>
        -- pyvisa.resources.Resource --
        The instrument resource object representing the connection to the Lakeshore 370.

    ========== OUTPUT ==========

    Returns:
        -- int --
        The current brightness level (0 to 100).

    ========== EXAMPLE ==========

    # Create a resource manager and open the connection to the instrument
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    # Query the current brightness
    brightness = query_brightness(instrument)
    print(f"Current brightness is: {brightness}")
    """

    try:
        # Send the BRIGT? command to query the current brightness
        answer = instrument.query("BRIGT?")
        brightness = int(answer)  # Convert the response to an integer
        return brightness

    except pyvisa.VisaIOError as e:
        # Handle any errors that occur during communication
        print(f"Error executing BRIGT? command: {e}")
        return -1  # Return -1 in case of an error

    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return -1  # Return -1 in case of an unexpected error




def query_resistance(instrument: pyvisa.resources.Resource, channel: int) -> float:
    """
    Queries the measured resistance of a specific channel on the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : int
        The channel number (1 to 16) to query.

    Returns:
    --------
    float
        The measured resistance of the specified channel [Ohm].

    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")
    resistance = query_resistance(instrument, 1)
    print(f"Measured Resistance: {resistance} Ohm")
    """
    
    # Validate the channel number
    if channel < 1 or channel > 16:
        raise ValueError(f"Invalid channel number {channel}. Please use a channel between 1 and 16.")
    
    # Validate the instrument type
    if not isinstance(instrument, pyvisa.resources.Resource):
        raise ValueError(f"Invalid instrument {instrument}. Please provide a valid PyVISA resource object.")
    
    try:
        response = instrument.query(f"RDGR? {channel}")
        
        # Check for empty response
        if not response.strip():
            raise ValueError(f"Empty response from instrument for channel {channel}")

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


def query_temperature(instrument: pyvisa.resources.Resource, channel: int) -> float:
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
    
    # Validate the channel number
    if channel < 1 or channel > 16:
        raise ValueError(f"Invalid channel number {channel}. Please use a channel between 1 and 16.")
        
    # Validate the instrument type
    if not isinstance(instrument, pyvisa.resources.Resource):
        raise ValueError(f"Invalid instrument {instrument}. Please provide a valid PyVISA resource object.")
    
    try:
        response = instrument.query(f"RDGK? {channel}")
        
        # Check for empty response
        if not response.strip():
            raise ValueError(f"Empty response from instrument for channel {channel}")
    
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
        

def create_instrument(address: str) -> pyvisa.resources.Resource:
    """
    Creates and returns a Pyvisa instrument instance using the provided address.

    Parameters:
    -----------
    address : str
        The address of the instrument (e.g., "GPIB0::12::INSTR").

    Returns:
    --------
    pyvisa.resources.Resource
        The Pyvisa instrument resource instance.

    Raises:
    -------
    pyvisa.VisaIOError
        If there is a communication issue with the Pyvisa ResourceManager or instrument.
    Exception
        For any unexpected errors during instrument creation.

    Example:
    --------
    try:
        instrument = create_instrument("GPIB0::12::INSTR")
        print(f"Successfully connected to instrument: {instrument}")
    except Exception as e:
        print(f"Failed to create instrument: {e}")
    """
    try:
        # Initialize the resource manager
        rm = pyvisa.ResourceManager()
        
        # Open the instrument resource
        instrument = rm.open_resource(address)
        print(f"Instrument at {address} created successfully.")
        return instrument
    
    except pyvisa.VisaIOError as e:
        print(f"Failed to create the instrument at {address}: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        print(f"An unexpected error occurred while creating the instrument at {address}: {e}")
        raise  # Re-raise any other exceptions for the caller to handle




def write(instrument: pyvisa.resources.Resource, instruction: str) -> None:
    """
    Sends a command (instruction) to a PyVISA instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A PyVISA instrument connection instance.
    instruction : str
        The command or instruction to send to the instrument.

    Raises:
    -------
    ValueError
        If the provided `instrument` is not a valid PyVISA resource.
    pyvisa.VisaIOError
        If there is a communication issue when sending the command.
    Exception
        For any unexpected errors during the operation.

    Example:
    --------
    import pyvisa
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    try:
        write(instrument, "*IDN?")
        print("Instruction sent successfully.")
    except Exception as e:
        print(f"Failed to send instruction: {e}")
    """
    
    # Validate the instrument type
    if not isinstance(instrument, pyvisa.resources.Resource):
        raise ValueError(f"Invalid instrument {instrument}. Please provide a valid PyVISA resource object.")

    try:
        # Send the instruction to the instrument
        instrument.write(instruction)
        print(f"Instruction '{instruction}' sent successfully.")
    
    except pyvisa.VisaIOError as e:
        print(f"Communication error while sending instruction '{instruction}': {e}")
        raise  # Re-raise for the caller to handle
    except Exception as e:
        print(f"An unexpected error occurred while sending instruction '{instruction}': {e}")
        raise  # Re-raise for the caller to handle



def read(instrument: pyvisa.resources.Resource) -> str:
    """
    Reads the response from a PyVISA instrument after a query.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A PyVISA instrument connection instance.

    Returns:
    --------
    str
        The response from the instrument as a string.

    Raises:
    -------
    ValueError
        If the provided `instrument` is not a valid PyVISA resource.
    pyvisa.VisaIOError
        If there is a communication issue when reading the response.
    Exception
        For any unexpected errors during the operation.

    Example:
    --------
    import pyvisa
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    try:
        write(instrument, "*IDN?")
        response = read(instrument)
        print(f"Instrument Response: {response}")
    except Exception as e:
        print(f"Failed to read from instrument: {e}")
    """
    # Validate the instrument type
    if not isinstance(instrument, pyvisa.resources.Resource):
        raise ValueError(f"Invalid instrument {instrument}. Please provide a valid PyVISA resource object.")

    try:
        # Read the response from the instrument
        response = instrument.read()
        return response

    except pyvisa.VisaIOError as e:
        print(f"Communication error while reading from the instrument: {e}")
        raise  # Re-raise the VisaIOError for the caller to handle
    except Exception as e:
        print(f"An unexpected error occurred while reading from the instrument: {e}")
        raise  # Re-raise any other exceptions for the caller to handle



def query(instrument: pyvisa.resources.Resource, instruction: str) -> str:
    """
    Sends a query (command) to a PyVISA instrument and returns the response.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A PyVISA instrument connection instance.
    instruction : str
        The command or query to send to the instrument.
        
    Returns:
    --------
    str
        The response from the instrument as a string.

    Raises:
    -------
    ValueError
        If the provided `instrument` is not a valid PyVISA resource.
    pyvisa.VisaIOError
        If there is a communication issue when sending the query or receiving the response.
    Exception
        For any unexpected errors during the operation.

    Example:
    --------
    import pyvisa
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")

    try:
        response = query(instrument, "*IDN?")
        print(f"Instrument Response: {response}")
    except Exception as e:
        print(f"Failed to send query: {e}")
    """
    # Validate the instrument type
    if not isinstance(instrument, pyvisa.resources.Resource):
        raise ValueError(f"Invalid instrument {instrument}. Please provide a valid PyVISA resource object.")

    try:
        # Send the query to the instrument and return the response
        response = instrument.query(instruction)
        print(f"Query '{instruction}' sent successfully. Response: {response}")
        return response
    
    except pyvisa.VisaIOError as e:
        print(f"Communication error while querying '{instruction}': {e}")
        raise  # Re-raise for the caller to handle
    except Exception as e:
        print(f"An unexpected error occurred while querying '{instruction}': {e}")
        raise  # Re-raise for the caller to handle



def query_power(instrument: pyvisa.resources.Resource, channel: int) -> float:
    """
    Queries the injected power of a specific channel on the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        A pyvisa ResourceManager object or instrument connection instance.
    channel : int
        The channel number (1 to 16) to query.

    Returns:
    --------
    float
        The injected power of the specified channel [Ohm].

    Raises:
    -------
    ValueError
        If the channel number is invalid or the response cannot be parsed.
    pyvisa.VisaIOError
        If there is a communication issue with the instrument.
    Exception
        For any unexpected errors during the operation.
        
    Example:
    --------
    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("GPIB0::12::INSTR")
    power = query_power(instrument, 1)
    print(f"Measured Power: {power} Watt")
    """
    
    # Validate the channel number
    if channel < 1 or channel > 16:
        raise ValueError(f"Invalid channel number {channel}. Please use a channel between 1 and 16.")
    
    # Validate the instrument type
    if not isinstance(instrument, pyvisa.resources.Resource):
        raise ValueError(f"Invalid instrument {instrument}. Please provide a valid PyVISA resource object.")
    
    try:
        response = instrument.query(f"RDGPWR? {channel}")
        
        # Check for empty response
        if not response.strip():
            raise ValueError(f"Empty response from instrument for channel {channel}")

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




def command_heater_range(instrument: pyvisa.resources.Resource, value: int) -> str:
    """
    Configure the heater range for the Lakeshore 370 instrument.

    Parameters
    ----------
    address : str
        The VISA address of the instrument.
    value : int
        The heater range value (must be one of the following):
        0 = Off,
        1 = 31.6 uA,
        2 = 100 uA,
        3 = 316 uA,
        4 = 1 mA,
        5 = 3.16 mA,
        6 = 10 mA,
        7 = 31.6 mA,
        8 = 100 mA.

    Returns
    -------
    str
        Confirmation message indicating successful execution.

    Raises
    ------
    ValueError
        If `value` is not in the range 0-8.
    """

    # Validate input
    if not (0 <= value <= 8):
        raise ValueError("Invalid value for heater range. Must be between 0 and 8.")

    # Use context manager to manage the resource
    try:
        instrument.write(f"HTRRNG {value}")
        
    except pyvisa.VisaIOError as e:
        print(f"Communication error: {e}")
        raise  # Raise the exception for the caller to handle
    except ValueError as e:
        print(f"Parsing error: {e}")
        raise  # Raise the exception for the caller to handle
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise  # Raise the exception for the caller to handle


def command_heater_output(instrument: pyvisa.resources.Resource, output: float) -> str:
    """
    Configure the heater output for the Lakeshore 370 instrument.

    Parameters
    ----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    output : float
        The heater output percentage. Must be between 0 and 100 [%].

    Returns
    -------
    str
        Confirmation message indicating successful execution.

    Raises
    ------
    ValueError
        If `output` is not between 0 and 100.
    RuntimeError
        If communication with the instrument fails.
    """

    # Validate input
    if not (0 <= output <= 100):
        raise ValueError("Invalid heater output. Must be a percentage between 0 and 100.")

    # Send the command
    try:
        instrument.write(f"MOUT {output}")
    except Exception as e:
        raise RuntimeError(f"Failed to set heater output: {e}")

    return f"Heater output successfully set to {output:.2f}%."


def query_scan_mode(instrument: pyvisa.resources.Resource) -> tuple[int, int]:
    """
    Query the scan mode of a channel on the Lakeshore 370 instrument.

    Parameters
    ----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.

    Returns
    -------
    tuple[int, int]
        A tuple containing:
        - channel (int): The channel number (1 to 16).
        - scan_mode (int): The scan mode of the channel:
            0 = Autoscan off,
            1 = Autoscan on.

    Raises
    ------
    RuntimeError
        If communication with the instrument fails or if the response format is unexpected.
    ValueError
        If the channel or scan mode values cannot be correctly parsed or are out of range.
    """

    try:
        # Query the instrument for the scan status
        answer = instrument.query("SCAN?").strip()

        # Parse the response
        if len(answer) < 4 or not answer[:2].isdigit() or not answer[3:4].isdigit():
            raise ValueError(f"Unexpected response format: {answer}")

        channel = int(answer[:2])
        scan_mode = int(answer[3:4])

        # Validate parsed values
        if not (1 <= channel <= 16):
            raise ValueError(f"Invalid channel number: {channel}")
        if scan_mode not in {0, 1}:
            raise ValueError(f"Invalid scan mode: {scan_mode}")

    except Exception as e:
        raise RuntimeError(f"Failed to query scan mode: {e}")

    return channel, scan_mode


def command_scan(instrument: pyvisa.resources.Resource, channel: int, scan_mode: int) -> str:
    """
    Configure the scan mode of the specified channel on the Lakeshore 370 instrument.

    Parameters
    ----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    channel : int
        The channel number to configure (1 to 16).
    scan_mode : int
        The scan mode to set:
            0 = Autoscan off,
            1 = Autoscan on.

    Returns
    -------
    str
        Confirmation message indicating successful execution.

    Raises
    ------
    ValueError
        If `channel` is not between 1 and 16 or `scan_mode` is not 0 or 1.
    RuntimeError
        If communication with the instrument fails.
    """

    # Validate inputs
    if not (1 <= channel <= 16):
        raise ValueError(f"Invalid channel number: {channel}. Must be between 1 and 16.")
    if scan_mode not in {0, 1}:
        raise ValueError(f"Invalid scan mode: {scan_mode}. Must be 0 (off) or 1 (on).")

    # Construct the command
    command = f"SCAN {channel},{scan_mode}"

    # Send the command
    try:
        instrument.write(command)
    except Exception as e:
        raise RuntimeError(f"Failed to set scan mode: {e}")

    return f"Scan mode successfully set to {scan_mode} for channel {channel}."

def command_resistance_range(
    instrument: pyvisa.resources.Resource,
    channel: int,
    mode: int,
    excitation: int,
    range_value: int,
    autorange: int,
    autoexcitation: int
) -> str:
    """
    Configure the resistance reading for a specific channel on the Lakeshore 370 instrument.

    Parameters
    ----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    channel : int
        The channel to configure (1 to 16, or 0 for all channels).
    mode : int
        The excitation mode:
            0 = voltage,
            1 = current.
    excitation : int
        The excitation range (1–22). See the manual for corresponding values.
    range_value : int
        The resistance range (1–22). See the manual for corresponding values.
    autorange : int
        The autorange mode:
            0 = autorange off,
            1 = autorange on.
    autoexcitation : int
        The autoexcitation mode:
            0 = autoexcitation on,
            1 = autoexcitation off.

    Returns
    -------
    str
        Confirmation message indicating successful execution.

    Raises
    ------
    ValueError
        If any input is out of the valid range.
    RuntimeError
        If communication with the instrument fails.
    """

    # Validate inputs
    if not (0 <= channel <= 16):
        raise ValueError(f"Invalid channel: {channel}. Must be between 0 and 16.")
    if mode not in {0, 1}:
        raise ValueError(f"Invalid mode: {mode}. Must be 0 (voltage) or 1 (current).")
    if not (1 <= excitation <= 22):
        raise ValueError(f"Invalid excitation: {excitation}. Must be between 1 and 22.")
    if not (1 <= range_value <= 22):
        raise ValueError(f"Invalid range_value: {range_value}. Must be between 1 and 22.")
    if autorange not in {0, 1}:
        raise ValueError(f"Invalid autorange: {autorange}. Must be 0 (off) or 1 (on).")
    if autoexcitation not in {0, 1}:
        raise ValueError(f"Invalid autoexcitation: {autoexcitation}. Must be 0 (on) or 1 (off).")

    # Construct the command string
    command = (
        f"RDGRNG {channel},{mode},{excitation},{range_value},{autorange},{autoexcitation}"
    )

    # Send the command to the instrument
    try:
        instrument.write(command)
    except Exception as e:
        raise RuntimeError(f"Failed to set resistance range: {e}")

    return (
        f"Resistance range successfully configured for channel {channel} with mode={mode}, "
        f"excitation={excitation}, range_value={range_value}, autorange={autorange}, "
        f"autoexcitation={autoexcitation}."
    )


def query_intensity_output(instrument: pyvisa.resources.Resource) -> float:
    """
    Query the intensity output of the Lakeshore 370 instrument.

    Parameters
    ----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.

    Returns
    -------
    float
        The intensity output in amperes [A].

    Raises
    ------
    ValueError
        If the heater range index is invalid.
    RuntimeError
        If querying the instrument fails.

    Example
    -------
    intensity_output = query_intensity_output(instrument)
    print(f"Intensity Output: {intensity_output:.6f} A")
    """

    # Define heater range values in amperes
    heater_range_values = [
        0,
        31.6e-6,
        100e-6,
        316e-6,
        1e-3,
        3.16e-3,
        10e-3,
        31.6e-3,
        100e-3,
    ]

    try:
        # Query the heater range index and percentage output
        heater_range_index = query_heater_range(instrument)
        heater_percentage = query_heater_output(instrument)

        # Validate the heater range index
        if not (0 <= heater_range_index < len(heater_range_values)):
            raise ValueError(f"Invalid heater range index: {heater_range_index}")

        # Calculate and return the intensity output (because percentage)
        intensity_output = heater_range_values[heater_range_index] * heater_percentage / 100
        return intensity_output

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Failed to query intensity output: {e}")


def query_temperature_control_parameters(instrument: pyvisa.resources.Resource) -> tuple:
    """
    Queries the temperature control parameters of the Lakeshore 370 instrument.

    Parameters
    ----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.

    Returns
    -------
    tuple
        A tuple containing the following parameters:
        - channel (int): The channel (1 to 16).
        - filtering (int): Filter status (0 = unfiltered, 1 = filtered).
        - unit (int): Setpoint unit (1 = Kelvin, 2 = Ohm).
        - delay (int): Delay in seconds for setpoint change (1–255) [s].
        - current_power (int): Heater output display (1 = current, 2 = power).
        - htr_limit (int): Maximum heater range (1 to 8).
        - htr_resistance (float): Heater load in ohms [Ohm].

    Raises
    ------
    RuntimeError
        If communication with the instrument fails.
    ValueError
        If the parsing of the response fails or the response format is invalid.

    Example
    -------
    params = query_temperature_control_parameters(instrument)
    print(params)
    """

    try:
        # Query the instrument for control parameters
        response = instrument.query("CSET?")

        # Ensure the response length matches the expected format
        if len(response) < 23:
            raise ValueError(f"Invalid response length: {len(response)} characters.")

        # Parse the response based on the expected format
        channel = int(response[0:2])
        filtering = int(response[3:4])
        unit = int(response[5:6])
        delay = int(response[7:10])
        current_power = int(response[11:12])
        htr_limit = int(response[13:14])
        htr_resistance = float(response[15:23])

        # Validate parsed values
        if not (1 <= channel <= 16):
            raise ValueError(f"Invalid channel: {channel}. Must be between 1 and 16.")
        if filtering not in {0, 1}:
            raise ValueError(f"Invalid filtering: {filtering}. Must be 0 (unfiltered) or 1 (filtered).")
        if unit not in {1, 2}:
            raise ValueError(f"Invalid unit: {unit}. Must be 1 (Kelvin) or 2 (Ohm).")
        if not (1 <= delay <= 255):
            raise ValueError(f"Invalid delay: {delay}. Must be between 1 and 255.")
        if current_power not in {1, 2}:
            raise ValueError(f"Invalid current_power: {current_power}. Must be 1 (current) or 2 (power).")
        if not (1 <= htr_limit <= 8):
            raise ValueError(f"Invalid htr_limit: {htr_limit}. Must be between 1 and 8.")

        # Return the parsed and validated parameters
        return channel, filtering, unit, delay, current_power, htr_limit, htr_resistance

    except pyvisa.VisaIOError as e:
        raise RuntimeError(f"Communication error with instrument: {e}")
    except ValueError as e:
        raise ValueError(f"Parsing error: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")


def command_temperature_control_parameters(
    instrument: pyvisa.resources.Resource, 
    channel: int, 
    filtering: int, 
    unit: int, 
    delay: int, 
    current_power: int, 
    htr_limit: int, 
    htr_resistance: float
) -> None:
    """
    Configures the temperature control parameters of the Lakeshore 370 instrument.

    Parameters
    ----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    channel : int
        The channel of the instrument to configure (1 to 16).
    filtering : int
        Filter status (0 = unfiltered, 1 = filtered).
    unit : int
        Setpoint unit (1 = Kelvin, 2 = Ohm).
    delay : int
        Delay in seconds for setpoint change during autoscanning (1–255) [s].
    current_power : int
        Specifies heater output display (1 = current, 2 = power).
    htr_limit : int
        Maximum heater range (1 to 8).
    htr_resistance : float
        Heater load in ohms [Ohm].

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If any of the input parameters are out of their valid ranges.

    Example
    -------
    command_temperature_control_parameters(
        instrument, 1, 0, 1, 10, 1, 4, 25.0
    )
    """

    # Input validation
    if not (1 <= channel <= 16):
        raise ValueError(f"Invalid channel: {channel}. Must be between 1 and 16.")
    if filtering not in {0, 1}:
        raise ValueError(f"Invalid filtering: {filtering}. Must be 0 (unfiltered) or 1 (filtered).")
    if unit not in {1, 2}:
        raise ValueError(f"Invalid unit: {unit}. Must be 1 (Kelvin) or 2 (Ohm).")
    if not (1 <= delay <= 255):
        raise ValueError(f"Invalid delay: {delay}. Must be between 1 and 255 seconds.")
    if current_power not in {1, 2}:
        raise ValueError(f"Invalid current_power: {current_power}. Must be 1 (current) or 2 (power).")
    if not (1 <= htr_limit <= 8):
        raise ValueError(f"Invalid htr_limit: {htr_limit}. Must be between 1 and 8.")
    if htr_resistance <= 0:
        raise ValueError(f"Invalid htr_resistance: {htr_resistance}. Must be greater than 0.")

    try:
        # Construct the command string
        command = f"CSET {channel},{filtering},{unit},{delay},{current_power},{htr_limit},{htr_resistance:.1f}"
        
        # Send the command to the instrument
        instrument.write(command)
        print(f"Command sent: {command}")

    except pyvisa.VisaIOError as e:
        print(f"Communication error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def command_setpoint(instrument: pyvisa.resources.Resource, setpoint: float) -> None:
    """
    Sets the desired setpoint value on the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    setpoint : float
        The setpoint value in Kelvin [K] or Ohms [Ω].

    Returns:
    --------
    None

    Example:
    --------
    command_setpoint(instrument, 300.0)
    """
    try:
        # Send the setpoint command to the instrument
        instrument.write(f"SETP {setpoint}")
        print(f"Setpoint command sent: {setpoint}.")

    except pyvisa.VisaIOError as e:
        print(f"Communication error with instrument: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def query_setpoint(instrument: pyvisa.resources.Resource) -> float:
    """
    Queries the current setpoint value of the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.

    Returns:
    --------
    float
        The current setpoint value in Kelvin [K] or Ohms [Ω].

    Example:
    --------
    setpoint = query_setpoint(instrument)
    print(f"Setpoint: {setpoint} K")
    """
    try:
        # Query the setpoint value from the instrument
        response = instrument.query("SETP?").strip()  # Ensure any trailing whitespace is removed
        
        # Convert the response to a float and return
        return float(response)
    
    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing the response value: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def command_pid_parameters(
    instrument: pyvisa.resources.Resource, 
    p: float, 
    i: int, 
    d: int
) -> None:
    """
    Configures the PID parameters for the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    p : float
        The proportional ("P") parameter.
    i : int
        The integral ("I") parameter [s].
    d : int
        The derivative ("D") parameter [s].

    Returns:
    --------
    None

    Example:
    --------
    command_pid_parameters(instrument, 10.0, 5, 2)
    """
    try:
        # Send the PID configuration command to the instrument
        command = f"PID {p},{i},{d}"
        instrument.write(command)
        print(f"PID parameters set: P={p}, I={i}, D={d}")
    
    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def query_pid_parameters(instrument: pyvisa.resources.Resource):
    """
    Queries the PID parameters for the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.

    Returns:
    --------
    tuple
        A tuple containing:
        - p (float): The proportional ("P") parameter.
        - i (int): The integral ("I") parameter [s].
        - d (int): The derivative ("D") parameter [s].

    Example:
    --------
    p, i, d = query_pid_parameters(instrument)
    print(f"PID Parameters: P={p}, I={i}, D={d}")
    """
    try:
        # Query the PID parameters from the instrument
        answer = instrument.query("PID?")  # Assuming "PID?" is the correct query for PID parameters

        # Parse the response (assuming the response format is 'P=<value>,I=<value>,D=<value>')
        parts = answer.split(',')
        
        # Ensure the response has the expected format
        if len(parts) != 3:
            raise ValueError(f"Unexpected response format: {answer}")

        p = float(parts[0].split('=')[1].strip())
        i = int(parts[1].split('=')[1].strip())
        d = int(parts[2].split('=')[1].strip())

        return p, i, d

    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
        return None
    except ValueError as e:
        print(f"Parsing error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def query_interface_mode(instrument: pyvisa.resources.Resource):
    """
    Queries the interface mode of the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.

    Returns:
    --------
    int
        The interface mode:
        - 0 = local
        - 1 = remote
        - 2 = remote with local lockout

    Example:
    --------
    interface_mode = query_interface_mode(instrument)
    print(f"Interface Mode: {interface_mode}")
    """
    try:
        # Query the interface mode from the instrument
        answer = instrument.query("MODE?")
        
        # Convert the response to integer
        interface_mode = int(answer)

        # Return the interface mode
        return interface_mode

    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
        return None
    except ValueError as e:
        print(f"Parsing error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    


def command_interface_mode(instrument: pyvisa.resources.Resource, interface_mode: int) -> None:
    """
    Configures the interface mode of the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    interface_mode : int
        The interface mode to set (0 = local, 1 = remote, 2 = remote with local lockout).

    Returns:
    --------
    None

    Example:
    --------
    command_interface_mode(instrument, 1)
    """
    try:
        # Validate the input interface mode
        if interface_mode not in [0, 1, 2]:
            raise ValueError("Invalid interface mode. Must be 0, 1, or 2.")

        # Convert interface mode to string and send the command
        instrument.write(f"MODE {interface_mode}")
        
    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
    except ValueError as e:
        print(f"Input error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def command_channel_parameter(
        instrument: pyvisa.resources.Resource, 
        channel: int, 
        channel_status: int, 
        dwell: int, 
        pause: int, 
        curve_number: int, 
        coefficient: int
) -> None:
    """
    Configures the channel parameters on the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    channel : int
        The channel number (1 to 16).
    channel_status : int
        The status of the channel (0 = Off, 1 = On).
    dwell : int
        The dwell time in seconds.
    pause : int
        The pause time in seconds.
    curve_number : int
        The curve number.
    coefficient : int
        The temperature coefficient (1 = negative, 2 = positive).

    Returns:
    --------
    None

    Example:
    --------
    command_channel_parameter(instrument, 1, 1, 10, 5, 3, 1)
    """
    try:
        # Validate input values
        if not (1 <= channel <= 16):
            raise ValueError("Channel must be between 1 and 16.")
        if channel_status not in [0, 1]:
            raise ValueError("Channel status must be 0 (Off) or 1 (On).")
        if dwell < 0 or pause < 0:
            raise ValueError("Dwell and pause times must be non-negative.")
        if coefficient not in [1, 2]:
            raise ValueError("Coefficient must be 1 (negative) or 2 (positive).")

        # Construct the command string using f-strings for better readability
        command = f"INSET {channel},{channel_status},{dwell},{pause},{curve_number},{coefficient}"

        # Send the command to the instrument
        instrument.write(command)

    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
    except ValueError as e:
        print(f"Input error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



def query_channel_parameter(instrument: pyvisa.resources.Resource, channel: int):
    """
    Queries the parameters of a specified channel on the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    channel : int
        The channel number (1 to 16).

    Returns:
    --------
    tuple :
        A tuple containing:
        - channel_status (int): The status of the channel (0 = Off, 1 = On)
        - dwell (int): The dwell time in seconds
        - pause (int): The pause time in seconds
        - curve_number (int): The curve number
        - coefficient (int): The temperature coefficient (1 = negative, 2 = positive)

    Example:
    --------
    channel_status, dwell, pause, curve_number, coefficient = query_channel_parameter(instrument, 1)
    """
    try:
        # Validate that the channel is within the valid range (1 to 16)
        if not (1 <= channel <= 16):
            raise ValueError("Channel must be between 1 and 16.")
        
        # Query the instrument for the channel parameters
        response = instrument.query(f"INSET? {channel}")
        
        # Assuming the response format is consistent, parse it
        # Example response format: "0,1000,500,3,1" (values separated by commas)
        parts = response.split(',')
        
        if len(parts) != 5:
            raise ValueError("Unexpected response format from the instrument.")
        
        # Parse values from the response
        channel_status = int(parts[0])
        dwell = int(parts[1])
        pause = int(parts[2])
        curve_number = int(parts[3])
        coefficient = int(parts[4])
        
        # Return the parsed values
        return channel_status, dwell, pause, curve_number, coefficient

    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing response: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def query_temperature_control_mode(instrument: pyvisa.resources.Resource) -> int:
    """
    Queries the current temperature control mode of the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.

    Returns:
    --------
    int
        The temperature control mode:
        - 1 = Closed-loop PID
        - 2 = Zone tuning
        - 3 = Open loop
        - 4 = Off

    Example:
    --------
    mode = query_temperature_control_mode(instrument)
    print(f"Current Temperature Control Mode: {mode}")
    """
    try:
        # Query the instrument for the control mode
        response = instrument.query("CMODE?")

        # Parse the response to integer
        mode = int(response.strip())  # Remove any trailing whitespace

        # Validate the response mode
        if mode not in [1, 2, 3, 4]:
            raise ValueError(f"Unexpected mode value received: {mode}")

        # Return the parsed mode
        return mode

    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing response: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def command_temperature_control_mode(instrument: pyvisa.resources.Resource, mode: int) -> None:
    """
    Sets the temperature control mode of the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    mode : int
        The temperature control mode to set:
        - 1 = Closed-loop PID
        - 2 = Zone tuning
        - 3 = Open loop
        - 4 = Off

    Returns:
    --------
    None

    Example:
    --------
    command_temperature_control_mode(instrument, 1)
    """

    # Validate the mode input to ensure it's within the allowed range (1 to 4)
    if mode not in [1, 2, 3, 4]:
        raise ValueError(f"Invalid mode value: {mode}. Must be 1, 2, 3, or 4.")

    try:
        # Convert mode to string and send the command to the instrument
        instrument.write(f"CMODE {mode}")
        print(f"Temperature control mode set to: {mode}")

    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def query_heater_output(instrument: pyvisa.resources.Resource) -> float:
    """
    Queries the heater output from the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.

    Returns:
    --------
    float
        The heater output in percentage [0-100%].

    Raises:
    -------
    ValueError
        If the response is not a valid float.
    pyvisa.VisaIOError
        If there is a communication error with the instrument.

    Example:
    --------
    output = query_heater_output(instrument)
    print(f"Heater Output: {output}%")
    """
    try:
        # Query the heater output
        response = instrument.query("HTR?")
        
        # Try converting the response to float
        output = float(response.strip())  # strip any extra spaces or newline
        
        # Ensure the output is within the expected range (0 to 100%)
        if not (0 <= output <= 100):
            raise ValueError(f"Invalid heater output value: {output}. Expected a value between 0 and 100.")
        
        return output

    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
        raise  # Reraise the error to handle it elsewhere if needed
    except ValueError as e:
        print(f"Error parsing heater output: {e}")
        raise  # Reraise to handle invalid format errors
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise  # Reraise unexpected errors


def query_heater_range(instrument: pyvisa.resources.Resource) -> int:
    """
    Queries the heater range from the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.

    Returns:
    --------
    int
        The heater range value:
        - 0 = Off
        - 1 = 31.6 µA
        - 2 = 100 µA
        - 3 = 316 µA
        - 4 = 1 mA
        - 5 = 3.16 mA
        - 6 = 10 mA
        - 7 = 31.6 mA
        - 8 = 100 mA

    Raises:
    -------
    ValueError
        If the response is not a valid integer or is out of the expected range.
    pyvisa.VisaIOError
        If there is a communication error with the instrument.

    Example:
    --------
    heater_range = query_heater_range(instrument)
    print(f"Heater Range: {heater_range}")
    """
    try:
        # Query the heater range
        response = instrument.query("HTRRNG?").strip()
        
        # Convert the response to an integer
        value = int(response)
        
        # Ensure the value is within the expected range (0-8)
        if value < 0 or value > 8:
            raise ValueError(f"Invalid heater range value: {value}. Expected a value between 0 and 8.")
        
        return value
    
    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
        raise  # Reraise the error to handle it elsewhere if needed
    except ValueError as e:
        print(f"Error parsing heater range: {e}")
        raise  # Reraise the error if the response is invalid
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise  # Reraise unexpected errors


def query_resistance_range(
    instrument: pyvisa.resources.Resource, channel: int
) -> tuple:
    """
    Queries the resistance range for a specific channel from the Lakeshore 370 instrument.

    Parameters:
    -----------
    instrument : pyvisa.resources.Resource
        The PyVISA instrument resource instance.
    
    channel : int
        The channel number (1 to 16). Use 0 to query all channels.

    Returns:
    --------
    tuple :
        - mode (int) : The excitation mode (0 = voltage, 1 = current)
        - excitation (int) : The excitation range (1 = 2 uV / 1 pA, etc.)
        - range_value (int) : The resistance range (1 = 2 mOhm, 2 = 6.32 mOhm, etc.)
        - autorange (int) : The autorange mode (0 = off, 1 = on)
        - autoexcitation (int) : The autoexcitation mode (0 = on, 1 = off)
    
    Raises:
    -------
    ValueError
        If the response format is not valid or out of the expected range.
    pyvisa.VisaIOError
        If there is a communication error with the instrument.

    Example:
    --------
    mode, excitation, range_value, autorange, autoexcitation = query_resistance_range(instrument, 1)
    print(f"Mode: {mode}, Excitation: {excitation}, Range: {range_value}, Autorange: {autorange}, Autoexcitation: {autoexcitation}")
    """
    try:
        # Query the resistance range
        answer = instrument.query(f"RDGRNG? {channel}").strip()

        # Ensure the answer is long enough for all parameters
        if len(answer) < 11:
            raise ValueError(f"Invalid response from instrument: {answer}. Response too short.")

        # Parse the values from the response
        mode = int(answer[0:1])
        excitation = int(answer[2:4])
        range_value = int(answer[5:7])
        autorange = int(answer[8:9])
        autoexcitation = int(answer[10:11])

        # Validate the parsed values (simple range checks)
        if mode not in [0, 1]:
            raise ValueError(f"Invalid excitation mode: {mode}. Expected 0 or 1.")
        if excitation < 1 or excitation > 22:
            raise ValueError(f"Invalid excitation range: {excitation}. Expected between 1 and 22.")
        if range_value < 1 or range_value > 22:
            raise ValueError(f"Invalid range value: {range_value}. Expected between 1 and 22.")
        if autorange not in [0, 1]:
            raise ValueError(f"Invalid autorange mode: {autorange}. Expected 0 or 1.")
        if autoexcitation not in [0, 1]:
            raise ValueError(f"Invalid autoexcitation mode: {autoexcitation}. Expected 0 or 1.")

        # Return the parsed and validated values
        return mode, excitation, range_value, autorange, autoexcitation
    
    except pyvisa.VisaIOError as e:
        print(f"Communication error with the instrument: {e}")
        raise  # Reraise the error for the caller to handle
    except ValueError as e:
        print(f"Error parsing resistance range response: {e}")
        raise  # Reraise the error if the response is invalid
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise  # Reraise unexpected errors





