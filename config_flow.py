"""MIYA HRV 配置流程."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .helpers.common_imports import logging, CONF_HOST, CONF_PORT, _LOGGER
from .const import DOMAIN, DEFAULT_PORT
from .helpers import generate_device_id


class MiyaHRVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理MIYA HRV配置流程."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """处理用户输入."""
        errors = {}

        if user_input is not None:
            try:
                # 验证连接
                host = user_input[CONF_HOST]
                port = user_input.get(CONF_PORT, DEFAULT_PORT)
                
                # 创建唯一ID
                await self.async_set_unique_id(generate_device_id(host, port))
                self._abort_if_unique_id_configured()
                
                # 测试连接
                try:
                    from .helpers.tcp_485_lib import create_client
                except ImportError:
                    try:
                        from helpers.tcp_485_lib import create_client
                    except ImportError:
                        from .helpers.tcp_485_lib.tcp_client_lib import create_client
                client = create_client(host, port, "hex")
                if await client.connect():
                    await client.disconnect()
                    
                    return self.async_create_entry(
                        title=f"MIYA HRV ({host}:{port})",
                        data=user_input,
                    )
                else:
                    errors["base"] = "cannot_connect"
                    
            except Exception as ex:
                _LOGGER.error(f"配置错误: {ex}")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
            errors=errors,
        ) 