#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIYA新风系统指令分析器
用于分析和解码现有的485协议指令
基于MIYA 485协议规范
"""

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

try:
    from .crc16_utils import crc16_ccitt
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from device_MIYA_HRV.crc16_utils import crc16_ccitt

class MiyaCommandAnalyzer:
    """MIYA新风系统指令分析器"""
    
    def __init__(self):
        
        # 根据MIYA 485协议规范定义状态值含义
        self.status_meanings = {
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
    
    def get_status_data(self, hex_string: str) -> Dict:
        """
        为hass提供状态数据
        """
        data = DataConverter.hex_to_tcp(hex_string)
        data_len = len(data)
        # 判断数据的类型
        command_type = self._determine_command_type(data)
        if command_type == "设备状态查询指令":
            
            info_table = self._generate_hass_status_table(data)
            fan_speed_status = self._fan_speed_status(data)
            if fan_speed_status:  # 检查是否为None
                info_table.update(fan_speed_status)
            mode_status = self._mode_status(data)
            if mode_status:  # 检查是否为None
                info_table.update(mode_status)
            return info_table
                  
        elif command_type == "设备地址响应":
            # 解析出设备地址
            pass

        else:
            return {'error': '未知指令类型'}
   
        return data
 
    def _determine_command_type(self, data: bytes) -> str:
        """确定指令类型"""
        if len(data) == 20:
            if data[0] == 0xC7:
                if data[3] == 0x01:
                    return "设备状态查询指令"
                elif data[3] == 0x02:
                    return "设备状态设置(控制)指令"
                else:
                    return "未知控制指令"
            else:
                return f"未知指令(包头: 0x{data[0]:02X})"
        elif len(data) == 7:
            if data[0] == 0xAA:
                return "设备地址响应"
            elif data[0] == 0xC7:
                if data[2] == 0xAA:
                    return "设备地址查询指令"
                else:
                    return "未知地址管理指令"
            else:
                return f"未知7字节指令(包头: 0x{data[0]:02X})"
        else:
            return f"未知长度指令({len(data)}字节)"
    
    def _generate_hass_status_table(self, data: bytes) -> Dict:
        """
        为hass生成状态表
        """
        return {
            # 'header': f"0x{data[0]:02X} ({self.status_meanings['header'].get(data[0], 'Unknown Header')})",
            # 'data_length': f"0x{data[1]:02X} ({self.status_meanings['data_length'].get(data[1], f'{data[1]} bytes')})",
            # 'device_address': f"0x{data[2]:02X} (Device {data[2]})",
            # 'function_type': f"0x{data[3]:02X} ({self.status_meanings['function_type'].get(data[3], 'Unknown Function')})",
            # 'device_address(repeat)': f"0x{data[4]:02X} (Device {data[4]})",
            # 'power_status': self.status_meanings['power_status'].get(data[5], 'Unknown Status'),
            # 'in_speed': self.status_meanings['fan_speed'].get(data[6], f'Speed {data[6]}'),
            # 'out_speed': self.status_meanings['fan_speed'].get(data[7], f'Speed {data[7]}'),
            'negative_ion': self.status_meanings['negative_ion'].get(data[8], 'Unknown Status'),
            'sleep_mode': self.status_meanings['sleep_mode'].get(data[9], 'Unknown Status'),
            # 'auto_manual': self.status_meanings['auto_manual'].get(data[10], 'Unknown Mode'),
            'UV_sterilization': self.status_meanings['UV_sterilization'].get(data[11], 'Unknown Status'),
            'inner_cycle': self.status_meanings['inner_cycle'].get(data[12], 'Unknown Mode'),
            'auxiliary_heat': self.status_meanings['auxiliary_heat'].get(data[13], 'Unknown Status'),
            'bypass': self.status_meanings['bypass'].get(data[14], 'Unknown Status'),
            # 'timer': f"0x{data[15]:02X} ({self.status_meanings['timer'].get(data[15], 'Unknown Status')})",
            # 'reserved_field1': f"0x{data[16]:02X}",
            # 'reserved_field2': f"0x{data[17]:02X}",
            # 'CRC16_high': f"0x{data[18]:02X}",
            # 'CRC16_low': f"0x{data[19]:02X}"
        }
    
    def _analyze_address_command(self, data: bytes) -> Dict:
        """分析地址管理指令"""
        if data[0] == 0xAA and len(data) == 7:
            return {
                '响应类型': '设备地址响应',
                '设备地址': data[3],
                '十六进制地址': f"0x{data[3]:02X}"
            }
        elif data[0] == 0xC7 and len(data) == 7:
            if data[2] == 0xAA:
                return {
                    '指令类型': '设备地址查询',
                    '查询参数': data[3]
                }
        return {'类型': '未知地址指令'}
    
    def _fan_speed_status(self, data: bytes) -> Dict:
        """判断进风和排风的风速"""
        if data[6] == 0x01 and data[7] == 0x01:
            return {'fan_mode': 'level_1'}
        elif data[6] == 0x02 and data[7] == 0x02:
            return {'fan_mode': 'level_2'}
        elif data[6] == 0x03 and data[7] == 0x03:
            return {'fan_mode': 'level_3'}
        elif data[6] == 0x04 and data[7] == 0x04:
            return {'fan_mode': 'level_4'}
        elif data[6] == 0x05 and data[7] == 0x05:
            return {'fan_mode': 'level_5'}
        else:
            # 如果进风和排风速度不匹配，返回默认值
            return {'fan_mode': 'unknown'}

    def _mode_status(self, data: bytes) -> Dict:
        """判断模式状态"""
        if data[5] == 0x02 and data[10] == 0x01:
            return {'mode': 'auto'}
        elif data[5] == 0x01:
            return {'mode': 'off'}
        elif data[5] == 0x02 and data[10] == 0x02:
            return {'mode': 'manual'}

    
    def _check_crc(self, data: bytes) -> Dict:
        """检查CRC校验"""
        if len(data) < 20:
            return {'status': 'N/A', 'reason': '数据长度不足'}
        
        try:
            # 提取CRC
            received_crc = (data[18] << 8) | data[19]
            
            # 计算CRC
            calculated_crc = crc16_ccitt(data[0:18])
            
            is_valid = received_crc == calculated_crc
            
            return {
                'status': 'PASS' if is_valid else 'FAIL',
                'received': f"0x{received_crc:04X}",
                'calculated': f"0x{calculated_crc:04X}",
                'valid': is_valid
            }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}






def main():
    """主函数 - 指令分析示例"""
    analyzer = MiyaCommandAnalyzer()
    
    # 示例指令
    test_command1 = "C7 12 01 01 01 01 04 04 01 01 01 01 01 01 01 01 00 00 62 78"  # 关机状态

    test_command2 = "C7 12 01 01 01 02 03 03 01 01 01 01 01 01 01 01 00 00 AD DD"  # 关机状态

   
    

    # all_status = analyzer.analyze_command(test_command1)
    # print(all_status)
    # print("--------------------------------")

    # status_data = analyzer.extract_status_data(test_command1)
    status_data = analyzer.get_status_data(test_command2)
    print(status_data)
    
  
    
if __name__ == "__main__":
    main() 