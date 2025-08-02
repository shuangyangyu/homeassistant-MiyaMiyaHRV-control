"""MIYA HRV 集成常量."""
from homeassistant.const import Platform
from homeassistant.components.climate import HVACMode

DOMAIN = "miya_hrv"
DEFAULT_PORT = 38

# 平台
PLATFORMS = [Platform.CLIMATE, Platform.SWITCH]

# 设备信息
DEVICE_NAME = "MIYA HRV Fresh Air System"
MANUFACTURER = "MIYA"

# 实体标识符前缀
ENTITY_ID_PREFIX = "miya"

# 实体类型标识符
ENTITY_TYPE_CLIMATE = "climate"
ENTITY_TYPE_SWITCH = "switch"

# 功能开关
FUNCTION_PURIFICATION = "purification"
FUNCTION_INTERNAL_CIRCULATION = "internal_circulation"
FUNCTION_EXTERNAL_CIRCULATION = "external_circulation"
FUNCTION_BYPASS = "bypass"
FUNCTION_NEGATIVE_ION = "negative_ion"
FUNCTION_SLEEP_MODE = "sleep_mode"

# 风扇模式
FAN_MODE_LOW = "low"
FAN_MODE_MEDIUM = "medium"
FAN_MODE_HIGH = "high"

# 模式显示名称映射
MODE_DISPLAY_NAMES = {
    HVACMode.OFF: "OFF",
    HVACMode.AUTO: "AUTO",
    HVACMode.FAN_ONLY: "FAN_ONLY",
}






# 命令映射函数
def get_commands(hass=None, entry_id=None):
    """获取命令映射，优先使用计算后的命令，否则返回空字典."""
    if hass and entry_id:
        try:
            # 尝试从Home Assistant数据中获取计算后的命令
            domain_data = hass.data.get(DOMAIN, {})
            entry_data = domain_data.get(entry_id, {})
            calculated_commands = entry_data.get('commands', {})
            
            if calculated_commands and 'command_fixed' in calculated_commands:
                # 将计算后的命令映射到标准格式
                fixed_commands = calculated_commands['command_fixed']
                
                # 创建命令映射
                commands = {}
                
                # 映射风扇模式
                if 'power_off' in fixed_commands:
                    commands[HVACMode.OFF] = fixed_commands['power_off']
                if 'power_auto' in fixed_commands:
                    commands[HVACMode.AUTO] = fixed_commands['power_auto']
                
                # 映射内循环命令
                if 'inner_cycle_on' in fixed_commands:
                    commands[FUNCTION_INTERNAL_CIRCULATION] = fixed_commands['inner_cycle_on']
                if 'inner_cycle_off' in fixed_commands:
                    commands[FUNCTION_INTERNAL_CIRCULATION + "_off"] = fixed_commands['inner_cycle_off']
                
                # 映射辅热命令
                if 'auxiliary_heat_on' in fixed_commands:
                    commands[FUNCTION_PURIFICATION] = fixed_commands['auxiliary_heat_on']
                if 'auxiliary_heat_off' in fixed_commands:
                    commands[FUNCTION_PURIFICATION + "_off"] = fixed_commands['auxiliary_heat_off']
                
                # 映射UV杀菌命令
                if 'uv_sterilization_on' in fixed_commands:
                    commands[FUNCTION_EXTERNAL_CIRCULATION] = fixed_commands['uv_sterilization_on']
                if 'uv_sterilization_off' in fixed_commands:
                    commands[FUNCTION_EXTERNAL_CIRCULATION + "_off"] = fixed_commands['uv_sterilization_off']
                
                # 映射旁通命令
                if 'bypass_on' in fixed_commands:
                    commands[FUNCTION_BYPASS] = fixed_commands['bypass_on']
                if 'bypass_off' in fixed_commands:
                    commands[FUNCTION_BYPASS + "_off"] = fixed_commands['bypass_off']
                
                # 映射负离子命令
                if 'negative_ion_on' in fixed_commands:
                    commands[FUNCTION_NEGATIVE_ION] = fixed_commands['negative_ion_on']
                if 'negative_ion_off' in fixed_commands:
                    commands[FUNCTION_NEGATIVE_ION + "_off"] = fixed_commands['negative_ion_off']
                
                # 映射睡眠模式命令
                if 'sleep_mode_on' in fixed_commands:
                    commands[FUNCTION_SLEEP_MODE] = fixed_commands['sleep_mode_on']
                if 'sleep_mode_off' in fixed_commands:
                    commands[FUNCTION_SLEEP_MODE + "_off"] = fixed_commands['sleep_mode_off']
                
                # 添加其他命令
                for key, value in fixed_commands.items():
                    if key not in commands:
                        commands[key] = value
                
                return commands
                
        except Exception as e:
            import logging
            _LOGGER = logging.getLogger(__name__)
            _LOGGER.error(f"获取计算后的命令失败: {e}")
    
    # 如果没有计算后的命令，返回空字典
    return {}

# 配置选项
CONF_HOST = "host"
CONF_PORT = "port"
CONF_NAME = "name"

# 默认值
DEFAULT_NAME = "MIYA HRV"
DEFAULT_HOST = "192.168.1.100"

# 验证
MIN_TEMP = 16.0
MAX_TEMP = 30.0
TEMP_STEP = 0.5

# 实体标识符生成函数
def generate_entity_id(entry_id: str, entity_type: str, function_id: str = None) -> str:
    """生成简洁的实体唯一标识符。
    
    Args:
        entry_id: 配置条目ID
        entity_type: 实体类型 (climate, switch等)
        function_id: 功能ID (仅用于switch实体)
    
    Returns:
        简洁的实体唯一标识符
    """
    if function_id:
        return f"{ENTITY_ID_PREFIX}_{function_id}"
    else:
        return f"{ENTITY_ID_PREFIX}_{entity_type}"

def generate_device_id(host: str, port: int) -> str:
    """生成设备唯一标识符。
    
    Args:
        host: 设备主机地址
        port: 设备端口
    
    Returns:
        设备唯一标识符
    """
    return f"{host}:{port}" 