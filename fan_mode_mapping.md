# 风扇模式"高 中 低"映射关系详解

## 📍 映射位置分布

### 1. 常量定义 (const.py)
```python
# 第15-17行：定义风扇模式常量
FAN_MODE_HIGH = "高"
FAN_MODE_MEDIUM = "中" 
FAN_MODE_LOW = "低"
```

### 2. 命令映射 (const.py)
```python
# 第35-39行：风扇模式到命令的映射
COMMANDS = {
    # 风扇模式
    FAN_MODE_HIGH: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 01 01 01 01",
    FAN_MODE_MEDIUM: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 02 02 02 02",
    FAN_MODE_LOW: "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 03 03 03 03",
}
```

### 3. 支持模式列表 (climate.py)
```python
# 第32行：定义支持的风扇模式列表
SUPPORTED_FAN_MODES = [FAN_MODE_LOW, FAN_MODE_MEDIUM, FAN_MODE_HIGH]
```

### 4. 实体属性设置 (climate.py)
```python
# 第95行：设置实体的风扇模式属性
self._attr_fan_modes = SUPPORTED_FAN_MODES
```

## 🔄 完整映射流程

### 用户界面显示
```
Home Assistant UI
    ↓
显示: ["低", "中", "高"]  ← 来自 SUPPORTED_FAN_MODES
    ↓
用户选择: "高"
```

### 命令发送流程
```python
# climate.py:async_set_fan_mode() 第165-178行
async def async_set_fan_mode(self, fan_mode: str) -> None:
    """设置风扇模式."""
    if fan_mode in SUPPORTED_FAN_MODES:  # 检查是否支持
        command = COMMANDS[fan_mode]     # 从映射表获取命令
        self._fan_mode = fan_mode        # 更新内部状态
        
        _LOGGER.info(f"🔄 设置风扇模式: {fan_mode}")
        print(f"🔄 设置风扇模式: {fan_mode}")
        await self._device.send_command(command)  # 发送命令
        self.async_write_ha_state()
```

### 具体映射关系
```python
# 用户选择 "高" → 发送命令 "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 01 01 01 01"
# 用户选择 "中" → 发送命令 "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 02 02 02 02"  
# 用户选择 "低" → 发送命令 "C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 03 03 03 03"
```

## 📊 映射表总结

| 用户界面显示 | 内部常量 | 十六进制命令 |
|-------------|----------|-------------|
| 高 | `FAN_MODE_HIGH = "高"` | `C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 01 01 01 01` |
| 中 | `FAN_MODE_MEDIUM = "中"` | `C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 02 02 02 02` |
| 低 | `FAN_MODE_LOW = "低"` | `C7 12 01 02 01 02 04 04 01 00 01 01 01 01 01 01 03 03 03 03` |

## 🔍 关键代码位置

### 1. 常量定义
**文件**: `const.py`  
**位置**: 第15-17行  
**作用**: 定义风扇模式的显示名称

### 2. 命令映射
**文件**: `const.py`  
**位置**: 第35-39行  
**作用**: 将风扇模式映射到具体的十六进制命令

### 3. 支持模式列表
**文件**: `climate.py`  
**位置**: 第32行  
**作用**: 定义Home Assistant支持的风扇模式

### 4. 实体属性设置
**文件**: `climate.py`  
**位置**: 第95行  
**作用**: 设置Climate实体的风扇模式属性

### 5. 命令发送逻辑
**文件**: `climate.py`  
**位置**: 第165-178行  
**作用**: 处理用户设置风扇模式的请求

### 6. 数据接收处理
**文件**: `climate.py`  
**位置**: 第191-230行  
**作用**: 处理设备返回的风扇模式数据

## 🎯 修改建议

### 如果需要修改显示名称
```python
# 在 const.py 中修改
FAN_MODE_HIGH = "高速"
FAN_MODE_MEDIUM = "中速"
FAN_MODE_LOW = "低速"
```

### 如果需要修改命令
```python
# 在 const.py 中修改 COMMANDS 字典
COMMANDS = {
    FAN_MODE_HIGH: "新的十六进制命令",
    FAN_MODE_MEDIUM: "新的十六进制命令", 
    FAN_MODE_LOW: "新的十六进制命令",
}
```

### 如果需要添加新的风扇模式
```python
# 1. 在 const.py 中添加常量
FAN_MODE_TURBO = "超高速"

# 2. 在 COMMANDS 中添加命令
COMMANDS[FAN_MODE_TURBO] = "新的十六进制命令"

# 3. 在 climate.py 中更新支持列表
SUPPORTED_FAN_MODES = [FAN_MODE_LOW, FAN_MODE_MEDIUM, FAN_MODE_HIGH, FAN_MODE_TURBO]
```

## 📋 总结

**"高 中 低"的映射关系分布在以下位置**：

1. **显示名称**: `const.py` 第15-17行
2. **命令映射**: `const.py` 第35-39行  
3. **支持列表**: `climate.py` 第32行
4. **实体属性**: `climate.py` 第95行
5. **发送逻辑**: `climate.py` 第165-178行
6. **接收处理**: `climate.py` 第191-230行

**修改任何映射关系时，需要同时更新对应的位置以保持一致性。** 