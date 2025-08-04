"""
MIYA HRV 设备助手模块
====================

这个包包含了MIYA HRV新风系统设备的所有助手模块：

主要模块:
- protocal.py: 协议层 - 命令计算和状态解析
- communicator.py: 通讯层 - TCP通信接口
- config_input.py: 配置输入 - 命令和状态定义
- crc_miya.py: CRC校验 - CCITT CRC16算法
- tcp_485_lib/: TCP通信库 - 异步TCP客户端

使用示例:
    >>> from helpers.protocal import cmd_calculate, MiyaCommandAnalyzer
    >>> from helpers.communicator import TCP_485_Device
    >>> from helpers.config_input import command_set_dict, status_meanings_dict
    >>> from helpers.crc_miya import crc16_ccitt
    >>> from helpers.tcp_485_lib import create_client

命令计算:
    >>> result = cmd_calculate(command_set_dict, "01")
    >>> print(result['command_fixed'])

状态解析:
    >>> analyzer = MiyaCommandAnalyzer()
    >>> status = analyzer.get_status_data("C7 12 01 01 01 02 03 03 01 01 01 01 01 01 01 01 00 00 AD DD")

设备通信:
    >>> device = TCP_485_Device("192.168.1.5", 38)
    >>> await device.connect()
    >>> await device.send_command("C7 12 01 01 01 02 03 03 01 01 01 01 01 01 01 01 00 00 AD DD")
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "MIIY HRV Project"
__description__ = "MIYA HRV新风系统设备助手模块"

# 导出的主要类和函数
__all__ = [
    # 协议层
    "cmd_calculate",
    "MiyaCommandAnalyzer",
    
    # 通讯层
    "TCP_485_Device",
    
    # 配置
    "command_set_dict",
    "status_meanings_dict",
    
    # HA 工具函数
    "get_device_status",
    "get_device_instance",
    "get_commands",
    "send_device_command",
    "get_fan_mode",
    "get_operation_mode",
    "get_negative_ion_status",
    "get_uv_sterilization_status",
    "get_sleep_mode_status",
    "get_inner_cycle_status",
    "get_auxiliary_heat_status",
    "get_bypass_status",
    "generate_entity_id",
    "generate_device_id",
    
    # 管理器
    "MiyaHRVManager",
    
    # 版本信息
    "__version__",
    "__author__",
    "__description__"
]

# 导入主要功能，方便直接使用
try:
    from .protocal import cmd_calculate, MiyaCommandAnalyzer
    from .communicator import TCP_485_Device
    from .config_input import command_set_dict, status_meanings_dict
    from .ha_utils import (
        get_device_status, get_device_instance, get_commands, send_device_command,
        get_fan_mode, get_operation_mode, get_negative_ion_status,
        get_uv_sterilization_status, get_sleep_mode_status, get_inner_cycle_status,
        get_auxiliary_heat_status, get_bypass_status, generate_entity_id, generate_device_id, MiyaHRVManager
    )
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from protocal import cmd_calculate, MiyaCommandAnalyzer
    from communicator import TCP_485_Device
    from config_input import command_set_dict, status_meanings_dict
    from ha_utils import (
        get_device_status, get_device_instance, get_commands, send_device_command,
        get_fan_mode, get_operation_mode, get_negative_ion_status,
        get_uv_sterilization_status, get_sleep_mode_status, get_inner_cycle_status,
        get_auxiliary_heat_status, get_bypass_status, generate_entity_id, generate_device_id, MiyaHRVManager
    )
