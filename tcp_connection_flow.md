# TCP连接运行逻辑详解

## 🔄 完整运行流程

### 1. Home Assistant启动阶段
```
Home Assistant启动
    ↓
扫描custom_components目录
    ↓
发现MIIY_HRV组件
    ↓
加载manifest.json
    ↓
注册组件到Home Assistant
```

### 2. 用户配置阶段
```
用户在Home Assistant中添加集成
    ↓
调用config_flow.py进行配置
    ↓
用户输入设备IP和端口
    ↓
创建配置条目(ConfigEntry)
    ↓
保存到Home Assistant配置中
```

### 3. 组件初始化阶段 (async_setup_entry)
```
配置条目被加载
    ↓
__init__.py:async_setup_entry()被调用
    ↓
创建MiyaHRVDevice实例 (未连接)
    ↓
存储设备实例到hass.data[DOMAIN]
    ↓
转发配置条目给各个平台
```

### 4. 平台设置阶段
```
Climate平台:async_setup_entry()被调用
    ↓
从hass.data[DOMAIN]获取设备实例
    ↓
调用device.connect() ← 🎯 TCP连接开始
    ↓
创建Climate实体
    ↓
实体添加到Home Assistant
```

### 5. TCP连接详细过程
```
device.connect()被调用
    ↓
导入tcp_485_lib库
    ↓
创建TCP客户端实例
    ↓
调用client.connect()建立TCP连接
    ↓
连接成功 → 启动数据监听任务
    ↓
连接失败 → 记录错误日志
```

### 6. 数据监听阶段
```
连接成功后
    ↓
启动_listen_for_data()异步任务
    ↓
持续监听设备数据
    ↓
解析接收到的数据
    ↓
通知所有监听器(实体)
```

### 7. 实体操作阶段
```
用户在Home Assistant中操作实体
    ↓
调用实体的async_set_*方法
    ↓
实体调用device.send_command()
    ↓
通过TCP发送命令到设备
    ↓
设备响应数据
    ↓
_listen_for_data()接收并解析
    ↓
通知实体更新状态
```

### 8. 组件卸载阶段
```
用户删除集成或Home Assistant重启
    ↓
调用async_unload_entry()
    ↓
卸载所有平台
    ↓
调用device.disconnect()
    ↓
断开TCP连接
    ↓
清理资源
```

## ⏰ 关键时机点

### 🎯 TCP连接时机
- **时机**: Climate平台设置时
- **位置**: `climate.py:async_setup_entry()` 第58行
- **代码**: `await device.connect()`
- **条件**: 配置条目存在且有效

### 🔌 连接建立过程
```python
# 在device.py中
async def connect(self):
    # 1. 导入TCP库
    from tcp_485_lib import create_client
    
    # 2. 创建客户端
    self.client = create_client(self.host, self.port, "hex")
    
    # 3. 建立连接
    if await self.client.connect():
        # 4. 启动监听任务
        asyncio.create_task(self._listen_for_data())
        return True
```

### 📡 数据监听启动
- **时机**: TCP连接成功后立即启动
- **方式**: 异步任务(asyncio.create_task)
- **功能**: 持续监听设备数据
- **生命周期**: 直到设备断开连接

## 🚨 错误处理

### 连接失败
- 记录错误日志
- 返回False
- 实体仍会创建，但无法与设备通信

### 连接断开
- 自动重连机制(如果库支持)
- 记录断开日志
- 清理监听任务

## 📋 总结

**TCP连接时机**: 在Climate平台设置时，即用户配置完集成后，Home Assistant加载组件时自动建立TCP连接。

**连接生命周期**: 
- 建立: 组件初始化时
- 维持: 整个组件运行期间
- 断开: 组件卸载时

**数据流**: 双向通信
- 发送: 用户操作 → 实体 → 设备 → TCP发送
- 接收: 设备 → TCP接收 → 解析 → 实体更新 