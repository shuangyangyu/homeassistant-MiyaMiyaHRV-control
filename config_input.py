#!/usr/bin/env python3
# -*- coding: utf-8 -*-

command_set_dict = {
    "command_fixed": {
        # Power On/Off 
        "power_off": "C7 12 01 02 01 01 04 04 01 00 01 01 01 01 01 01 00 00",
        "power_auto": "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 00 00",
        
        # inner_cycle
        "inner_cycle_on": "C7 12 00 02 00 00 00 00 00 00 00 00 02 00 00 00 00 00",
        "inner_cycle_off": "C7 12 00 02 00 00 00 00 00 00 00 00 01 00 00 00 00 00",
        
        # auxiliary_heat
        "auxiliary_heat_on": "C7 12 00 02 00 00 00 00 00 00 00 00 00 02 00 00 00 00",
        "auxiliary_heat_off": "C7 12 00 02 00 00 00 00 00 00 00 00 00 01 00 00 00 00",
        
        # uv_sterilization
        "uv_sterilization_on": "C7 12 00 02 00 00 00 00 00 00 00 02 00 00 00 00 00 00",
        "uv_sterilization_off": "C7 12 00 02 00 00 00 00 00 00 00 01 00 00 00 00 00 00",
        
        # bypass
        "bypass_on": "C7 12 00 02 00 00 00 00 00 00 00 00 00 00 02 00 00 00",
        "bypass_off": "C7 12 00 02 00 00 00 00 00 00 00 00 00 00 01 00 00 00",
        
        # negative_ion
        "negative_ion_on": "C7 12 00 02 00 00 00 00 02 00 00 00 00 00 00 00 00 00",
        "negative_ion_off": "C7 12 00 02 00 00 00 00 01 00 00 00 00 00 00 00 00 00",
        
        # sleep_mode
        "sleep_mode_on": "C7 12 00 02 00 00 00 00 00 02 00 00 00 00 00 00 00 00",
        "sleep_mode_off": "C7 12 00 02 00 00 00 00 00 01 00 00 00 00 00 00 00 00"
    },

    "command_broadcast": {
        "broadcast": "AD 07 AA XX XX XX XX"
    },
}
