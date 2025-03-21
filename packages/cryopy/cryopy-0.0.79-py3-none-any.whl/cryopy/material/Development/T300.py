#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# %%
def thermal_conductivity(temperature):
    """
    ========== DESCRIPTION ==========

    This function return the thermal conductivity of CFRP T300

    ========== VALIDITY ==========

    <temperature> : [4.6 -> 296]

    ========== FROM ==========

    Internal report - contact valentin.sauvage@outlook.com 

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <thermal_conductivity>
        -- float --
        The thermal conductivity of T300
        [W].[m]**(-1).[K]**(-1)

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 298 and temperature >= 4.4, 'The function ' \
                                                      ' T300.thermal_conductivity is not defined for ' \
                                                      'T = ' + str(temperature) + ' K'

    ################## MODULES ################################################

    import numpy as np

    ################## INITIALISATION #########################################

    Coefficients = np.array([-5.08526105, 2.73116624, -0.95055867, 0.17541869, -0.00896476])

    ################## FUNCTION ###############################################

    result = 0

    for i in range(len(Coefficients)):
        result = result + Coefficients[i] * np.log(temperature) ** i

    return np.exp(result)
