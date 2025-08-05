"""
Home Assistant 工具模块
====================

为 HA 组件提供设备状态获取和命令发送的辅助函数。
"""

from .common_imports import asyncio, logging, Optional, Dict, Any, HomeAssistant, ConfigEntry, CONF_HOST, CONF_PORT, _LOGGER

from .communicator import TCP_485_Device
from .protocal import MiyaCommandAnalyzer, cmd_calculate
from .config_input import command_set_dict
from .const import CONF_DEVICE_ADDR

def get_device_status(hass, entry_id: str) -> Dict[str, Any]:
    """获取设备状态数据."""
    try:
        if entry_id in hass.data.get('miya_hrv', {}):
            device_data = hass.data['miya_hrv'][entry_id]
            # 优先使用管理器获取状态
            if 'manager' in device_data:
                status = device_data['manager'].get_status()
            else:
                # 兼容旧版本
                status = device_data.get('status', {})
            _LOGGER.debug(f"获取到设备状态: {status}")
            return status
        _LOGGER.warning(f"未找到 entry_id: {entry_id} 的状态数据")
        return {}
    except Exception as e:
        _LOGGER.error(f"获取设备状态失败: {e}")
        return {}

def get_device_instance(hass, entry_id: str):
    """获取设备实例."""
    try:
        if entry_id in hass.data.get('miya_hrv', {}):
            return hass.data['miya_hrv'][entry_id].get('device')
        return None
    except Exception as e:
        _LOGGER.error(f"获取设备实例失败: {e}")
        return None

def get_commands(hass, entry_id: str) -> Dict[str, Any]:
    """获取命令映射，优先使用计算后的命令，否则返回空字典."""
    if hass and entry_id:
        try:
            # 尝试从Home Assistant数据中获取计算后的命令
            domain_data = hass.data.get('miya_hrv', {})
            entry_data = domain_data.get(entry_id, {})
            calculated_commands = entry_data.get('commands', {})
            
            if calculated_commands and 'command_fixed' in calculated_commands:
                # 将计算后的命令映射到标准格式
                fixed_commands = calculated_commands['command_fixed']
                
                # 创建命令映射
                commands = {}
                
                # 映射风扇模式
                if 'power_off' in fixed_commands:
                    commands['power_off'] = fixed_commands['power_off']
                if 'power_auto' in fixed_commands:
                    commands['power_auto'] = fixed_commands['power_auto']
                
                # 映射内循环命令
                if 'inner_cycle_on' in fixed_commands:
                    commands['inner_cycle_on'] = fixed_commands['inner_cycle_on']
                if 'inner_cycle_off' in fixed_commands:
                    commands['inner_cycle_off'] = fixed_commands['inner_cycle_off']
                
                # 映射辅助加热命令
                if 'auxiliary_heat_on' in fixed_commands:
                    commands['auxiliary_heat_on'] = fixed_commands['auxiliary_heat_on']
                if 'auxiliary_heat_off' in fixed_commands:
                    commands['auxiliary_heat_off'] = fixed_commands['auxiliary_heat_off']
                
                # 映射UV杀菌命令
                if 'uv_sterilization_on' in fixed_commands:
                    commands['uv_sterilization_on'] = fixed_commands['uv_sterilization_on']
                if 'uv_sterilization_off' in fixed_commands:
                    commands['uv_sterilization_off'] = fixed_commands['uv_sterilization_off']
                
                # 映射旁通命令
                if 'bypass_on' in fixed_commands:
                    commands['bypass_on'] = fixed_commands['bypass_on']
                if 'bypass_off' in fixed_commands:
                    commands['bypass_off'] = fixed_commands['bypass_off']
                
                # 映射负离子命令
                if 'negative_ion_on' in fixed_commands:
                    commands['negative_ion_on'] = fixed_commands['negative_ion_on']
                if 'negative_ion_off' in fixed_commands:
                    commands['negative_ion_off'] = fixed_commands['negative_ion_off']
                
                # 映射睡眠模式命令
                if 'sleep_mode_on' in fixed_commands:
                    commands['sleep_mode_on'] = fixed_commands['sleep_mode_on']
                if 'sleep_mode_off' in fixed_commands:
                    commands['sleep_mode_off'] = fixed_commands['sleep_mode_off']
                
                # 添加其他命令
                for key, value in fixed_commands.items():
                    if key not in commands:
                        commands[key] = value
                
                return commands
                
        except Exception as e:
            _LOGGER.error(f"获取计算后的命令失败: {e}")
    
    # 如果没有计算后的命令，返回空字典
    return {}

async def send_device_command(hass, entry_id: str, command_name: str) -> bool:
    """发送设备命令."""
    try:
        device = get_device_instance(hass, entry_id)
        commands = get_commands(hass, entry_id)
        
        if not device or not commands:
            _LOGGER.error("设备或命令不可用")
            return False
        
        # 直接使用传入的命令键，不再需要映射
        command = commands.get(command_name)
        if command:
            await device.send_command(command)
            _LOGGER.info(f"📡 发送命令: {command_name} -> {command}")
            return True
        else:
            _LOGGER.error(f"❌ 未找到命令: {command_name}")
            _LOGGER.debug(f"📋 可用命令: {list(commands.keys())}")
            return False
            
    except Exception as e:
        _LOGGER.error(f"❌ 发送命令失败: {e}")
        return False

def get_fan_mode(status: Dict[str, Any]) -> str:
    """从状态数据中获取风扇模式."""
    return status.get('fan_mode', 'unknown')

def get_operation_mode(status: Dict[str, Any]) -> str:
    """从状态数据中获取运行模式."""
    return status.get('mode', 'unknown')

def get_negative_ion_status(status: Dict[str, Any]) -> bool:
    """从状态数据中获取负离子状态."""
    ion_status = status.get('negative_ion', 'off')
    return ion_status == 'on'

def get_uv_sterilization_status(status: Dict[str, Any]) -> bool:
    """从状态数据中获取UV杀菌状态."""
    uv_status = status.get('UV_sterilization', 'off')
    return uv_status == 'on'

def get_sleep_mode_status(status: Dict[str, Any]) -> bool:
    """从状态数据中获取睡眠模式状态."""
    sleep_status = status.get('sleep_mode', 'off')
    return sleep_status == 'on'

def get_inner_cycle_status(status: Dict[str, Any]) -> bool:
    """从状态数据中获取内循环状态."""
    cycle_status = status.get('inner_cycle', 'off')
    return cycle_status == 'on'

def get_auxiliary_heat_status(status: Dict[str, Any]) -> bool:
    """从状态数据中获取辅助加热状态."""
    heat_status = status.get('auxiliary_heat', 'off')
    return heat_status == 'on'

def get_bypass_status(status: Dict[str, Any]) -> bool:
    """从状态数据中获取旁通状态."""
    bypass_status = status.get('bypass', 'off')
    return bypass_status == 'on'

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
        return f"miya_{function_id}"
    else:
        return f"miya_{entity_type}"

def generate_device_id(host: str, port: int) -> str:
    """生成设备唯一标识符。
    
    Args:
        host: 设备主机地址
        port: 设备端口
    
    Returns:
        设备唯一标识符
    """
    return f"{host}:{port}"

class MiyaHRVManager:
    """MIYA HRV 组件管理器."""
    
    def __init__(self, hass: HomeAssistant, entry_id: str):
        """初始化管理器."""
        self.hass = hass
        self.entry_id = entry_id
        self.calculated_commands = None
        self.device_status = {}
        self.device = None
        self.analyzer = None
        self.entities = {}
    
    def calculate_commands(self, device_addr: str = "01"):
        """计算设备命令，包含CRC校验."""
        try:
            self.calculated_commands = cmd_calculate(command_set_dict, device_addr)
            _LOGGER.info("命令计算完成")
            return self.calculated_commands
        except Exception as e:
            _LOGGER.error(f"命令计算失败: {e}")
            return None
    
    async def setup(self, entry: ConfigEntry):
        """设置组件."""
        self.hass.data.setdefault('miya_hrv', {})
        
        # 获取设备地址
        device_addr = entry.data.get('device_addr', '01')
        
        # 计算命令
        if self.calculated_commands is None:
            self.calculate_commands(device_addr)
        
        # 创建设备实例
        self.device = TCP_485_Device(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, 38)  
        )
        
        # 创建状态分析器
        self.analyzer = MiyaCommandAnalyzer()
        
        # 存储到 hass.data
        self.hass.data['miya_hrv'][self.entry_id] = {
            'device': self.device,
            'analyzer': self.analyzer,
            'commands': self.calculated_commands,
            'status': self.device_status,
            'entities': self.entities,
            'manager': self  # 存储管理器引用
        }
        
        # 启动设备监听
        await self.start_device_monitoring()
        
        return True
    
    async def start_device_monitoring(self):
        """启动设备监听和状态更新."""
        async def connect_and_listen():
            """连接设备并持续监听数据."""
            try:
                # 连接设备
                if await self.device.connect():
                    _LOGGER.info(f"✅ 成功连接到设备 {self.device.host}:{self.device.port}")
                    
                    # 发送状态查询命令
                    if self.calculated_commands and 'command_fixed' in self.calculated_commands:
                        query_cmd = self.calculated_commands['command_fixed'].get('设备状态查询')
                        if query_cmd:
                            await self.device.send_command(query_cmd)
                            _LOGGER.info(f"📡 发送状态查询命令: {query_cmd}")
                    
                    # 持续监听数据
                    async for data in self.device.listen_for_data():
                        try:
                            # 解析状态数据
                            status_data = self.analyzer.get_status_data(data)
                            
                            # 更新状态_更新到hass.data中
                            self.device_status.update(status_data)
                            
                            _LOGGER.info(f"状态已更新: {status_data}")
                            
                            # 通知所有相关实体更新状态
                            await self.notify_entities_status_update(status_data)
                            
                        except Exception as e:
                            _LOGGER.error(f"解析数据失败: {e}")
                            
                else:
                    _LOGGER.error(f"无法连接到设备 {self.device.host}:{self.device.port}")
                    
            except Exception as e:
                _LOGGER.error(f"设备监听任务出错: {e}")
        
        # 启动监听任务
        self.hass.async_create_task(connect_and_listen())
    
    async def notify_entities_status_update(self, status_data: dict):
        """通知所有实体状态更新."""
        try:
            # 直接调用实体的 update_status 方法
            for entity_name, entity in self.entities.items():
                try:
                    if hasattr(entity, 'update_status'):
                        entity.update_status(status_data)
                        _LOGGER.debug(f"📡 直接更新实体: {entity_name}")
                except Exception as e:
                    _LOGGER.error(f"❌ 更新实体 {entity_name} 失败: {e}")
                    
        except Exception as e:
            _LOGGER.error(f"❌ 通知实体状态更新失败: {e}")
    
    def get_status(self) -> dict:
        """获取设备状态."""
        return self.device_status.copy()
    
    def register_entity(self, entity_id: str, entity):
        """注册实体."""
        self.entities[entity_id] = entity
    
    def unregister_entity(self, entity_id: str):
        """注销实体."""
        if entity_id in self.entities:
            del self.entities[entity_id]
    
    async def cleanup(self):
        """清理资源."""
        if self.device:
            await self.device.disconnect()
        self.entities.clear()
        self.device_status.clear() 