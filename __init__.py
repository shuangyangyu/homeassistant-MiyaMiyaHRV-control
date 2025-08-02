"""MIYA HRV Fresh Air System Integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import DOMAIN, DEFAULT_PORT, PLATFORMS
from .device import MiyaHRVDevice

_LOGGER = logging.getLogger(__name__)

CALCULATED_COMMANDS = None

def calculate_commands():
    """计算设备命令，包含CRC校验."""
    global CALCULATED_COMMANDS
    try:
        from .command_calculate import cmd_calculate2
        from .config_input import command_set_dict
        
        device_addr = "01"
        CALCULATED_COMMANDS = cmd_calculate2(command_set_dict, device_addr)
        
        _LOGGER.info("命令计算完成")

        
        return CALCULATED_COMMANDS
    except Exception as e:
        _LOGGER.error(f"命令计算失败: {e}")
        return None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置MIYA HRV配置条目."""
    hass.data.setdefault(DOMAIN, {})
    
    # 在初始化时计算命令
    if CALCULATED_COMMANDS is None:
        calculate_commands()
    
    # 创建设备实例
    device = MiyaHRVDevice(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT)
    )
    
    # 存储设备实例和计算后的命令
    hass.data[DOMAIN][entry.entry_id] = {
        'device': device,
        'commands': CALCULATED_COMMANDS
    }
    
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
        await device_data['device'].disconnect()
    
    return unload_ok
