'''
协议层
封装设备协议细节，生成和解析原始命令数据。

'''
from typing import Dict

try:
    from .config_input import command_set_dict as input_dict
    from .crc_miya import crc16_ccitt,crc16_ccitt_bytes
    from .config_input import status_meanings_dict as status_meanings_dict
except ImportError:
    from config_input import command_set_dict as input_dict
    from crc_miya import crc16_ccitt,crc16_ccitt_bytes
    from config_input import status_meanings_dict as status_meanings_dict

try:
    from .tcp_485_lib import hex_to_bytes,bytes_to_hex,DataConverter
except ImportError:
    from tcp_485_lib import hex_to_bytes,bytes_to_hex,DataConverter

device_addr="01"

# 生成原始命令数据

def cmd_calculate(input_dict, device_addr):
    
    """
    Input device address and command dictionary, calculate CRC and return a new command dictionary
    
    """
    
    complete_command_dict = {}
    
    fixed_dict=input_dict.get("command_fixed")
    for command_name, command_hex in fixed_dict.items():
        try:
            value_bytes = bytearray(hex_to_bytes(command_hex))
            device_addr_int = int(device_addr, 16)
            value_bytes[2] = device_addr_int
            value_bytes[4] = device_addr_int
            crc_data = value_bytes[0:18]
            crc = crc16_ccitt(crc_data)
            value_bytes.append((crc >> 8) & 0xFF)  # byte 18: CRC高位
            value_bytes.append(crc & 0xFF)         # byte 19: CRC低位
            new_value = bytes_to_hex(bytes(value_bytes))  
            complete_command_dict[command_name] = new_value
            
        except Exception as e:
            print(f"处理命令 {command_name} 时出错: {e}")

    out_dict={
        "command_fixed":complete_command_dict,
        "command_broadcast":input_dict.get("command_broadcast"),
        "command_broadcast_status":input_dict.get("command_broadcast_status")
    }
    
    return out_dict

# 解析原始命令数据

class MiyaCommandAnalyzer:
    """MIYA新风系统指令分析器"""
    
    def __init__(self):

        self.status_meanings = status_meanings_dict
        
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
        elif command_type == "设备状态设置(控制)指令":
            # 控制指令的响应，通常包含当前状态
            info_table = self._generate_hass_status_table(data)
            fan_speed_status = self._fan_speed_status(data)
            if fan_speed_status:  # 检查是否为None
                info_table.update(fan_speed_status)
            mode_status = self._mode_status(data)
            if mode_status:  # 检查是否为None
                info_table.update(mode_status)
            return info_table
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
  


if __name__ == "__main__":
    # print(cmd_calculate(input_dict, device_addr))
     print(MiyaCommandAnalyzer().get_status_data("C7 12 01 01 01 02 03 03 01 01 01 01 01 01 01 01 00 00 AD DD")) 
