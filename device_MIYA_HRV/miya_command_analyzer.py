#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIYA新风系统指令分析器
用于分析和解码现有的485协议指令
基于MIYA 485协议规范
"""

from .crc16_utils import crc16_ccitt
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tcp_485_lib.tool import DataConverter
from typing import Dict

class MiyaCommandAnalyzer:
    """MIYA新风系统指令分析器"""
    
    def __init__(self):
        
        # 根据MIYA 485协议规范定义状态值含义
        self.status_meanings = {
            # 包头
            'header': {
                0xC7: '标准包头'
            },
            
            # 数据长度
            'data_length': {
                0x12: '18字节数据'
            },
            
            # 功能类型
            'function_type': {
                0x01: '设备状态查询',
                0x02: '设备状态设置(控制)'
            },
            
            # 机器运行状态
            'power_status': {
                0x01: '关机',
                0x02: '开机'
            },
            
            # 风速档位
            'fan_speed': {
                0x01: '风量0档',
                0x02: '风量1档',
                0x03: '风量2档',
                0x04: '风量3档',
                0x05: '风量4档'
            },
            
            # 负离子
            'negative_ion': {
                0x01: '负离子关',
                0x02: '负离子开'
            },
            
            # 辅热
            'auxiliary_heat': {
                0x01: '辅热关',
                0x02: '辅热开'
            },
            
            # 手动/自动
            'auto_manual': {
                0x01: '自动',
                0x02: '手动'
            },
            
            # 室外线表滑
            'outdoor_sensor': {
                0x01: '关闭',
                0x02: '开启'
            },
            
            # 内循环
            'inner_cycle': {
                0x01: '普通模式',
                0x02: '内循环'
            },
            
            # 旁通
            'bypass': {
                0x01: '旁通关',
                0x02: '旁通开'
            },
            
            # 定时
            'timer': {
                0x01: '定时关',
                0x02: '定时开'
            }
        }
    
    def analyze_command(self, hex_string: str) -> Dict:
        """
        分析单个指令
        
        Args:
            hex_string: 十六进制指令字符串，如 "C7 12 01 02 01..."
            
        Returns:
            分析结果字典
        """
        try:
            # 使用DataConverter替代controller.parse_hex_string
            data = DataConverter.hex_to_tcp(hex_string)
            data_len = len(data)
            
            # 基本信息
            analysis = {
                # 'raw_command': hex_string,
                # 'byte_count': data_len,
                # 'command_type': self._determine_command_type(data),
                'summary': {},
                #'crc_check': {}
            }
            
            # 生成摘要
            if data_len >= 18:
                analysis['summary'] = self._generate_summary(data)
                analysis['crc_check'] = self._check_crc(data)
            elif data_len == 7:
                analysis['summary'] = self._analyze_address_command(data)
            
            return analysis
            
        except Exception as e:
            return {
                'error': f"分析错误: {str(e)}",
                'raw_command': hex_string
            }
    
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
    
    def _generate_summary(self, data: bytes) -> Dict:
        """根据MIYA 485协议生成指令摘要"""
        return {
            '包头': f"0x{data[0]:02X} ({self.status_meanings['header'].get(data[0], '未知包头')})",
            '数据长度': f"0x{data[1]:02X} ({self.status_meanings['data_length'].get(data[1], f'{data[1]}字节')})",
            '设备地址': f"0x{data[2]:02X} (设备{data[2]})",
            '功能类型': f"0x{data[3]:02X} ({self.status_meanings['function_type'].get(data[3], '未知功能')})",
            '设备地址(重复)': f"0x{data[4]:02X} (设备{data[4]})",
            '机器运行状态': f"0x{data[5]:02X} ({self.status_meanings['power_status'].get(data[5], '未知状态')})",
            '进风风速': f"0x{data[6]:02X} ({self.status_meanings['fan_speed'].get(data[6], f'风速{data[6]}档')})",
            '排风风速': f"0x{data[7]:02X} ({self.status_meanings['fan_speed'].get(data[7], f'风速{data[7]}档')})",
            '负离子': f"0x{data[8]:02X} ({self.status_meanings['negative_ion'].get(data[8], '未知状态')})",
            '辅热': f"0x{data[9]:02X} ({self.status_meanings['auxiliary_heat'].get(data[9], '未知状态')})",
            '手动/自动': f"0x{data[10]:02X} ({self.status_meanings['auto_manual'].get(data[10], '未知模式')})",
            '室外线表滑': f"0x{data[11]:02X} ({self.status_meanings['outdoor_sensor'].get(data[11], '未知状态')})",
            '内循环': f"0x{data[12]:02X} ({self.status_meanings['inner_cycle'].get(data[12], '未知模式')})",
            '辅热(重复)': f"0x{data[13]:02X} ({self.status_meanings['auxiliary_heat'].get(data[13], '未知状态')})",
            '旁通': f"0x{data[14]:02X} ({self.status_meanings['bypass'].get(data[14], '未知状态')})",
            '定时': f"0x{data[15]:02X} ({self.status_meanings['timer'].get(data[15], '未知状态')})",
            '保留字段1': f"0x{data[16]:02X}",
            '保留字段2': f"0x{data[17]:02X}",
            'CRC16高位': f"0x{data[18]:02X}",
            'CRC16低位': f"0x{data[19]:02X}"
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
    
    # 示例指令分析
    command_result = analyzer.analyze_command("C7 12 01 01 01 01 04 04 01 01 01 01 01 01 01 01 00 00 62 78")
    
    print(command_result)

    # import json
    # print(json.dumps(command_result, ensure_ascii=False, indent=2))
    
if __name__ == "__main__":
    main() 