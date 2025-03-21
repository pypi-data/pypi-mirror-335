#%% Ohm_law
def ohm_law(current = 0, voltage = 0, power = 0 , resistance = 0, display = True) -> float:
    
    """
    ========== DESCRIPTION ==========

    This function calculate either the current, the voltage, the power 
    or the resistance, depending on the input parameters.

    ========== VALIDITY ==========

    Always

    ========== FROM ==========

    The famous Ohm's law

    ========== INPUT ==========

    <current>
        -- float --
    	The current
        [A]
        
    <voltage>
        -- float --
    	The voltage
        [V]
        
    <power>
        -- float --
    	The power
        [W]
        
    <resistance>
        -- float --
    	The resistance
        [Ohms]
        
    <display>
        -- boolean --
        Is printing the result ? Default is True.
        
    ========== OUTPUT ==========

    <current>
        -- float --
    	The current
        [A]
        
    <voltage>
        -- float --
    	The voltage
        [V]
        
    <power>
        -- float --
    	The power
        [W]
        
    <resistance>
        -- float --
    	The resistance
        [Ohms]

    ========== STATUS ==========

    Status : Checked

    """

    # If current and power are provided
    if current != 0 and power != 0:
        
        voltage = power/current
        resistance = power/current**2
       
    # If current and voltage are provided
    if current != 0 and voltage != 0:
        
        power = current*voltage
        resistance = voltage/current
      
    # If current and resistance are provided
    if current != 0 and resistance != 0:
        
        power = resistance*current**2
        voltage = resistance*current
      
    # If power and voltage are provided
    if power != 0 and voltage != 0:
        
        current = power/voltage
        resistance = voltage**2/power
       
    # If power and resistance are provided
    if power != 0 and resistance != 0:
        
        current = (power/resistance)**0.5
        voltage = (power*resistance)**0.5
       
    # If voltage and resistance are provided
    if voltage != 0 and resistance != 0:
        
        current = voltage/resistance
        power = voltage**2/resistance
    
    print('')
    if display:
        # Print the results for current
        if current >= 1 :
            print_current = round(current,3)
            print('Current      = ' + str(print_current) + ' A')
            
        if 1 > current >= 1e-3 :
            print_current = round(current*1e3,3)
            print('Current      = ' + str(print_current) + ' mA')
            
        if 1e-3 > current >= 1e-6 :
            print_current = round(current*1e6,3)
            print('Current      = ' + str(print_current) + ' uA')
            
        if 1e-6 > current >= 1e-9 :
            print_current = round(current*1e9,3)
            print('Current      = ' + str(print_current) + ' nA')
            
        # Print the results for voltage
        if voltage >= 1 :
            print_voltage = round(voltage,3)
            print('Voltage      = ' + str(print_voltage) + ' V')
            
        if 1 > voltage >= 1e-3 :
            print_voltage = round(voltage*1e3,3)
            print('Voltage      = ' + str(print_voltage) + ' mV')
            
        if 1e-3 > voltage >= 1e-6 :
            print_voltage = round(voltage*1e6,3)
            print('Voltage      = ' + str(print_voltage) + ' uV')
            
        if 1e-6 > voltage >= 1e-9 :
            print_voltage = round(voltage*1e9,3)
            print('Voltage      = ' + str(print_voltage) + ' nV')
            
        # Print the results for power
        if power >= 1 :
            print_power = round(power,3)
            print('Power        = ' + str(print_power) + ' W')
            
        if 1 > power >= 1e-3 :
            print_power = round(power*1e3,3)
            print('Power        = ' + str(print_power) + ' mW')
            
        if 1e-3 > power >= 1e-6 :
            print_power = round(power*1e6,3)
            print('Power        = ' + str(print_power) + ' uW')
            
        if 1e-6 > power >= 1e-9 :
            print_power = round(power*1e9,3)
            print('Power        = ' + str(print_power) + ' nW')
            
        if 1e-9 > power >= 1e-12 :
            print_power = round(power*1e12,3)
            print('Power        = ' + str(print_power) + ' pW')   
            
        if 1e-12 > power >= 1e-15 :
            print_power = round(power*1e15,3)
            print('Power        = ' + str(print_power) + ' fW')
            
        # Print the results for resistance
        if resistance >= 1e6 :
            print_resistance = round(resistance*1e-6,3)
            print('Resistance   = ' + str(print_resistance) + ' MOhms')
            
        if 1e6 > resistance >= 1e3 :
            print_resistance = round(resistance*1e-3,3)
            print('Resistance   = ' + str(print_resistance) + ' kOhms')
    
        if 1e3 > resistance >= 1 :
            print_resistance = round(resistance*1,3)
            print('Resistance   = ' + str(print_resistance) + ' Ohms')
    
        if 1 > resistance >= 1e-3 :
            print_resistance = round(resistance*1e3,3)
            print('Resistance   = ' + str(print_resistance) + ' mOhms')
            
        if 1e-3 > resistance >= 1e-6 :
            print_resistance = round(resistance*1e6,3)
            print('Resistance   = ' + str(print_resistance) + ' uOhms')
        
    # Export the results
    return current, voltage, power, resistance    


#%% 

# On channel 2
current, voltage, power, resistance = ohm_law(power=0.1,resistance=100,display=False)
resistance = 10000

voltage = voltage * 0.1

current, voltage, power, resistance = ohm_law(voltage=voltage,resistance=resistance)


        