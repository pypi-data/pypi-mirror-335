#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%
def thermal_expansion(temperature):
    """
    ========== DESCRIPTION ==========

    This function return the thermal expansion coefficient of STYCAST 2850 FT cat 9

    ========== VALIDITY ==========

    <temperature> : [4.2 -> 335]

    ========== FROM ==========

    Internal report - contact valentin.sauvage@outlook.com 

    ========== INPUT ==========

    <temperature>
        -- float --
        The temperature of the material
        [K]

    ========== OUTPUT ==========

    <thermal_expansion>
        -- float --
        The thermal expansion coefficient of stycast 2850FT cat 9
        [Ø]

    ========== STATUS ==========

    Status : Checked

    """

    ################## CONDITIONS #############################################

    assert temperature <= 335 and temperature >= 4.2, 'The function ' \
                                                      ' STYCAST2850FT9.thermal_expansion is not defined for ' \
                                                      'T = ' + str(temperature) + ' K'

    ################## FUNCTION ###############################################

    expansion = 4.694544e-7 * temperature ** 4 - 3.352487e-4 * temperature ** 3 + 1.211048e-1 * temperature ** 2 - 2.852325 * temperature - 4.609941e3

    return expansion * 1e-6
