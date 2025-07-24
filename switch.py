"""MIYA HRV Switch 平台."""
import logging
from typing import Any, List

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    DEVICE_NAME,
    MANUFACTURER,
    FUNCTION_PURIFICATION,
    FUNCTION_INTERNAL_CIRCULATION,
    FUNCTION_EXTERNAL_CIRCULATION,
    MODE_OFF,
    COMMANDS,
)

_LOGGER = logging.getLogger(__name__)

# 支持的开关功能
SWITCH_FUNCTIONS = [
    (FUNCTION_PURIFICATION, "净化功能", "mdi:air-filter"),
    (FUNCTION_INTERNAL_CIRCULATION, "内循环", "mdi:refresh"),
    (FUNCTION_EXTERNAL_CIRCULATION, "外循环", "mdi:airplane"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置MIYA HRV Switch平台."""
    device = hass.data[DOMAIN][config_entry.entry_id]
    
    # 创建Switch实体
    switches = []
    for function_id, name, icon in SWITCH_FUNCTIONS:
        switch_entity = MiyaHRVSwitch(
            device=device,
            function_id=function_id,
            name=f"{DEVICE_NAME} {name}",
            unique_id=f"{config_entry.entry_id}_{function_id}",
            icon=icon,
        )
        switches.append(switch_entity)
    
    async_add_entities(switches)


class MiyaHRVSwitch(SwitchEntity):
    """MIYA HRV Switch实体."""

    def __init__(self, device, function_id: str, name: str, unique_id: str, icon: str):
        """初始化Switch实体."""
        self._device = device
        self._function_id = function_id
        self._name = name
        self._unique_id = unique_id
        self._icon = icon
        self._is_on = False
        
        # 添加数据监听器
        self._device.add_listener(self._handle_device_data)

    @property
    def name(self) -> str:
        """返回实体名称."""
        return self._name

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
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """打开开关."""
        command = COMMANDS[self._function_id]
        self._is_on = True
        await self._device.send_command(command)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """关闭开关."""
        # 发送关闭命令
        command = COMMANDS[MODE_OFF]  # 使用通用的关闭命令
        self._is_on = False
        await self._device.send_command(command)
        self.async_write_ha_state()
        await self._device.send_command(command)
        self.async_write_ha_state()

    async def _handle_device_data(self, data: dict) -> None:
        """处理设备数据更新."""
        try:
            # 根据解析的数据更新状态
            if "functions" in data:
                functions = data["functions"]
                if self._function_id in functions:
                    self._is_on = functions[self._function_id]
                    self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"处理设备数据时出错: {e}")

    async def async_will_remove_from_hass(self) -> None:
        """实体从Home Assistant移除时调用."""
        self._device.remove_listener(self._handle_device_data) 