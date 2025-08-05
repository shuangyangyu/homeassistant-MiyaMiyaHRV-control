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
- ha_utils.py: Home Assistant工具函数

使用示例:
    >>> from helpers.protocal import cmd_calculate, MiyaCommandAnalyzer
    >>> from helpers.communicator import TCP_485_Device
    >>> from helpers.config_input import command_set_dict, status_meanings_dict
    >>> from helpers.ha_utils import MiyaHRVManager
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "MIIY HRV Project"
__description__ = "MIYA HRV新风系统设备助手模块"
