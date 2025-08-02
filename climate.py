"""MIYA HRV Climate 平台."""
import logging
from typing import Any, List, Optional

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_NAME,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    DEVICE_NAME,
    MANUFACTURER,
    ENTITY_TYPE_CLIMATE,
    MODE_DISPLAY_NAMES,
    FAN_MODE_LOW,
    FAN_MODE_MEDIUM,
    FAN_MODE_HIGH,
    generate_entity_id,
    get_commands,
)

_LOGGER = logging.getLogger(__name__)

# 支持的模式
SUPPORTED_FAN_MODES = [FAN_MODE_LOW, FAN_MODE_MEDIUM, FAN_MODE_HIGH]
SUPPORTED_HVAC_MODES = [HVACMode.OFF, HVACMode.AUTO, HVACMode.FAN_ONLY]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置MIYA HRV Climate平台."""
    device_data = hass.data[DOMAIN][config_entry.entry_id]
    device = device_data['device']
    
    # 连接到设备
    await device.connect()
    
    # 创建Climate实体
    climate_entity = MiyaHRVClimate(
        device=device,
        name=DEVICE_NAME,
        unique_id=generate_entity_id(config_entry.entry_id, ENTITY_TYPE_CLIMATE),
        hass=hass,
        entry_id=config_entry.entry_id,
    )
    
    async_add_entities([climate_entity])


class MiyaHRVClimate(ClimateEntity):
    """MIYA HRV Climate实体."""

    def __init__(self, device, name: str, unique_id: str, hass=None, entry_id=None):
        """初始化Climate实体."""
        self._device = device
        self._unique_id = unique_id
        self._hass = hass
        self._entry_id = entry_id
        
        # 状态变量 - 使用官方模式
        self._hvac_mode = HVACMode.OFF
        self._fan_mode = FAN_MODE_MEDIUM
        
        # 添加数据监听器
        self._device.add_listener(self._handle_device_data)
        
        # 支持的属性 (新风系统不需要温度控制)
        self._attr_supported_features = (
            ClimateEntityFeature.FAN_MODE
        )
        
        self._attr_hvac_modes = SUPPORTED_HVAC_MODES
        self._attr_fan_modes = SUPPORTED_FAN_MODES
        # 新风系统不需要温度控制
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        
        # 设置实体名称
        self._attr_name = "MIYA HRV 新风系统"
        self._attr_has_entity_name = False

    @property
    def unique_id(self) -> str:
        """返回唯一ID."""
        return self._unique_id

    @property
    def hvac_mode(self) -> HVACMode:
        """返回当前HVAC模式."""
        return self._hvac_mode
    
    @property
    def hvac_mode_display(self) -> str:
        """返回HVAC模式的显示名称."""
        return MODE_DISPLAY_NAMES.get(self._hvac_mode, str(self._hvac_mode))
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """返回额外的状态属性."""
        return {
            "hvac_mode_display": self.hvac_mode_display,
            "fan_mode_display": "LOW" if self._fan_mode == FAN_MODE_LOW else "MEDIUM" if self._fan_mode == FAN_MODE_MEDIUM else "HIGH"
        }

    @property
    def fan_mode(self) -> str:
        """返回当前风扇模式."""
        return self._fan_mode

    @property
    def current_temperature(self) -> Optional[float]:
        """返回当前温度 (新风系统不需要)."""
        return None

    @property
    def target_temperature(self) -> Optional[float]:
        """返回目标温度 (新风系统不需要)."""
        return None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """设置HVAC模式."""
        if hvac_mode not in SUPPORTED_HVAC_MODES:
            _LOGGER.error(f"不支持的模式: {hvac_mode}")
            return
        
        # 获取命令映射
        commands = get_commands(self._hass, self._entry_id)
        command = commands.get(hvac_mode)
        
        if not command:
            _LOGGER.error(f"未找到模式 {hvac_mode} 对应的命令")
            return
        
        self._hvac_mode = hvac_mode
        
        # 记录日志 - 使用自定义名称显示
        mode_name = MODE_DISPLAY_NAMES.get(hvac_mode, str(hvac_mode))
        _LOGGER.info(f"设置模式: {mode_name}")
        
        await self._device.send_command(command)
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """设置风扇模式."""
        if fan_mode in SUPPORTED_FAN_MODES:
            # 获取命令映射
            commands = get_commands(self._hass, self._entry_id)
            command = commands.get(fan_mode)
            
            if not command:
                _LOGGER.error(f"未找到风扇模式 {fan_mode} 对应的命令")
                return
            
            self._fan_mode = fan_mode
            
            # 记录日志
            mode_name = "LOW" if fan_mode == FAN_MODE_LOW else "MEDIUM" if fan_mode == FAN_MODE_MEDIUM else "HIGH"
            _LOGGER.info(f"设置风扇模式: {mode_name}")
            
            await self._device.send_command(command)
            self.async_write_ha_state()
        else:
            _LOGGER.error(f"不支持的风扇模式: {fan_mode}")



    # 新风系统不需要温度控制，移除 async_set_temperature 方法

    async def _handle_device_data(self, hex_data: str) -> None:
        """处理设备数据更新."""
        try:
            # 解析十六进制数据
            hex_bytes = hex_data.replace(" ", "").upper()
            
            # 解析电源状态 - 检查第5个字节
            if len(hex_bytes) >= 10:
                power_status = hex_bytes[8:10]  # 第5个字节
                if power_status == "01":
                    self._hvac_mode = HVACMode.OFF
                    _LOGGER.info("系统状态: 关闭")
                elif power_status == "02":
                    self._hvac_mode = HVACMode.AUTO
                    _LOGGER.info("系统状态: 自动模式")
            
            # 解析风扇速度 - 检查第6个字节
            if len(hex_bytes) >= 12:
                fan_speed = hex_bytes[10:12]  # 第6个字节
                if fan_speed == "01":
                    self._fan_mode = FAN_MODE_LOW
                    _LOGGER.info("风扇速度: 低速")
                elif fan_speed == "02":
                    self._fan_mode = FAN_MODE_LOW
                    _LOGGER.info("风扇速度: 低速")
                elif fan_speed == "03":
                    self._fan_mode = FAN_MODE_MEDIUM
                    _LOGGER.info("风扇速度: 中速")
                elif fan_speed == "04":
                    self._fan_mode = FAN_MODE_HIGH
                    _LOGGER.info("风扇速度: 高速")
                elif fan_speed == "05":
                    self._fan_mode = FAN_MODE_HIGH
                    _LOGGER.info("风扇速度: 高速")
            
            # 更新状态
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"处理设备数据时出错: {e}")

    async def async_will_remove_from_hass(self) -> None:
        """实体从Home Assistant移除时调用."""
        self._device.remove_listener(self._handle_device_data) 