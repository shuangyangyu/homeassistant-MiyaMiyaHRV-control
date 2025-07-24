"""MIYA HRV 新风系统集成."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import DOMAIN, DEFAULT_PORT, PLATFORMS
from .device import MiyaHRVDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置MIYA HRV配置条目."""
    hass.data.setdefault(DOMAIN, {})
    
    # 创建设备实例
    device = MiyaHRVDevice(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT)
    )
    
    # 存储设备实例
    hass.data[DOMAIN][entry.entry_id] = device
    
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
        device = hass.data[DOMAIN].pop(entry.entry_id)
        await device.disconnect()
    
    return unload_ok


 