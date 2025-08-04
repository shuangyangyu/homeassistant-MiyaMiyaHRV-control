"""
通用导入模块
===========

集中管理项目中常用的导入，减少重复导入。
"""

# 标准库导入
import logging
import asyncio
from typing import Any, List, Optional, Dict, Union

# Home Assistant 核心导入
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST, 
    CONF_PORT, 
    CONF_NAME,
    ATTR_TEMPERATURE,
    UnitOfTemperature
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

# Home Assistant 组件导入
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.components.switch import SwitchEntity

# 创建日志记录器
_LOGGER = logging.getLogger(__name__) 