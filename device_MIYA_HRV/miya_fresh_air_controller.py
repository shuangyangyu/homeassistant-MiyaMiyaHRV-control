#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIYA新风系统485协议控制器
包含指令生成器和状态解析器

"""

import struct
from typing import Dict, List, Tuple, Optional
from enum import Enum

import sys
import os
from typing import Dict

# 添加父目录到路径，以便导入tcp_485_lib
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from tcp_485_lib.tool import DataConverter
except ImportError:
    # 如果无法导入，尝试相对导入
    sys.path.append(parent_dir)
    from tcp_485_lib.tool import DataConverter

# 修复crc16_utils导入问题
try:
    from .crc16_utils import crc16_ccitt
except ImportError:
    try:
        # 如果相对导入失败，尝试绝对导入
        from device_MIYA_HRV.crc16_utils import crc16_ccitt
    except ImportError:
        # 如果还是失败，尝试直接导入
        import crc16_utils
        crc16_ccitt = crc16_utils.crc16_ccitt


class MiyaFreshAirController:
    """MIYA新风系统485协议控制器"""
    
    # 协议常量
    PACKET_HEADER = 0xC7  # 实际设备使用C7
    DATA_LENGTH = 0x12
    
    # 功能类型
    CMD_QUERY = 0x01      # 设备状态查询
    CMD_CONTROL = 0x02    # 设备状态设置
    

    
    def __init__(self):
        """初始化控制器"""
        pass
    

    
    def generate_control_command(self, 
                               device_addr: int,
                               power: int = 0x00,           # 开关机：0x00不操作, 0x01关机, 0x02开机
                               fan_speed_in: int = 0x00,    # 进风风速：0x00不操作, 0x01-0x05风速档位
                               fan_speed_out: int = 0x00,   # 排风风速：0x00不操作, 0x01-0x05风速档位
                               negative_ion: int = 0x00,    # 负离子：0x00不操作, 0x01关, 0x02开
                               aux_heat: int = 0x00,        # 辅热：0x00不操作, 0x01关, 0x02开
                               auto_manual: int = 0x00,     # 手动/自动：0x00不操作, 0x01自动, 0x02手动
                               outdoor_sensor: int = 0x00,  # 室外温湿度：0x00不操作, 0x01关, 0x02开
                               inner_cycle: int = 0x00,     # 内循环：0x00不操作, 0x01内循环, 0x02普通模式
                               aux_group: int = 0x00,       # 辅组：0x00不操作, 0x01关, 0x02开
                               bypass: int = 0x00,          # 旁通：0x00不操作, 0x01关, 0x02开
                               timer: int = 0x00            # 定时：0x00不操作, 0x01关, 0x02开
                               ) -> bytes:
        """
        生成控制指令
        
        Args:
            device_addr: 设备地址
            power: 开关机状态
            fan_speed_in: 进风风速
            fan_speed_out: 排风风速
            negative_ion: 负离子开关
            aux_heat: 辅热开关
            auto_manual: 自动/手动模式
            outdoor_sensor: 室外温湿度传感器
            inner_cycle: 内循环模式
            aux_group: 辅组开关
            bypass: 旁通开关
            timer: 定时开关
            
        Returns:
            完整的控制指令字节序列
        """
        # 构建数据包（不包含CRC）
        packet = bytearray([
            self.PACKET_HEADER,    # byte 0: 包头
            self.DATA_LENGTH,      # byte 1: 数据长度
            device_addr,           # byte 2: 设备地址
            self.CMD_CONTROL,      # byte 3: 功能类型（控制）
            device_addr,           # byte 4: 设备地址（重复）
            power,                 # byte 5: 开关机
            fan_speed_in,          # byte 6: 进风风速
            fan_speed_out,         # byte 7: 排风风速
            negative_ion,          # byte 8: 负离子
            aux_heat,              # byte 9: 辅热
            auto_manual,           # byte 10: 手动/自动
            outdoor_sensor,        # byte 11: 室外温湿度
            inner_cycle,           # byte 12: 内循环
            aux_group,             # byte 13: 辅组
            bypass,                # byte 14: 旁通
            timer,                 # byte 15: 定时
            0x00,                  # byte 16: 保留
            0x00                   # byte 17: 保留
        ])
        
        # 计算CRC16校验（从byte 0开始，包含包头）
        crc_data = packet[0:18]  # 包头+数据长度+16字节数据
        crc = crc16_ccitt(crc_data)
        
        # 添加CRC16（高位在前，低位在后）
        packet.append((crc >> 8) & 0xFF)  # byte 18: CRC高位
        packet.append(crc & 0xFF)         # byte 19: CRC低位
        
        return bytes(packet)
    # 定义固定指令生成
    def generate_fixed_command(self, device_addr: int, command_type: int) -> bytes:
        """
        生成固定指令
        """
        # 构建数据包（不包含CRC）
        data_packet = "C7 12 00 02 00 00 00 00 00 00 01 00 00 00 00 00 00 00"
        new_packet = bytearray(self.parse_hex_string(data_packet))  # 转换为bytearray以便修改
        # 计算CRC16校验（从byte 0开始，包含包头）
        crc_data = new_packet[0:18]  # 包头+数据长度+16字节数据
        crc = crc16_ccitt(crc_data)
        # 添加CRC16（高位在前，低位在后）
        new_packet.append((crc >> 8) & 0xFF)  # byte 18: CRC高位
        new_packet.append(crc & 0xFF)         # byte 19: CRC低位
        return bytes(new_packet)
    
    
   
   
    def format_hex_string(self, data: bytes) -> str:
        """
        将字节数据格式化为可读的HEX字符串
        
        Args:
            data: 字节数据
            
        Returns:
            格式化的HEX字符串
        """
        return ' '.join(f'{b:02X}' for b in data)
    
    def parse_hex_string(self, hex_str: str) -> bytes:
        """
        将HEX字符串解析为字节数据
        
        Args:
            hex_str: HEX字符串，如 "C7 12 01 01..."
            
        Returns:
            字节数据
        """
        # 移除空格并转换为大写
        hex_clean = hex_str.replace(' ', '').replace('-', '').upper()
        
        # 确保是偶数长度
        if len(hex_clean) % 2 != 0:
            raise ValueError("HEX字符串长度必须是偶数")
        
        # 转换为字节
        return bytes.fromhex(hex_clean)

def format_hex_string(self, data: bytes) -> str:
    """
    将字节数据格式化为可读的HEX字符串
    
    Args:
        data: 字节数据
        
    Returns:
        格式化的HEX字符串
    """
    return ' '.join(f'{b:02X}' for b in data)

def parse_hex_string(self, hex_str: str) -> bytes:
# 定义一个生成固定指令的方法 出入两个参数 一个是物理地址 一个是字典代表指令 字典的key 是 指令的名称 值是 指令的值



def generate_fixed_command(self, device_addr: str, command_list: list) -> bytes:
    """
    生成固定指令
    """
    #物理地址默认是01
    if device_addr is None:
        device_addr = 0x01
    # 如果command_dict 是空 报错
    if command_list is None:
        raise ValueError("command_list 不能为空")
    # 如果command_list 是列表 则根据列表的key 和 值 生成指令  
    # 例如：("内循环on","C7 12 00 02 00 00 00 00 00 00 00 00 02 00 00 00 00 00", ...}
    # 根据command_list 生成指令
    for command in command_list:
        command_bytes = parse_hex_string(command)
        crc_data = command_bytes[0:18]  # 包头+数据长度+16字节数据
        crc = crc16_ccitt(crc_data)
        # 添加CRC16（高位在前，低位在后）
        command_bytes.append((crc >> 8) & 0xFF)  # byte 18: CRC高位
        command_bytes.append(crc & 0xFF)         # byte 19: CRC低位
        command_bytes = bytes(command_bytes)
        command_hex = format_hex_string(command_bytes)
        print(f"指令: {command_hex}")
        
        
    return command_hex
        
        
        
 


   
        
    
    
    
    





def main():
    """示例使用方法"""
    controller = MiyaFreshAirController()
    fixed_cmd = controller.generate_fixed_command(1, 0x01)
    print(f"固定指令: {controller.format_hex_string(fixed_cmd)}")

    
    # # 1. 生成控制指令示例
    # print("1. 生成控制指令:")
    # cmd = controller.generate_control_command(
    #     device_addr=1,
    #     power=0x01,        
    #     fan_speed_in=0x04, 
    #     fan_speed_out=0x04,
    #     negative_ion=0x01, 
    #     auto_manual=0x01,   
    #     outdoor_sensor=0x01, 
    #     inner_cycle=0x01, 
    #     aux_group=0x01,
    #     bypass=0x01, 
    #     timer=0x01 
        
    # )
    # print(f"开机指令: {controller.format_hex_string(cmd)}")
    
  
    

    
    



if __name__ == "__main__":
    main() 