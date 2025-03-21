def molar_specific_heat(temperature, pressure, fraction_3he):
    """
    ========== DESCRIPTION ==========

    This function return the molar specific heat of a mixture of helium 3 & helium 4
    
    ========== FROM ==========

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the mixture
        [K]

    <pressure>
        -- float --
        The pressure of the mixture
        [Pa]

    <fraction_3he>
        -- float --
        The fraction of helium 3 on the mixture
        []

    ========== OUTPUT ==========

    <molar_specific_heat>
        -- float --
        The molar specific heat of helium 3/4 mixture
        [J].[K]**(-1).[mol]**(-1)


    ========== STATUS ==========

    Status : Checked

    ========== NOTES ===========

    """

    ################## MODULES ################################################

    from cryopy.helium import helium4
    from cryopy.helium import fermi

    ################## FUNCTION ###############################################

    return fraction_3he * fermi.molar_specific_heat(temperature, pressure, fraction_3he) + (1 - fraction_3he) * helium4.molar_specific_heat(temperature, pressure)

#%%
def molar_volume(temperature, pressure, fraction_3he):
    """
    ========== DESCRIPTION ==========

    This function return the molar volume of a mixture of helium 3 & helium 4 

    ========== FROM ==========

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of helium 4
        [K]

    <pressure>
        -- float --
        The pressure of helium 4
        [Pa]

    <fraction_3he>
        -- float --
        The fraction of helium 3 on the mixture
        []

    ========== OUTPUT ==========

    <molar_volume>
        -- float --
        The molar volume of the mixture
        [m]**(3).[mol]**(-1)

    ========== STATUS ==========

    Status : Checked
    
    ========== NOTES ==========

    """

    ################## MODULES ################################################

    from cryopy.helium import helium4
    from cryopy.helium import helium3

    ################## FUNCTION ###############################################

    return fraction_3he*helium3.molar_volume(temperature, pressure) + (1-fraction_3he)*helium4.molar_volume(temperature, pressure)

#%%
def molar_mass(temperature, pressure,fraction_3he):
    """
    ========== DESCRIPTION ==========

    This function return the molar mass of a mixture of helium 3 & 
    helium 4 

    ========== FROM ==========

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the mixture
        [K]

    <pressure>
        -- float --
        The pressure of the mixture
        [Pa]

    <fraction_3he>
        -- float --
        The fraction of helium 3 on mixture
        []

    ========== OUTPUT ==========

    <molar_mass>
        -- float --
        The molar mass of the mixture
        [kg].[mol]**(-1)

    ========== STATUS ==========

    Status : 
    
    ========== NOTES ==========


    """

    ################## MODULES ################################################

    from cryopy.helium import helium4
    from cryopy.helium import helium3

    ################## FUNCTION ###############################################

    return fraction_3he*helium3.molar_mass(temperature,pressure)+(1-fraction_3he)*helium4.molar_mass(temperature,pressure)

#%%
def osmotic_pressure(temperature, pressure, fraction_3he):
    """
    ========== DESCRIPTION ==========

    This function return the osmotic pressure of a mixture of helium 3 & 
    helium 4 

    ========== FROM ==========

    Kuerten et al. (1987)
        Thermodynamic properties of liquid 3He-4He mixtures at zero pressure for temperatures below 250 mK and 3He concentrations below 8% - Equation (24)

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of helium 4
        [K]

    <pressure>
        -- float --
        The pressure of helium 4
        [Pa]

    <fraction_3he>
        -- float --
        The fraction of helium 3 on mixture
        []

    ========== OUTPUT ==========

    <osmotic_pressure>
        -- float --
        The osmotic pressure of the mixture
        [Pa]

    ========== STATUS ==========

    Status : Checked

    ========== NOTES ==========
    
    2020-02-25:
        Modification of value to T=0 by a polynôm using values from table (19)
        instead of equation (45)
    
    """

    ################## MODULES ################################################

    import numpy as np
    from cryopy.helium import helium4
    from cryopy.helium import fermi
    from cryopy.helium import helium7
    from scipy.misc import derivative
    from scipy.integrate import quad

    ################## INITIALISATION #########################################

    coefficients = [7.71714007e+09, -2.28854069e+09, 2.80349751e+08, -2.01610697e+07, 7238437e+06, 3.68490992e+03,
                    -4.60897007e-01]
    polynom = np.poly1d(coefficients)

    t = temperature / fermi.temperature_function(temperature, pressure, fraction_3he)

    # Temporary function for derivation of fermi temperature 
    def fun(fraction_3he):
        return fermi.temperature_function(temperature, pressure, fraction_3he)

    ################## FUNCTION ###############################################

    if temperature == 0:
        return polynom(fraction_3he)
    else:
        return helium7.osmotic_pressure(0, pressure, fraction_3he) + fraction_3he ** 2 / helium4.molar_volume(
            temperature, pressure) * derivative(fun, fraction_3he) * quad(fermi.molar_specific_heat, 0, t, fraction_3he)


#%%
def molar_entropy(temperature, pressure, fraction_3he):
    """
    ========== DESCRIPTION ==========


    This function return the molar entropy of a mixture of helium 3 & 
    helium 4 

    ========== VALIDITE ==========

    0 <= Temperature <= 2 K
    0 <= Pression <= 0 Pa
    0 <= Concentration3He <= 100 %

    ========== SOURCE ==========

    KUERTEN - Thermodynamic properties of liquid 3He-4He mixtures
    at zero pressure for temperatures below 250 mK and 3He concentrations
    below 8% - Equation (2)

    ========== ENTREE ==========

    [Temperature]
        La température du fluide en [K]
    [Pression]
        La pression en [Pa]
    [Concentration3He]
        La concentration de 3He dans le mélange 3He-4He sans unité

    ========== SORTIE ==========

    [EntropieMolaire]
        L'entropie molaire du mélange 3He-4He en [J/K/mol]

    ========== STATUS ==========

    Status : 

    ========== A FAIRE ==========

    Contrainte sur la pression à vérifier
    A verifier pour les prochaines valeurs de l'entropie 3He et 4He

    """

    ################## MODULES ###############################################

    from cryopy.helium import helium4
    from cryopy.helium import fermi
    from cryopy.helium import helium3

    ################## CONDITION 1 ####################################
    # helium 4 est superfluide, helium 3 assimilable à un liquide de fermi
    if temperature < TemperatureTransition(Pression, Concentration3He) or Concentration3He < ConcentrationConcentre(
            Temperature, Pression):
        return Concentration3He * fermi.molar_entropy(temperature, pressure, fraction_3he) + (
                1 - Concentration3He) * helium4.molar_entropy(temperature, pressure)

    else:
        # helium 4 est normal, helium 3 est normal
        return fraction_3he * helium3.molar_entropy(temperature, pressure, fraction_3he) + (
                1 - fraction_3he) * helium4.molar_entropy(temperature, pressure)

#%%
def tricritical_temperature(pressure):
    """
    ========== DESCRIPTION ==========

    This function return the temperature of helium 3 of the tricritical point at a given pressure

    ========== VALIDITE ==========

    <pressure> : [0 -> 22e5]

    ========== FROM ==========

    Chaudhry et al. (2010) 
        "Thermodynamic Properties of Liquid 3He-4He Mixtures Between 0–10 bar below 1.5 K"

    ========== INPUT ==========

    <pressure>
        -- float --
        The pressure of the mixture
        [Pa]

    ========== OUTPUT ==========

    <tricritical_temperature>
        -- float --
        The temperature of the mixture at the tricritical point
        []

    ========== STATUS ==========

    Status : 

    """
    ################## MODULES ################################################

    from cryopy.helium import helium7

    ################## CONDITION ##############################################

    assert 0 <= pressure <= 22e5 and pressure >= 0, 'The function helium7.tricritical_temperature is not defined for P = ' + str(pressure) + ' Pa'

    ################## INITIALISATION #########################################

    # Convert [Pa] to [Bar]
    pressure = pressure * 1e-5

    ################## FUNCTION ###############################################

    if pressure == 0:
        return 0.867
    else:
        return helium7.tricritical_temperature(0) - 0.12992576 * pressure / (pressure + 2.5967345) - 6.457263e-4 * pressure

#%%
def tricritical_fraction_3he(pressure):
    """
    ========== DESCRIPTION ==========

    This function return the fraction of helium 3 on the tri critical point at a given pressure

    ========== VALIDITE ==========

    <pressure> : [0 -> 22e5]

    ========== FROM ==========

    Chaudhry et al. (2010)
        "Thermodynamic Properties of Liquid 3He-4He Mixtures Between 0–10 bar below 1.5 K"

    ========== INPUT ==========

    <pressure>
        -- float --
        The pressure of the mixture
        [Pa]

    ========== OUTPUT ==========

    <tricritical_fraction_3he>
        -- float --
        The fraction of helium 3 at the tricritical point
        []

    ========== STATUS ==========

    Status : 2022-12-22

    """
    ################## MODULES ###############################################

    from cryopy.helium import helium7

    ################## CONDITION ##############################################

    assert 0 <= pressure <= 22e5, 'The function helium7.tricritical_fraction_3he is not defined for p = ' + str(pressure) + ' bar'

    ################## INITIALISATION #########################################

    ################## FUNCTION ###############################################

    if pressure == 0:
        return 0.674

    else:
        return helium7.tricritical_fraction_3he(0) + 0.3037124 * (helium7.tricritical_temperature(0) - helium7.tricritical_temperature(pressure)) - 4.41225e6 * (helium7.tricritical_temperature(0) - helium7.tricritical_temperature(pressure)) ** 9

#%%
def transition_temperature(pressure, fraction_3he):
    """
    ========== DESCRIPTION ==========

    This function return the transition temperature

    ========== VALIDITY ==========

    <pressure> : [0 -> 10e5]
    <fraction_3he> : [0 -> helium7.tricritical_fraction_3he(pressure)]
 
    ========== FROM ==========

    Chaudhry et al. (2010) 
        "Thermodynamic Properties of Liquid 3He-4He Mixtures Between 0–10 bar below 1.5 K"

    ========== ENTREE ==========

    <pressure>
        -- float --
        The pressure of the mixture
        [Pa]
        
    <fraction_3he>
        -- float --
        The fraction of helium 3 on the mixture
        []
        
    ========== SORTIE ==========

    <transition_temperature>
        -- float --
        The transition temperature 
        [K]

    ========== STATUS ==========

    Status : 

    """

    ################## MODULES ################################################

    import numpy as np
    from cryopy.helium import helium7

    ################## CONDITIONS #############################################

    assert 0 <= pressure <= 10e5 , 'The function helium7.transition_temperature is not defined for P = ' + str(pressure) + ' Pa'

    assert 0 <= fraction_3he <= helium7.tricritical_fraction_3he(pressure), 'The function helium7.transition_temperature is not defined for x = ' + str(fraction_3he * 100) + ' %'

    ################## INITIALISATION #########################################

    # Convert from [Pa] to [Bar]
    pressure = pressure * 1e-5

    D1 = np.poly1d([0.0009255,0.0024823,-2.620259])
    D2 = np.poly1d([0.0009397,0.0013175,-1.023726])

    ################## FUNCTION ###############################################

    return helium7.tricritical_temperature(pressure) + D1(pressure) * (fraction_3he - helium7.tricritical_fraction_3he(pressure)) + D2(pressure) * (fraction_3he - helium7.tricritical_fraction_3he(pressure)) ** 2

#%%
def fraction_3he_dilute(temperature, pressure):
    """
    ========== DESCRIPTION ==========

    This function return the fraction of helium 3 inside the dilute phase

    ========== VALIDITY ==========

    <temperature> : [0 -> helium7.tricritical_temperature(pressure)]
    <pressure> : [0 -> 10e5]

    ========== FROM ==========

    Chaudhry et al. (2010) 
        "Thermodynamic Properties of Liquid 3He-4He Mixtures Between 0–10 bar below 1.5 K"

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the dilute phase
        [Pa]

    <pressure>
        -- float --
        The pressure of the dilute phase
        [Pa]

    ========== OUTPUT ==========

    <fraction_3he_dilute>
        -- float --
        The fraction of helium 3 inside the dilute phase
        []

    ========== STATUS ==========

    Status : Checked

    """

    ################## MODULES ################################################

    import numpy as np
    from cryopy.helium import helium7

    ################## CONDITIONS #############################################

    assert 0 <= temperature <= helium7.tricritical_temperature(pressure) , 'The function helium7.fraction_3he_dilute is not defined for T = ' + str(temperature) + ' K'

    assert 0 <= pressure <= 10e5 , 'The function  helium7.fraction_3he_dilute is not defined for P = ' + str(pressure) + ' Pa'

    ################## INITIALISATION #########################################

    # Convert from [Pa] to [Bar]
    pressure = pressure * 1e-5

    A0 = np.poly1d([0.0102283,-0.1269791,-0.209148])
    A1 = np.poly1d([0.0169801,-0.2165742,0.960222])
    A2 = np.poly1d([0.0092997,-0.1198491,0.549920])
    B = np.poly1d([-0.0020886,0.02291499,0.080280])
    
    ################## FUNCTION ###############################################
    
    return helium7.tricritical_fraction_3he(pressure) + A0(pressure) * (temperature - helium7.tricritical_temperature(pressure)) / ((temperature - helium7.tricritical_temperature(pressure)) - B(pressure)) + A1(pressure) * (temperature - helium7.tricritical_temperature(pressure)) + A2(pressure) * (temperature - helium7.tricritical_temperature(pressure)) ** 2

#%%
def fraction_3he_concentrated(temperature, pressure):
    """
    ========== DESCRIPTION ==========

    This function return the fraction of helium 3 inside the concentrate phase

    ========== VALIDITY ==========

    <temperature> : [0 -> helium7.tricritical_temperature(pressure)]
    <pressure> : [0 -> 10e5]

    ========== FROM ==========

    Chaudhry et al. (2010) 
        "Thermodynamic Properties of Liquid 3He-4He Mixtures Between 0–10 bar below 1.5 K"

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the concentrated phase
        [Pa]

    <pressure>
        -- float --
        The pressure of the concentrated phase
        [Pa]

    ========== OUTPUT ==========

    <fraction_3he_concentrate>
        -- float --
        The fraction of helium 3 inside the concentrated phase
        []

    ========== STATUS ==========

    Status : 

    """

    ################## MODULES ################################################

    import numpy as np
    from cryopy.helium import helium7

    ################## CONDITIONS #############################################

    assert 0 <= temperature <= helium7.tricritical_temperature(pressure) , 'The function helium7.fraction_3he_concentrate is not defined for T = ' + str(temperature) + ' K'

    assert 0 <= pressure <= 10e5 , 'The function helium7.fraction_3he_concentrated is not defined for P = ' + str(pressure) + ' Pa'

    ################## INITIALISATION #########################################

    # Convert [Pa] to [Bar]
    pressure = pressure * 1e-5
    
    C1 = np.poly1d([-0.0028598,0.0173549,-0.746805])
    C2 = np.poly1d([-0.0152076,0.1120251,-0.180743])
    C3 = np.poly1d([-0.0201411,0.1723264,0.316170])

    ################## FUNCTION ###############################################

    return helium7.tricritical_fraction_3he(pressure) + C1(pressure) * (temperature - helium7.tricritical_temperature(pressure)) + C2(pressure) * (temperature - helium7.tricritical_temperature(pressure)) ** 2 + C3(pressure) * (temperature - helium7.tricritical_temperature(pressure)) ** 3

#%%
def phase_diagram(pressure):
    """
    ========== DESCRIPTION ==========

    This function return the plot of the helium 3 / helium 4 phase diagram

    ========== VALIDITY ==========

    <pressure> : []

    ========== FROM ==========

    ========== INPUT ==========

    <pressure>
        -- float --
        The pressure 
        [Pa]

    ========== OUTPUT ==========

    <phase_diagram>
        -- plot --
        The helium 3 / helium 4 phase diagram
        []

    ========== STATUS ==========

    Status : 

    """

    ################## MODULES ################################################

    import numpy as np
    import matplotlib.pyplot as plt

    ################## CONDITIONS #############################################

    ################## INITIALISATION #########################################



    return 3


#%% Sandbox

import numpy as np
temperature = np.arange(0.1,0.4,0.001)

pressure = np.arange(0,10e5,1e4)
maximum = []
fraction_max = []
temperature_max = []

for p in pressure:
    x_concentrated = [fraction_3he_concentrated(t,p) for t in temperature]
    fraction_max.append(max(x_concentrated))
    maximum.append(np.argmax(x_concentrated))
    temperature_max.append(temperature[np.argmax(x_concentrated)])
    
    
import matplotlib.pyplot as plt

#coef = np.polyfit(pressure, temperature_max, 7)
coef = np.array([-1.17922125e-42,  2.07942046e-36,  9.87808000e-32, -3.05139959e-24, 3.23482929e-18, -1.84439626e-12,  6.73562647e-07,  1.50379312e-01])
f = np.poly1d(coef)

test_fit = [f(p) for p in pressure]


plt.figure()
plt.plot(pressure,temperature_max)
plt.plot(pressure,test_fit)
plt.legend(['data','fit'])

#%% Sandbox 2

pressure = 1e5
# Tricritical point
fraction_3He_tricritical = tricritical_fraction_3he(pressure)
temperature_tricritical = tricritical_temperature(pressure)

# Superfluid transition
fraction_3He_superfluid_transition_array = np.arange(0,fraction_3He_tricritical,0.001)
temperature_superfluid_transition_array = [transition_temperature(pressure, x) for x in fraction_3He_superfluid_transition_array]

# Concentrated phase
temperature_concentrated_array = np.arange(0.2,temperature_tricritical,0.001)
fraction_3he_concentrated_array = [fraction_3he_concentrated(t, pressure) for t in temperature_concentrated_array]

# Dilute phase
temperature_dilute_array = np.arange(0,temperature_tricritical,0.001)
fraction_3he_dilute_array = [fraction_3he_dilute(t, pressure) for t in temperature_dilute_array]

################## FUNCTION ###############################################

plt.figure()
plt.plot(fraction_3He_superfluid_transition_array,temperature_superfluid_transition_array,color='black')
plt.plot(fraction_3he_concentrated_array,temperature_concentrated_array,color='black')
plt.plot(fraction_3he_dilute_array,temperature_dilute_array,color='black')


#%% Sandbox 3

pressure = np.arange(0,18e5,1e4)
x = [tricritical_fraction_3he(p) for p in pressure]
t = [tricritical_temperature(p) for p in pressure]

plt.figure()
plt.plot(x,t)
plt.grid()
