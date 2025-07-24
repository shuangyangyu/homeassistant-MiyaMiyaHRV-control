"""MIYA HRV 集成常量."""
from homeassistant.const import Platform
from homeassistant.components.climate import HVACMode

DOMAIN = "miya_hrv"
DEFAULT_PORT = 38

# 平台
PLATFORMS = [Platform.CLIMATE, Platform.SWITCH]

# 设备信息
DEVICE_NAME = "MIYA HRV 新风系统"
MANUFACTURER = "MIYA"

# 功能开关
FUNCTION_PURIFICATION = "purification"
FUNCTION_INTERNAL_CIRCULATION = "internal_circulation"
FUNCTION_EXTERNAL_CIRCULATION = "external_circulation"

# 风扇模式中文映射
FAN_MODE_LOW = "FAN_LOW"
FAN_MODE_MEDIUM = "FAN_MEDIUM"
FAN_MODE_HIGH = "FAN_HIGH"

# 风扇模式中文显示名称
FAN_MODE_NAMES = {
    FAN_MODE_LOW: "低",
    FAN_MODE_MEDIUM: "中",
    FAN_MODE_HIGH: "高",
}

# 命令映射 - 使用Home Assistant内置模式
COMMANDS = {
    # 风扇模式 - 使用Home Assistant内置风扇模式
    FAN_MODE_LOW: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 03 03 03 03",
    FAN_MODE_MEDIUM: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 02 02 02 02",
    FAN_MODE_HIGH: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 01 01 01 01",
    
    # HVAC模式 - 使用Home Assistant内置HVACMode
    HVACMode.OFF: "C7 12 01 01 04 04 01 00 01 01 01 01 01 01 00 00 6A 7E",  # 关闭
    HVACMode.AUTO: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 00 00 A5 DB",  # 自动模式
    HVACMode.FAN_ONLY: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 05 05 05 05",  # 手动模式
    
    # 预设模式 - 使用Home Assistant内置预设模式
    "ECO": "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 10 10 10 10",  # 节能模式
    "AWAY": "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 20 20 20 20",  # 离家模式
    "SLEEP": "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 30 30 30 30",  # 睡眠模式
    
    # 功能开关
    FUNCTION_PURIFICATION: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 40 40 40 40",
    FUNCTION_INTERNAL_CIRCULATION: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 50 50 50 50",
    FUNCTION_EXTERNAL_CIRCULATION: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 60 60 60 60",
}

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