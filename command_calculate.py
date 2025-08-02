from config_input import command_set_dict as input_dict
from tcp_485_lib import hex_to_bytes,bytes_to_hex
from device_MIYA_HRV.crc16_utils import crc16_ccitt,crc16_ccitt_bytes

device_addr="01"

def cmd_calculate2(input_dict, device_addr):
    
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
        "command_broadcast":input_dict.get("command_broadcast")
    }
    
    return out_dict
