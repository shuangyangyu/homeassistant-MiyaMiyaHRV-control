"""MIYA HRV Climate 平台."""
from .helpers.common_imports import (
    logging, Any, List, Optional,
    ClimateEntity, ClimateEntityFeature, HVACMode,
    ConfigEntry, ATTR_TEMPERATURE, CONF_NAME, UnitOfTemperature,
    HomeAssistant, AddEntitiesCallback, ConfigType, DiscoveryInfoType,
    _LOGGER
)

from .const import (
    DOMAIN,
    DEVICE_NAME,
    ENTITY_TYPE_CLIMATE,
)

# 导入辅助函数
from .helpers.ha_utils import get_device_status, send_device_command, get_commands, generate_entity_id

# 支持的模式
SUPPORTED_FAN_MODES = ["low", "medium", "high"]
SUPPORTED_HVAC_MODES = [HVACMode.OFF, HVACMode.AUTO, HVACMode.FAN_ONLY]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置MIYA HRV Climate平台."""
    device_data = hass.data[DOMAIN][config_entry.entry_id]
    device = device_data['device']
    
    # 创建Climate实体
    climate_entity = MiyaHRVClimate(
        device=device,
        name=DEVICE_NAME,
        unique_id=generate_entity_id(config_entry.entry_id, ENTITY_TYPE_CLIMATE),
        hass=hass,
        entry_id=config_entry.entry_id,
    )
    
    # 注册实体到管理器
    device_data = hass.data[DOMAIN][config_entry.entry_id]
    if 'manager' in device_data:
        device_data['manager'].register_entity(climate_entity.unique_id, climate_entity)
    else:
        # 兼容旧版本
        device_data['entities'][climate_entity.unique_id] = climate_entity
    
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
        self._fan_mode = "medium"
        self._current_status = {}  # 存储当前状态数据
        
        
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
        # 优先使用本地状态数据，如果没有则从全局获取
        status = self._current_status if self._current_status else get_device_status(self._hass, self._entry_id)
        mode = status.get('mode', 'off')
        
        # 映射到 HA 的 HVAC 模式
        mode_map = {
            "off": HVACMode.OFF,
            "auto": HVACMode.AUTO,
            "manual": HVACMode.FAN_ONLY  # 手动模式映射为仅风扇
        }
        
        return mode_map.get(mode, HVACMode.OFF)
    
    @property
    def hvac_mode_display(self) -> str:
        """返回HVAC模式的显示名称."""
        return str(self._hvac_mode)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """返回额外的状态属性."""
        return {
            "hvac_mode_display": self.hvac_mode_display,
            "fan_mode_display": "LOW" if self._fan_mode == "low" else "MEDIUM" if self._fan_mode == "medium" else "HIGH"
        }

    @property
    def fan_mode(self) -> str:
        """返回当前风扇模式."""
        # 优先使用本地状态数据，如果没有则从全局获取
        status = self._current_status if self._current_status else get_device_status(self._hass, self._entry_id)
        fan_mode = status.get('fan_mode', 'level_2')
        
        # 映射到 HA 的风扇模式
        fan_map = {
            "level_1": "low",
            "level_2": "medium",
            "level_3": "high",
            "level_4": "high",
            "level_5": "high"
        }
        
        return fan_map.get(fan_mode, "medium")

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
        
        # 直接使用英文命令键
        command_map = {
            HVACMode.OFF: "power_off",
            HVACMode.AUTO: "power_auto",
            HVACMode.FAN_ONLY: "power_auto"  # 手动模式暂时使用自动模式
        }
        
        command_name = command_map.get(hvac_mode)
        if command_name:
            success = await send_device_command(self._hass, self._entry_id, command_name)
            if success:
                self._hvac_mode = hvac_mode
                # 记录日志
                _LOGGER.info(f"设置模式: {hvac_mode}")
                self.async_write_ha_state()
        else:
            _LOGGER.error(f"未找到模式 {hvac_mode} 对应的命令")

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """设置风扇模式."""
        if fan_mode in SUPPORTED_FAN_MODES:
            # 直接使用英文命令键
            command_map = {
                "low": "fan_mode_level_1",
                "medium": "fan_mode_level_2",
                "high": "fan_mode_level_3"
            }
            
            command_name = command_map.get(fan_mode)
            if command_name:
                success = await send_device_command(self._hass, self._entry_id, command_name)
                if success:
                    self._fan_mode = fan_mode
                    # 记录日志
                    mode_name = "LOW" if fan_mode == "low" else "MEDIUM" if fan_mode == "medium" else "HIGH"
                    _LOGGER.info(f"设置风扇模式: {mode_name}")
                    self.async_write_ha_state()
            else:
                _LOGGER.error(f"未找到风扇模式 {fan_mode} 对应的命令")
        else:
            _LOGGER.error(f"不支持的风扇模式: {fan_mode}")



    def update_status(self, status_data: dict):
        """更新实体状态数据."""
        self._current_status = status_data
        # 检查实体是否已经完全初始化
        if hasattr(self, 'hass') and self.hass is not None:
            self.async_write_ha_state()
            _LOGGER.debug(f"📊 Climate 状态已更新: {status_data}")
        else:
            _LOGGER.debug(f"📊 Climate 实体尚未完全初始化，仅更新本地状态")


    async def async_will_remove_from_hass(self) -> None:
        """实体从Home Assistant移除时调用."""
