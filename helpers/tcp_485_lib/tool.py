#!/usr/bin/env python3
"""数据转换工具类 - 公用方法"""

import logging
from typing import Union

_LOGGER = logging.getLogger(__name__)


class DataConverter:
    """数据转换工具类 - 提供十六进制与字节数据之间的转换功能"""
    
    @staticmethod
    def tcp_to_hex(data: bytes, uppercase: bool = True, separator: str = " ") -> str:
        """将TCP接收的字节数据转换为十六进制字符串
        
        Args:
            data: 字节数据
            uppercase: 是否转换为大写 (默认True)
            separator: 分隔符 (默认空格)
            
        Returns:
            十六进制字符串
            
        Raises:
            TypeError: 输入数据不是bytes类型
        """
        if not isinstance(data, bytes):
            raise TypeError("输入数据必须是bytes类型")
        
        hex_str = data.hex()
        if uppercase:
            hex_str = hex_str.upper()
        
        if separator:
            hex_pairs = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
            return separator.join(hex_pairs)
        
        return hex_str
    
    @staticmethod
    def hex_to_tcp(hex_string: str) -> bytes:
        """将十六进制字符串转换为TCP发送的字节数据
        
        Args:
            hex_string: 十六进制字符串，支持多种格式:
                - "C7 12 01 00" (空格分隔，推荐)
                - "C7120100" (无分隔符)
                - "c7 12 01 00" (小写字母)
                
        Returns:
            字节数据
            
        Raises:
            TypeError: 输入不是字符串类型
            ValueError: 输入包含非十六进制字符或长度不为偶数
        """
        if not isinstance(hex_string, str):
            raise TypeError("输入必须是字符串类型")
        
        # 清理字符串，移除所有空白字符
        cleaned = ''.join(hex_string.split())
        
        # 验证十六进制字符
        if not all(c in '0123456789ABCDEFabcdef' for c in cleaned):
            raise ValueError("输入包含非十六进制字符")
        
        # 确保字符数为偶数
        if len(cleaned) % 2 != 0:
            raise ValueError("十六进制字符串长度必须为偶数")
        
        try:
            return bytes.fromhex(cleaned)
        except ValueError as e:
            raise ValueError(f"十六进制字符串转换失败: {e}")
    
    @staticmethod
    def format_tcp_data(data: bytes, prefix: str = "TCP Data") -> str:
        """格式化显示TCP数据
        
        Args:
            data: 字节数据
            prefix: 显示前缀 (默认"TCP Data")
            
        Returns:
            格式化的字符串，包含数据长度和十六进制表示
        """
        hex_str = DataConverter.tcp_to_hex(data)
        return f"{prefix}: [{len(data)} bytes] {hex_str}"
    
    @staticmethod
    def validate_hex_string(hex_string: str) -> bool:
        """验证十六进制字符串格式是否正确
        
        Args:
            hex_string: 要验证的十六进制字符串
            
        Returns:
            True表示格式正确，False表示格式错误
        """
        try:
            DataConverter.hex_to_tcp(hex_string)
            return True
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def normalize_hex_string(hex_string: str, separator: str = " ") -> str:
        """标准化十六进制字符串格式
        
        Args:
            hex_string: 原始十六进制字符串
            separator: 分隔符 (默认空格)
            
        Returns:
            标准化后的十六进制字符串
            
        Raises:
            ValueError: 输入格式无效
        """
        # 先转换为字节，再转换回标准格式
        bytes_data = DataConverter.hex_to_tcp(hex_string)
        return DataConverter.tcp_to_hex(bytes_data, uppercase=True, separator=separator)
    
    @staticmethod
    def hex_to_int(hex_string: str) -> int:
        """将十六进制字符串转换为整数
        
        Args:
            hex_string: 十六进制字符串
            
        Returns:
            对应的整数值
        """
        bytes_data = DataConverter.hex_to_tcp(hex_string)
        return int.from_bytes(bytes_data, byteorder='big')
    
    @staticmethod
    def int_to_hex(value: int, byte_length: int = 4, separator: str = " ") -> str:
        """将整数转换为十六进制字符串
        
        Args:
            value: 整数值
            byte_length: 字节长度 (默认4字节)
            separator: 分隔符 (默认空格)
            
        Returns:
            十六进制字符串
        """
        bytes_data = value.to_bytes(byte_length, byteorder='big')
        return DataConverter.tcp_to_hex(bytes_data, separator=separator)
    
    @staticmethod
    def hex_to_ascii(hex_string: str) -> str:
        """将十六进制字符串转换为ASCII字符串
        
        Args:
            hex_string: 十六进制字符串
            
        Returns:
            ASCII字符串
        """
        bytes_data = DataConverter.hex_to_tcp(hex_string)
        return bytes_data.decode('ascii', errors='ignore')
    
    @staticmethod
    def ascii_to_hex(ascii_string: str, separator: str = " ") -> str:
        """将ASCII字符串转换为十六进制字符串
        
        Args:
            ascii_string: ASCII字符串
            separator: 分隔符 (默认空格)
            
        Returns:
            十六进制字符串
        """
        bytes_data = ascii_string.encode('ascii')
        return DataConverter.tcp_to_hex(bytes_data, separator=separator)


# 便捷函数
def hex_to_bytes(hex_string: str) -> bytes:
    """便捷函数：十六进制字符串转字节
    
    Args:
        hex_string: 十六进制字符串
        
    Returns:
        字节数据
    """
    return DataConverter.hex_to_tcp(hex_string)


def bytes_to_hex(data: bytes, separator: str = " ") -> str:
    """便捷函数：字节转十六进制字符串
    
    Args:
        data: 字节数据
        separator: 分隔符 (默认空格)
        
    Returns:
        十六进制字符串
    """
    return DataConverter.tcp_to_hex(data, separator=separator)


def format_data(data: Union[str, bytes], prefix: str = "Data") -> str:
    """便捷函数：格式化数据显示
    
    Args:
        data: 数据（字符串或字节）
        prefix: 显示前缀
        
    Returns:
        格式化的字符串
    """
    if isinstance(data, str):
        # 如果是十六进制字符串，先转换为字节
        try:
            bytes_data = DataConverter.hex_to_tcp(data)
            return DataConverter.format_tcp_data(bytes_data, prefix)
        except ValueError:
            # 如果不是有效的十六进制，按ASCII处理
            return f"{prefix}: [{len(data)} chars] {data}"
    else:
        return DataConverter.format_tcp_data(data, prefix)


# 导出主要类
__all__ = [
    'DataConverter',
    'hex_to_bytes',
    'bytes_to_hex', 
    'format_data'
] 