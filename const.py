"""MIYA HRV 集成常量."""
from homeassistant.const import Platform
from homeassistant.components.climate import HVACMode

DOMAIN = "miya_hrv"
DEFAULT_PORT = 38

# 平台
PLATFORMS = [Platform.CLIMATE, Platform.SWITCH]

# 设备信息
DEVICE_NAME = "MIYA HRV Fresh Air System"

# 实体标识符前缀
ENTITY_ID_PREFIX = "miya"

# 实体类型标识符
ENTITY_TYPE_CLIMATE = "climate"
ENTITY_TYPE_SWITCH = "switch"



# 配置选项
CONF_HOST = "host"
CONF_PORT = "port"
CONF_NAME = "name"

# 默认值
DEFAULT_NAME = "MIYA HRV"
DEFAULT_HOST = "192.168.1.100"

# 验证
MIN_TEMP = 16.0
MAX_TEMP = 30.0
TEMP_STEP = 0.5

 