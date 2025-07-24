# 多设备TCP连接架构

## 🔄 当前架构分析

### 单设备架构 (当前实现)
```
Home Assistant
    ↓
配置条目 (ConfigEntry)
    ↓
一个MiyaHRVDevice实例
    ↓
一个TCP连接
    ↓
一个Climate实体
```

### 多设备架构 (需要实现)
```
Home Assistant
    ↓
多个配置条目 (ConfigEntry1, ConfigEntry2, ...)
    ↓
多个MiyaHRVDevice实例
    ↓
多个TCP连接
    ↓
多个Climate实体
```

## 📊 TCP连接数量

### 连接数量 = 设备数量
- **1个设备** → **1个TCP连接**
- **3个设备** → **3个TCP连接**
- **N个设备** → **N个TCP连接**

### 每个设备独立连接
```python
# 设备1: 192.168.1.100:8080
device1 = MiyaHRVDevice(host="192.168.1.100", port=8080)
await device1.connect()  # TCP连接1

# 设备2: 192.168.1.101:8080  
device2 = MiyaHRVDevice(host="192.168.1.101", port=8080)
await device2.connect()  # TCP连接2

# 设备3: 192.168.1.102:8080
device3 = MiyaHRVDevice(host="192.168.1.102", port=8080)
await device3.connect()  # TCP连接3
```

## 🏗️ Home Assistant多设备支持

### 当前架构已经支持多设备！

**关键点**: Home Assistant的配置条目系统天然支持多设备：

```python
# __init__.py 中的关键代码
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """每个配置条目都会调用这个函数"""
    
    # 为每个设备创建独立的设备实例
    device = MiyaHRVDevice(
        host=entry.data[CONF_HOST],  # 每个设备的IP不同
        port=entry.data.get(CONF_PORT, DEFAULT_PORT)
    )
    
    # 每个设备存储在不同的entry_id下
    hass.data[DOMAIN][entry.entry_id] = device  # 独立存储
```

### 多设备配置流程
```
用户添加第一个设备
    ↓
创建ConfigEntry1 (entry_id: "abc123")
    ↓
调用async_setup_entry(entry1)
    ↓
创建device1实例 → TCP连接1
    ↓
创建climate_entity1

用户添加第二个设备  
    ↓
创建ConfigEntry2 (entry_id: "def456")
    ↓
调用async_setup_entry(entry2)
    ↓
创建device2实例 → TCP连接2
    ↓
创建climate_entity2
```

## 📁 数据结构

### hass.data[DOMAIN] 结构
```python
hass.data[DOMAIN] = {
    "abc123": MiyaHRVDevice(host="192.168.1.100"),  # 设备1
    "def456": MiyaHRVDevice(host="192.168.1.101"),  # 设备2
    "ghi789": MiyaHRVDevice(host="192.168.1.102"),  # 设备3
}
```

### 实体命名
```python
# 设备1的实体
climate_entity1 = MiyaHRVClimate(
    device=device1,
    name="MIYA HRV 客厅",  # 用户可自定义名称
    unique_id="abc123_climate"
)

# 设备2的实体
climate_entity2 = MiyaHRVClimate(
    device=device2, 
    name="MIYA HRV 卧室",  # 用户可自定义名称
    unique_id="def456_climate"
)
```

## 🔧 配置界面支持

### config_flow.py 需要支持多设备
```python
class MiyaHRVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """配置流程支持多设备."""
    
    async def async_step_user(self, user_input=None):
        """用户输入设备信息."""
        if user_input is not None:
            # 检查是否已存在相同IP的设备
            existing_entries = self.hass.config_entries.async_entries(DOMAIN)
            for entry in existing_entries:
                if entry.data[CONF_HOST] == user_input[CONF_HOST]:
                    return self.async_abort(reason="already_configured")
            
            # 创建新的配置条目
            return self.async_create_entry(
                title=f"MIYA HRV {user_input[CONF_HOST]}",  # 显示IP地址
                data=user_input
            )
```

## 📊 资源使用分析

### 内存使用
- **每个设备**: ~1-2MB (TCP连接 + 监听任务)
- **3个设备**: ~3-6MB
- **10个设备**: ~10-20MB

### 网络连接
- **每个设备**: 1个TCP连接 + 1个监听任务
- **连接池**: 每个设备独立管理
- **错误隔离**: 一个设备故障不影响其他设备

### CPU使用
- **监听任务**: 每个设备1个异步任务
- **数据解析**: 每个设备独立解析
- **UI更新**: 每个实体独立更新

## 🚨 错误处理

### 连接失败隔离
```python
# 设备1连接失败，不影响设备2
try:
    await device1.connect()  # 失败
except Exception:
    _LOGGER.error("设备1连接失败")
    # 设备1的实体显示为不可用状态

await device2.connect()  # 成功
# 设备2正常工作
```

### 重连机制
```python
# 每个设备独立重连
async def _reconnect_device(self):
    """设备重连机制."""
    while True:
        try:
            await self.connect()
            break
        except Exception:
            await asyncio.sleep(30)  # 30秒后重试
```

## 📋 使用建议

### 设备命名
- **建议**: 使用有意义的名称 (如"客厅新风"、"卧室新风")
- **避免**: 使用相同名称造成混淆

### 网络配置
- **IP地址**: 确保每个设备有唯一IP
- **端口**: 可以使用相同端口 (不同IP)
- **防火墙**: 确保所有设备端口可访问

### 监控建议
- **日志**: 每个设备独立日志记录
- **状态**: 监控每个设备的连接状态
- **性能**: 监控多设备时的系统性能

## 🎯 总结

**当前架构已经支持多设备！**

- ✅ **每个设备独立TCP连接**
- ✅ **每个设备独立配置条目**
- ✅ **每个设备独立实体**
- ✅ **错误隔离和独立重连**
- ✅ **资源使用合理**

**只需要在配置界面添加设备名称输入，让用户能够区分不同设备即可。** 