"""MIYA HRV Fresh Air System Integration."""
from .helpers.common_imports import logging, ConfigEntry, HomeAssistant, _LOGGER

from .const import DOMAIN, PLATFORMS
from .helpers.ha_utils import MiyaHRVManager


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置MIYA HRV配置条目."""
    # 创建管理器
    manager = MiyaHRVManager(hass, entry.entry_id)
    
    # 设置组件
    await manager.setup(entry)
    
    # 设置平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # 注册清理回调
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """重新加载MIYA HRV配置条目."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载MIYA HRV配置条目."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        device_data = hass.data[DOMAIN].pop(entry.entry_id)
        if 'manager' in device_data:
            await device_data['manager'].cleanup()
        _LOGGER.info("✅ 设备连接已断开")
    
    return unload_ok
