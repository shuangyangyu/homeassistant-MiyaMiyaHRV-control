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
    FAN_MODE_LOW,
    FAN_MODE_MEDIUM,
    FAN_MODE_HIGH,
    FAN_MODE_NAMES,
    COMMANDS,
)

_LOGGER = logging.getLogger(__name__)

# 支持的模式 - 使用Home Assistant内置模式
SUPPORTED_FAN_MODES = [FAN_MODE_LOW, FAN_MODE_MEDIUM, FAN_MODE_HIGH]
SUPPORTED_HVAC_MODES = [HVACMode.OFF, HVACMode.AUTO, HVACMode.FAN_ONLY]
# 使用Home Assistant内置预设模式
SUPPORTED_PRESET_MODES = ["ECO", "AWAY", "SLEEP"]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置MIYA HRV Climate平台."""
    device = hass.data[DOMAIN][config_entry.entry_id]
    
    # 连接到设备
    await device.connect()
    
    # 创建Climate实体
    climate_entity = MiyaHRVClimate(
        device=device,
        name=DEVICE_NAME,
        unique_id=f"{config_entry.entry_id}_climate",
    )
    
    async_add_entities([climate_entity])


class MiyaHRVClimate(ClimateEntity):
    """MIYA HRV Climate实体."""

    def __init__(self, device, name: str, unique_id: str):
        """初始化Climate实体."""
        self._device = device
        self._name = name
        self._unique_id = unique_id
        
        # 状态变量 - 使用Home Assistant内置模式
        self._hvac_mode = HVACMode.OFF
        self._fan_mode = FAN_MODE_MEDIUM
        self._current_preset = None
        
        # 添加数据监听器
        self._device.add_listener(self._handle_device_data)
        
        # 支持的属性 (新风系统不需要温度控制)
        self._attr_supported_features = (
            ClimateEntityFeature.FAN_MODE |
            ClimateEntityFeature.PRESET_MODE
        )
        
        self._attr_hvac_modes = SUPPORTED_HVAC_MODES
        self._attr_fan_modes = SUPPORTED_FAN_MODES
        self._attr_preset_modes = SUPPORTED_PRESET_MODES
        # 新风系统不需要温度控制
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

    @property
    def name(self) -> str:
        """返回实体名称."""
        return self._name

    @property
    def unique_id(self) -> str:
        """返回唯一ID."""
        return self._unique_id

    @property
    def hvac_mode(self) -> HVACMode:
        """返回当前HVAC模式."""
        return self._hvac_mode

    @property
    def fan_mode(self) -> str:
        """返回当前风扇模式."""
        return self._fan_mode

    @property
    def preset_mode(self) -> Optional[str]:
        """返回当前预设模式."""
        return self._current_preset

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
        
        # 使用Home Assistant内置HVACMode
        command = COMMANDS[hvac_mode]
        self._hvac_mode = hvac_mode
        
        # 记录日志
        mode_name = "关闭" if hvac_mode == HVACMode.OFF else "自动" if hvac_mode == HVACMode.AUTO else "手动"
        _LOGGER.info(f"🔄 设置模式: {mode_name}")
        print(f"🔄 设置模式: {mode_name}")
        
        await self._device.send_command(command)
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """设置风扇模式."""
        if fan_mode in SUPPORTED_FAN_MODES:
            command = COMMANDS[fan_mode]
            self._fan_mode = fan_mode
            
            # 获取中文显示名称
            fan_mode_name = FAN_MODE_NAMES.get(fan_mode, fan_mode)
            _LOGGER.info(f"🔄 设置风扇模式: {fan_mode_name}")
            print(f"🔄 设置风扇模式: {fan_mode_name}")
            
            await self._device.send_command(command)
            self.async_write_ha_state()
        else:
            _LOGGER.error(f"不支持的风扇模式: {fan_mode}")
            print(f"❌ 不支持的风扇模式: {fan_mode}")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """设置预设模式."""
        if preset_mode in SUPPORTED_PRESET_MODES:
            command = COMMANDS[preset_mode]
            self._current_preset = preset_mode
            
            # 记录日志
            preset_name = "节能" if preset_mode == "ECO" else "离家" if preset_mode == "AWAY" else "睡眠"
            _LOGGER.info(f"🔄 设置预设模式: {preset_name}")
            print(f"🔄 设置预设模式: {preset_name}")
            
            await self._device.send_command(command)
            self.async_write_ha_state()
        else:
            _LOGGER.error(f"不支持的预设模式: {preset_mode}")
            print(f"❌ 不支持的预设模式: {preset_mode}")

    # 新风系统不需要温度控制，移除 async_set_temperature 方法

    async def _handle_device_data(self, data: dict) -> None:
        """处理设备数据更新."""
        try:
            # 根据解析的数据更新状态
            if "hvac_mode" in data:
                mode = data["hvac_mode"]
                if mode == "off":
                    self._hvac_mode = HVACMode.OFF
                    _LOGGER.info("📥 收到模式更新: 关闭")
                    print("📥 收到模式更新: 关闭")
                elif mode == "auto":
                    self._hvac_mode = HVACMode.AUTO
                    _LOGGER.info("📥 收到模式更新: 自动")
                    print("📥 收到模式更新: 自动")
                elif mode == "manual":
                    self._hvac_mode = HVACMode.FAN_ONLY
                    _LOGGER.info("📥 收到模式更新: 手动")
                    print("📥 收到模式更新: 手动")
            
            if "fan_mode" in data:
                fan_mode = data["fan_mode"]
                if fan_mode in SUPPORTED_FAN_MODES:
                    self._fan_mode = fan_mode
                    # 获取中文显示名称
                    fan_mode_name = FAN_MODE_NAMES.get(fan_mode, fan_mode)
                    _LOGGER.info(f"📥 收到风扇模式更新: {fan_mode_name}")
                    print(f"📥 收到风扇模式更新: {fan_mode_name}")
            
            if "preset_mode" in data:
                preset_mode = data["preset_mode"]
                if preset_mode in SUPPORTED_PRESET_MODES:
                    self._current_preset = preset_mode
                    _LOGGER.info(f"📥 收到预设模式更新: {preset_mode}")
                    print(f"📥 收到预设模式更新: {preset_mode}")
            
            # 新风系统不需要温度处理
            
            # 通知Home Assistant状态已更新
            self.async_write_ha_state()
            
        except Exception as e:
            _LOGGER.error(f"处理设备数据时出错: {e}")

    async def async_will_remove_from_hass(self) -> None:
        """实体从Home Assistant移除时调用."""
        self._device.remove_listener(self._handle_device_data) 