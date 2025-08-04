#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRC16校验工具模块
提供CCITT CRC16算法实现，用于MIYA新风系统485协议

"""

from typing import Union


class CRC16Utils:
    """CRC16校验工具类"""
    
    @staticmethod
    def crc16_ccitt(data: Union[bytes, bytearray]) -> int:
        """
        计算CCITT CRC16校验（与MIYA设备实际算法一致）
        
        Args:
            data: 需要校验的数据
            
        Returns:
            CRC16校验值（16位整数）
        """
        crc = 0
        for byte in data:
            current = byte << 8
            for _ in range(8):
                if (crc ^ current) & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                current <<= 1
                # 确保CRC保持在16位范围内
                crc &= 0xFFFF
        return crc
    
    @staticmethod
    def crc16_ccitt_bytes(data: Union[bytes, bytearray]) -> bytes:
        """
        计算CCITT CRC16校验并返回字节格式（高位在前，低位在后）
        
        Args:
            data: 需要校验的数据
            
        Returns:
            CRC16校验值的字节表示（2字节，高位在前）
        """
        crc = CRC16Utils.crc16_ccitt(data)
        return bytes([(crc >> 8) & 0xFF, crc & 0xFF])
    
    @staticmethod
    def verify_crc16(data: Union[bytes, bytearray], expected_crc: int) -> bool:
        """
        验证CRC16校验值是否正确
        
        Args:
            data: 原始数据
            expected_crc: 期望的CRC16值
            
        Returns:
            校验是否通过
        """
        calculated_crc = CRC16Utils.crc16_ccitt(data)
        return calculated_crc == expected_crc
    
    @staticmethod
    def verify_crc16_bytes(data: Union[bytes, bytearray], crc_bytes: Union[bytes, bytearray]) -> bool:
        """
        验证CRC16校验字节是否正确
        
        Args:
            data: 原始数据
            crc_bytes: CRC16校验字节（2字节，高位在前）
            
        Returns:
            校验是否通过
        """
        if len(crc_bytes) != 2:
            raise ValueError("CRC字节长度必须为2字节")
        
        expected_crc = (crc_bytes[0] << 8) | crc_bytes[1]
        return CRC16Utils.verify_crc16(data, expected_crc)

def crc16_ccitt(data: Union[bytes, bytearray]) -> int:
    """
    便捷函数：计算CCITT CRC16校验
    
    Args:
        data: 需要校验的数据
        
    Returns:
        CRC16校验值
    """
    return CRC16Utils.crc16_ccitt(data)

def crc16_ccitt_bytes(data: Union[bytes, bytearray]) -> bytes:
    """
    便捷函数：计算CCITT CRC16校验并返回字节格式
    
    Args:
        data: 需要校验的数据
        
    Returns:
        CRC16校验值的字节表示
    """
    return CRC16Utils.crc16_ccitt_bytes(data)

def verify_crc16(data: Union[bytes, bytearray], expected_crc: int) -> bool:
    """
    便捷函数：验证CRC16校验值
    
    Args:
        data: 原始数据
        expected_crc: 期望的CRC16值
        
    Returns:
        校验是否通过
    """
    return CRC16Utils.verify_crc16(data, expected_crc)

def verify_crc16_bytes(data: Union[bytes, bytearray], crc_bytes: Union[bytes, bytearray]) -> bool:
    """
    便捷函数：验证CRC16校验字节
    
    Args:
        data: 原始数据
        crc_bytes: CRC16校验字节
        
    Returns:
        校验是否通过
    """
    return CRC16Utils.verify_crc16_bytes(data, crc_bytes)

# 测试函数
def test_crc16():
    """测试CRC16功能"""
    print("=== CRC16校验工具测试 ===\n")
    
    # 测试数据
    test_data = bytes([0xC7, 0x12, 0x01, 0x01, 0x01, 0x01, 0x04, 0x04, 
                       0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00])
    
    print(f"测试数据: {' '.join(f'{b:02X}' for b in test_data)}")
    
    # 计算CRC
    crc_value = crc16_ccitt(test_data)
    crc_bytes = crc16_ccitt_bytes(test_data)
    
    print(f"CRC16值: 0x{crc_value:04X}")
    print(f"CRC16字节: {' '.join(f'{b:02X}' for b in crc_bytes)}")
    
    # 验证CRC
    is_valid = verify_crc16(test_data, crc_value)
    is_valid_bytes = verify_crc16_bytes(test_data, crc_bytes)
    
    print(f"CRC验证结果: {is_valid}")
    print(f"CRC字节验证结果: {is_valid_bytes}")
    
    # 测试错误CRC
    wrong_crc = 0x1234
    is_wrong_valid = verify_crc16(test_data, wrong_crc)
    print(f"错误CRC验证结果: {is_wrong_valid}")


if __name__ == "__main__":
    test_crc16() 