"""MIYA HRV Switch 平台."""
import logging
from typing import Any, List

from homeassistant.components.switch import SwitchEntity
from homeassistant.components.climate import HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    DEVICE_NAME,
    MANUFACTURER,
    ENTITY_TYPE_SWITCH,
    FUNCTION_PURIFICATION,
    FUNCTION_INTERNAL_CIRCULATION,
    FUNCTION_EXTERNAL_CIRCULATION,
    FUNCTION_BYPASS,
    FUNCTION_NEGATIVE_ION,
    FUNCTION_SLEEP_MODE,
    generate_entity_id,
    get_commands,
)

_LOGGER = logging.getLogger(__name__)

# 支持的开关功能
SWITCH_FUNCTIONS = [
    (FUNCTION_PURIFICATION, "mdi:air-filter"),
    (FUNCTION_INTERNAL_CIRCULATION, "mdi:refresh"),
    (FUNCTION_EXTERNAL_CIRCULATION, "mdi:airplane"),
    (FUNCTION_BYPASS, "mdi:gate"),
    (FUNCTION_NEGATIVE_ION, "mdi:atom"),
    (FUNCTION_SLEEP_MODE, "mdi:sleep"),
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
        
        # 添加数据监听器
        self._device.add_listener(self._handle_device_data)

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
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """打开开关."""
        # 获取命令映射
        commands = get_commands(self._hass, self._entry_id)
        command = commands.get(self._function_id)
        
        if not command:
            _LOGGER.error(f"未找到功能 {self._function_id} 对应的开启命令")
            return
        
        self._is_on = True
        await self._device.send_command(command)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """关闭开关."""
        # 获取命令映射
        commands = get_commands(self._hass, self._entry_id)
        
        # 尝试获取对应的关闭命令
        off_command_key = self._function_id + "_off"
        command = commands.get(off_command_key)
        
        # 如果没有找到对应的关闭命令，使用通用关闭命令
        if not command:
            command = commands.get(HVACMode.OFF)
        
        if not command:
            _LOGGER.error(f"未找到功能 {self._function_id} 对应的关闭命令")
            return
        
        self._is_on = False
        await self._device.send_command(command)
        self.async_write_ha_state()

    async def _handle_device_data(self, hex_data: str) -> None:
        """处理设备数据更新."""
        try:
            # 解析十六进制数据
            hex_bytes = hex_data.replace(" ", "").upper()
            
            # 根据功能ID解析对应的状态
            if self._function_id == "purification":
                # 辅热/净化功能 - 检查第13个字节
                if len(hex_bytes) >= 26:
                    status = hex_bytes[24:26]  # 第13个字节
                    self._is_on = status == "02"
                    _LOGGER.info(f"净化功能状态: {'开启' if self._is_on else '关闭'}")
                    
            elif self._function_id == "internal_circulation":
                # 内循环功能 - 检查第12个字节
                if len(hex_bytes) >= 24:
                    status = hex_bytes[22:24]  # 第12个字节
                    self._is_on = status == "02"
                    _LOGGER.info(f"内循环功能状态: {'开启' if self._is_on else '关闭'}")
                    
            elif self._function_id == "external_circulation":
                # 外循环/UV杀菌功能 - 检查第11个字节
                if len(hex_bytes) >= 22:
                    status = hex_bytes[20:22]  # 第11个字节
                    self._is_on = status == "02"
                    _LOGGER.info(f"外循环功能状态: {'开启' if self._is_on else '关闭'}")
                    
            elif self._function_id == "bypass":
                # 旁通功能 - 检查第15个字节
                if len(hex_bytes) >= 30:
                    status = hex_bytes[28:30]  # 第15个字节
                    self._is_on = status == "02"
                    _LOGGER.info(f"旁通功能状态: {'开启' if self._is_on else '关闭'}")
                    
            elif self._function_id == "negative_ion":
                # 负离子功能 - 检查第9个字节
                if len(hex_bytes) >= 18:
                    status = hex_bytes[16:18]  # 第9个字节
                    self._is_on = status == "02"
                    _LOGGER.info(f"负离子功能状态: {'开启' if self._is_on else '关闭'}")
                    
            elif self._function_id == "sleep_mode":
                # 睡眠模式 - 检查第10个字节
                if len(hex_bytes) >= 20:
                    status = hex_bytes[18:20]  # 第10个字节
                    self._is_on = status == "02"
                    _LOGGER.info(f"睡眠模式状态: {'开启' if self._is_on else '关闭'}")
            
            # 更新状态
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"处理设备数据时出错: {e}")

    async def async_will_remove_from_hass(self) -> None:
        """实体从Home Assistant移除时调用."""
        self._device.remove_listener(self._handle_device_data) 