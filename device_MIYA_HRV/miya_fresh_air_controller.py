#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIYA新风系统485协议控制器
包含指令生成器和状态解析器

"""

import struct
from typing import Dict, List, Tuple, Optional
from enum import Enum
from device_MIYA_HRV.crc16_utils import crc16_ccitt


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
    
    def generate_query_command(self, device_addr: int) -> bytes:
        """
        生成状态查询指令
        
        Args:
            device_addr: 设备地址
            
        Returns:
            查询指令字节序列
        """
        return self.generate_control_command(
            device_addr=device_addr,
            # 所有控制参数都设为0x00（不操作），实现纯查询
        )
    
    def parse_status_response(self, data: bytes) -> Dict:
        """
        解析状态返回数据
        
        Args:
            data: 接收到的状态数据
            
        Returns:
            解析后的状态字典
        """
        if len(data) != 20:
            raise ValueError(f"数据长度错误，期望20字节，实际{len(data)}字节")
        
        # 验证包头和数据长度
        header = data[0]
        data_len = data[1]
        
        if data_len != self.DATA_LENGTH:
            print(f"警告：数据长度字段异常，期望0x{self.DATA_LENGTH:02X}，实际0x{data_len:02X}")
        
        # 验证CRC16
        crc_received = (data[18] << 8) | data[19]
        crc_calculated = crc16_ccitt(data[0:18])  # 从包头开始计算
        
        crc_valid = crc_received == crc_calculated
        if not crc_valid:
            print(f"警告：CRC16校验失败，接收0x{crc_received:04X}，计算0x{crc_calculated:04X}")
        
        # 解析状态字段
        status = {
            'packet_info': {
                'header': f"0x{header:02X}",
                'data_length': f"0x{data_len:02X}",
                'crc_valid': crc_valid,
                'crc_received': f"0x{crc_received:04X}",
                'crc_calculated': f"0x{crc_calculated:04X}"
            },
            'device_addr': data[2],
            'cmd_type': '状态查询' if data[3] == self.CMD_QUERY else '状态设置',
            'device_addr_repeat': data[4],
            'power': {
                'value': data[5],
                'status': '关机' if data[5] == 0x01 else '开机' if data[5] == 0x02 else '未知'
            },
            'fan_speed_in': {
                'value': data[6],
                'status': f"风速{data[6]}档" if 1 <= data[6] <= 5 else f"未知档位(0x{data[6]:02X})"
            },
            'fan_speed_out': {
                'value': data[7],
                'status': f"风速{data[7]}档" if 1 <= data[7] <= 5 else f"未知档位(0x{data[7]:02X})"
            },
            'negative_ion': {
                'value': data[8],
                'status': '关' if data[8] == 0x01 else '开' if data[8] == 0x02 else '未知'
            },
            'aux_heat': {
                'value': data[9],
                'status': '关' if data[9] == 0x01 else '开' if data[9] == 0x02 else '未知'
            },
            'auto_manual': {
                'value': data[10],
                'status': '自动' if data[10] == 0x01 else '手动' if data[10] == 0x02 else '未知'
            },
            'outdoor_sensor': {
                'value': data[11],
                'status': '关闭' if data[11] == 0x01 else '开启' if data[11] == 0x02 else '未知'
            },
            'inner_cycle': {
                'value': data[12],
                'status': '普通模式' if data[12] == 0x01 else '内循环' if data[12] == 0x02 else '未知'
            },
            'aux_group': {
                'value': data[13],
                'status': '关' if data[13] == 0x01 else '开' if data[13] == 0x02 else '未知'
            },
            'bypass': {
                'value': data[14],
                'status': '关' if data[14] == 0x01 else '开' if data[14] == 0x02 else '未知'
            },
            'timer': {
                'value': data[15],
                'status': '关' if data[15] == 0x01 else '开' if data[15] == 0x02 else '未知'
            }
        }
        
        return status
    
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



def main():
    """示例使用方法"""
    controller = MiyaFreshAirController()
    
    print("=== MIYA新风系统485协议控制器示例 ===\n")
    
    # 1. 生成控制指令示例
    print("1. 生成控制指令:")
    cmd = controller.generate_control_command(
        device_addr=1,
        power=0x01,        
        fan_speed_in=0x04, 
        fan_speed_out=0x04,
        negative_ion=0x01, 
        auto_manual=0x01,   
        outdoor_sensor=0x01, 
        inner_cycle=0x01, 
        aux_group=0x01,
        bypass=0x01, 
        timer=0x01 
        
    )
    print(f"开机指令: {controller.format_hex_string(cmd)}")
    
    # # 2. 生成查询指令示例
    # print("\n2. 生成查询指令:")
    # query_cmd = controller.generate_query_command(device_addr=1)
    # print(f"查询指令: {controller.format_hex_string(query_cmd)}")
    
    # 3. 解析状态数据示例
    print("\n3. 解析状态数据:")
    # 使用提供的实际数据
    hex_data = "C7 12 01 01 01 01 04 04 01 01 01 01 01 01 01 01 00 00 62 78"
    try:
        data = controller.parse_hex_string(hex_data)
        status = controller.parse_status_response(data)
        
        print(f"原始数据: {hex_data}")
        print(f"包头信息: {status['packet_info']}")
        print(f"设备地址: {status['device_addr']}")
        print(f"命令类型: {status['cmd_type']}")
        print(f"设备地址(重复): {status['device_addr_repeat']}")
        
        # 打印所有控制状态
        print("\n=== 设备状态详情 ===")
        print(f"电源状态: {status['power']['status']} (值: 0x{status['power']['value']:02X})")
        print(f"进风风速: {status['fan_speed_in']['status']} (值: 0x{status['fan_speed_in']['value']:02X})")
        print(f"排风风速: {status['fan_speed_out']['status']} (值: 0x{status['fan_speed_out']['value']:02X})")
        print(f"负离子: {status['negative_ion']['status']} (值: 0x{status['negative_ion']['value']:02X})")
        print(f"辅热: {status['aux_heat']['status']} (值: 0x{status['aux_heat']['value']:02X})")
        print(f"运行模式: {status['auto_manual']['status']} (值: 0x{status['auto_manual']['value']:02X})")
        print(f"室外温湿度: {status['outdoor_sensor']['status']} (值: 0x{status['outdoor_sensor']['value']:02X})")
        print(f"内循环: {status['inner_cycle']['status']} (值: 0x{status['inner_cycle']['value']:02X})")
        print(f"辅组: {status['aux_group']['status']} (值: 0x{status['aux_group']['value']:02X})")
        print(f"旁通: {status['bypass']['status']} (值: 0x{status['bypass']['value']:02X})")
        print(f"定时: {status['timer']['status']} (值: 0x{status['timer']['value']:02X})")
        
    except Exception as e:
        print(f"解析错误: {e}")
    



if __name__ == "__main__":
    main() 