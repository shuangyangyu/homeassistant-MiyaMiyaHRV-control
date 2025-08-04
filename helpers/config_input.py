#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 固定指令集
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
        "sleep_mode_off": "C7 12 00 02 00 00 00 00 00 01 00 00 00 00 00 00 00 00",
    
        # fan_mode_level_1  
        "fan_mode_level_1": "C7 12 00 02 00 00 02 02 00 00 00 00 00 00 00 00 00 00",

        # fan_mode_level_2
        "fan_mode_level_2": "C7 12 00 02 00 00 03 03 00 00 00 00 00 00 00 00 00 00",

        # fan_mode_level_3
        "fan_mode_level_3": "C7 12 00 02 00 00 04 04 00 00 00 00 00 00 00 00 00 00",
        
        # Device status query command
        "设备状态查询": "C7 12 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
    
    },

    "command_broadcast": {
        "broadcast": "AD 07 AA XX XX XX XX"
    },

    # Device status query command
    "command_broadcast_status": {
        "command_broadcast_status": "C7 12 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 7D 6C"
    },
}

# 自定义状态值含义
status_meanings_dict = {
            # header
            'header': {
                0xC7: 'Standard Header'
            },
            
            # data_length
            'data_length': {
                0x12: '18 bytes data'
            },
            
            # function_type
            'function_type': {
                0x01: 'Device Status Query',
                0x02: 'Device Status Set(Control)'
            },
            
            # power_status
            'power_status': {
                0x01: 'off',
                0x02: 'on'
            },
            
            # fan_speed
            'fan_speed': {
                0x01: 'Level_0',
                0x02: 'Level_1',
                0x03: 'Level_2',
                0x04: 'Level_3',
                0x05: 'Level_4'
            },
            
            # sleep_mode
            'sleep_mode': {
                0x01: 'off',
                0x02: 'on'
            }, 
            
            # negative_ion
            'negative_ion': {
                0x01: 'off',
                0x02: 'on'
            },
            
            # auxiliary_heat
            'auxiliary_heat': {
                0x01: 'off',
                0x02: 'on'
            },
            
            # auto_manual
            'auto_manual': {
                0x01: 'auto',
                0x02: 'manual'
            },
            
            # UV Sterilization
            'UV_sterilization': {
                0x01: 'off',
                0x02: 'on'
            },
            
            # inner_cycle
            'inner_cycle': {
                0x01: 'off',
                0x02: 'on'
            },
            
            # bypass
            'bypass': {
                0x01: 'off',
                0x02: 'on'
            },
            
            # timer
            'timer': {
                0x01: 'off',
                0x02: 'on'
            }
        }