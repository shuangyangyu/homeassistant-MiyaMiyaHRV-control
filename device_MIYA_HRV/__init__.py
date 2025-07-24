#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIYA HRV设备模块
包含CRC16校验工具和其他设备相关功能

"""

from .crc16_utils import (
    CRC16Utils,
    crc16_ccitt,
    crc16_ccitt_bytes,
    verify_crc16,
    verify_crc16_bytes
)

__all__ = [
    'CRC16Utils',
    'crc16_ccitt',
    'crc16_ccitt_bytes',
    'verify_crc16',
    'verify_crc16_bytes'
]

__version__ = '1.0.0' 