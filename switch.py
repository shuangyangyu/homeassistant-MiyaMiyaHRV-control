"""MIYA HRV Switch 平台."""
from .helpers.common_imports import (
    logging, Any, List,
    SwitchEntity, HVACMode, ConfigEntry, CONF_NAME,
    HomeAssistant, AddEntitiesCallback, ConfigType, DiscoveryInfoType,
    _LOGGER
)

from .const import (
    DOMAIN,
    DEVICE_NAME,
    ENTITY_TYPE_SWITCH,
)

# 导入辅助函数
from .helpers import get_device_status, send_device_command, get_commands, generate_entity_id

# 支持的开关功能
SWITCH_FUNCTIONS = [
    ("uv_sterilization", "mdi:lightbulb"),
    ("inner_cycle", "mdi:refresh"),
    ("auxiliary_heat", "mdi:fire"),
    ("bypass", "mdi:gate"),
    ("negative_ion", "mdi:atom"),
    ("sleep_mode", "mdi:bed"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置MIYA HRV Switch平台."""
    device_data = hass.data[DOMAIN][config_entry.entry_id]
    device = device_data['device']
    
    # 创建Switch实体
    switches = []
    for function_id, icon in SWITCH_FUNCTIONS:
        switch_entity = MiyaHRVSwitch(
            device=device,
            function_id=function_id,
            name=DEVICE_NAME,
            unique_id=generate_entity_id(config_entry.entry_id, ENTITY_TYPE_SWITCH, function_id),
            icon=icon,
            hass=hass,
            entry_id=config_entry.entry_id,
        )
        switches.append(switch_entity)
    
    # 注册实体到管理器
    device_data = hass.data[DOMAIN][config_entry.entry_id]
    for entity in switches:
        if 'manager' in device_data:
            device_data['manager'].register_entity(entity.unique_id, entity)
        else:
            # 兼容旧版本
            device_data['entities'][entity.unique_id] = entity
    
    async_add_entities(switches)


class MiyaHRVSwitch(SwitchEntity):
    """MIYA HRV Switch实体."""

    def __init__(self, device, function_id: str, name: str, unique_id: str, icon: str, hass=None, entry_id=None):
        """初始化Switch实体."""
        self._device = device
        self._function_id = function_id
        self._name = name
        self._unique_id = unique_id
        self._icon = icon
        self._hass = hass
        self._entry_id = entry_id
        self._is_on = False
        self._current_status = {}  # 存储当前状态数据
        
        # 移除旧的监听器方式，使用新的状态管理系统
        # self._device.add_listener(self._handle_device_data)

    @property
    def name(self) -> str:
        """返回实体名称."""
        return f"MIYA HRV {self._function_id.replace('_', ' ').title()}"

    @property
    def unique_id(self) -> str:
        """返回唯一ID."""
        return self._unique_id

    @property
    def icon(self) -> str:
        """返回图标."""
        return self._icon

    @property
    def is_on(self) -> bool:
        """返回开关状态."""
        # 优先使用本地状态数据，如果没有则从全局获取
        status = self._current_status if self._current_status else get_device_status(self._hass, self._entry_id)
        
        # 直接使用状态字典中的键名
        if self._function_id == "negative_ion":
            return status.get('negative_ion') == 'on'
        elif self._function_id == "uv_sterilization":
            return status.get('UV_sterilization') == 'on'
        elif self._function_id == "sleep_mode":
            return status.get('sleep_mode') == 'on'
        elif self._function_id == "inner_cycle":
            return status.get('inner_cycle') == 'on'
        elif self._function_id == "auxiliary_heat":
            return status.get('auxiliary_heat') == 'on'
        elif self._function_id == "bypass":
            return status.get('bypass') == 'on'

        
        return self._is_on  # 回退到旧的状态

    async def async_turn_on(self, **kwargs: Any) -> None:
        """打开开关."""
        # 直接使用英文命令键
        command_map = {
            "negative_ion": "negative_ion_on",
            "uv_sterilization": "uv_sterilization_on",
            "sleep_mode": "sleep_mode_on",
            "inner_cycle": "inner_cycle_on",
            "auxiliary_heat": "auxiliary_heat_on",
            "bypass": "bypass_on"
        }
        
        command_name = command_map.get(self._function_id)
        if command_name:
            success = await send_device_command(self._hass, self._entry_id, command_name)
            if success:
                self._is_on = True
                self.async_write_ha_state()
        else:
            _LOGGER.error(f"未找到功能 {self._function_id} 对应的开启命令")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """关闭开关."""
        # 直接使用英文命令键
        command_map = {
            "negative_ion": "negative_ion_off",
            "uv_sterilization": "uv_sterilization_off",
            "sleep_mode": "sleep_mode_off",
            "inner_cycle": "inner_cycle_off",
            "auxiliary_heat": "auxiliary_heat_off",
            "bypass": "bypass_off"
        }
        
        command_name = command_map.get(self._function_id)
        if command_name:
            success = await send_device_command(self._hass, self._entry_id, command_name)
            if success:
                self._is_on = False
                self.async_write_ha_state()
        else:
            _LOGGER.error(f"未找到功能 {self._function_id} 对应的关闭命令")

    def update_status(self, status_data: dict):
        """更新实体状态数据."""
        self._current_status = status_data
        self.async_write_ha_state()
        _LOGGER.debug(f"📊 Switch {self._function_id} 状态已更新: {status_data}")

    # 移除旧的设备数据处理方法，现在使用新的状态管理系统
    # async def _handle_device_data(self, hex_data: str) -> None:
    #     """处理设备数据更新."""
    #     # 这个方法不再需要，因为状态现在通过 helpers 获取

    async def async_will_remove_from_hass(self) -> None:
        """实体从Home Assistant移除时调用."""
        # 移除旧的监听器调用，现在使用新的状态管理系统
        # self._device.remove_listener(self._handle_device_data) 