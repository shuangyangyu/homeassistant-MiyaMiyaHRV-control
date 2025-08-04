# TCP 通信库

一个通用的Python异步TCP通信库，整合了TCP客户端和数据转换功能。

## 功能特性

- ✅ 异步TCP连接管理
- ✅ 自动重连机制
- ✅ 十六进制与字节数据转换
- ✅ 灵活的数据模式切换
- ✅ 连接统计和监控
- ✅ 支持hex和bytes两种数据模式
- ✅ 完全通用，不绑定特定协议
- ✅ **简洁的异步迭代器API**
- ✅ **TCP保活功能（保持连接稳定）**

## 快速开始

### 🚀 推荐用法（异步迭代器）

```python
import asyncio
from tcp_485_lib import create_client

async def main():
    client = create_client("192.168.1.5", 38, "hex")
    
    if await client.connect():
        # 异步迭代器 - 最简洁优雅的用法
        async for data in client.listen():
            print(f"收到: {data}")
            # 处理数据...

asyncio.run(main())
```

### 传统用法（回调方式）

```python
import asyncio
from tcp_485_lib import create_client

async def main():
    client = create_client("192.168.1.5", 38, "hex")
    
    # 设置数据接收回调
    async def on_data(hex_data: str, raw_data: bytes):
        print(f"收到数据: {hex_data}")
    
    client.set_data_callback(on_data)
    
    if await client.connect():
        await asyncio.sleep(10)  # 监听10秒
        await client.disconnect()

asyncio.run(main())
```

## 初始化参数说明

### create_client() 便捷函数

```python
client = create_client(
    host="192.168.1.5",      # 必需: 设备IP地址
    port=80,                 # 可选: 端口号，默认80
    data_mode="hex",         # 可选: 数据模式，默认"hex"
    tcp_keepalive=True,      # 可选: 启用TCP保活，默认True
    keepalive_interval=30.0  # 可选: TCP保活间隔(秒)，默认30秒
)
```

### Tcp485Client() 完整构造函数

```python
from tcp_485_lib import Tcp485Client

client = Tcp485Client(
    host="192.168.1.100",
    port=8080,
    data_mode="hex",
    tcp_keepalive=True,
    keepalive_interval=30.0
)
```

## 参数详解

### data_mode 数据模式

| 模式 | 说明 | 异步迭代器返回 | 回调函数参数 |
|------|------|-----------|--------------|
| `"hex"` | 十六进制字符串模式 | `str` | `(hex_data: str, raw_data: bytes)` |
| `"bytes"` | 字节数据模式 | `bytes` | `(data: bytes)` |

### TCP保活配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `tcp_keepalive` | 是否启用TCP保活 | `True` |
| `keepalive_interval` | TCP保活间隔(秒) | `30.0` |

## API 方法

### 🎯 异步迭代器（推荐）

```python
# 最简洁的用法
async for data in client.listen():
    print(f"收到: {data}")
    # 可以随时break退出循环
```

### 传统API（保持兼容）

| 方法 | 说明 |
|------|------|
| `client.set_data_callback(func)` | 设置回调函数 |
| `await client.connect()` | 连接服务器 |
| `await client.disconnect()` | 断开连接 |
| `await client.send_hex(hex_str)` | 发送十六进制 |
| `await client.send_bytes(data)` | 发送字节数据 |
| `client.enable_iterator(enabled)` | 启用/禁用迭代器（性能优化） |

### 🔗 TCP保活API

| 方法 | 说明 |
|------|------|
| `client.enable_tcp_keepalive(enabled)` | 启用/禁用TCP保活 |
| `client.set_keepalive_interval(interval)` | 设置TCP保活间隔 |
| `client.get_connection_info()` | 获取连接信息（包含保活状态） |

## 数据转换

```python
from tcp_485_lib import DataConverter

# 十六进制转字节
bytes_data = DataConverter.hex_to_tcp("C7 12 01 00")

# 字节转十六进制
hex_str = DataConverter.tcp_to_hex(bytes_data)

# 格式化显示
formatted = DataConverter.format_tcp_data(bytes_data, "收到数据")
```

## 使用场景

### 1. 数据监听（推荐）

```python
# 最简单优雅的方式
client = create_client("192.168.1.5", 38, "hex")
if await client.connect():
    async for data in client.listen():
        print(f"📥 {data}")
        # 处理数据逻辑...
```

### 2. 发送数据

```python
client = create_client("192.168.1.5", 38, "hex")
if await client.connect():
    # 发送hex数据
    await client.send_hex("C7 12 01 00")
    
    # 发送字节数据
    await client.send_bytes(b'\xC7\x12\x01\x00')
```

### 3. TCP保活配置

```python
# 启用TCP保活（默认）
client = create_client("192.168.1.5", 38, "hex", tcp_keepalive=True, keepalive_interval=30.0)

# 禁用TCP保活
client = create_client("192.168.1.5", 38, "hex", tcp_keepalive=False)

# 运行时控制
client.enable_tcp_keepalive(True)   # 启用
client.set_keepalive_interval(15.0) # 设置15秒间隔
```

### 4. 性能优化（仅回调）

```python
client = create_client("192.168.1.5", 38, "hex")

# 禁用异步迭代器，节省内存（仅使用回调）
client.enable_iterator(False)

async def on_data(hex_data: str, raw_data: bytes):
    print(f"📥 {hex_data}")

client.set_data_callback(on_data)
```

## 运行示例

```bash
# 运行简洁示例
python3 simple_usage.py 1         # 异步迭代器（推荐）
python3 simple_usage.py 2         # 传统回调方式
python3 simple_usage.py 3         # 性能优化回调

# 运行TCP保活演示
python3 tcp_keepalive_demo.py 1   # 基础TCP保活功能
python3 tcp_keepalive_demo.py 2   # 自定义TCP保活配置
python3 tcp_keepalive_demo.py 3   # TCP保活控制
python3 tcp_keepalive_demo.py 4   # TCP保活监控

# 运行演示
python3 demo.py                   # 传统回调方式演示
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `tcp_client_lib.py` | 核心库文件，包含完整功能 |
| `simple_usage.py` | **简洁示例（推荐查看）** |
| `tcp_keepalive_demo.py` | **TCP保活功能演示** |
| `demo.py` | 传统回调方式演示 |

## 错误处理

库会自动处理常见错误：

- 连接失败自动重试（最多5次）
- 网络断开自动重连
- 数据转换异常捕获
- 超时处理
- 队列满时自动清理旧数据
- TCP保活失败自动重连

## 性能优化

```python
# 如果只使用回调方式，可以禁用异步迭代器以节省内存
client.enable_iterator(False)

# 如果不需要TCP保活，可以禁用以节省资源
client.enable_tcp_keepalive(False)
```

## 日志配置

```python
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

# 仅显示错误日志
logging.basicConfig(level=logging.ERROR)
```

## 🎉 主要优势

1. **异步迭代器**: 最简洁优雅的Python异步编程方式
2. **TCP保活**: 自动保持TCP连接稳定，避免网络设备断开
3. **向后兼容**: 保持原有回调API不变
4. **使用简单**: 无需复杂的API学习
5. **功能完整**: 包含连接管理、数据转换、统计监控
6. **性能优异**: 基于asyncio，支持高并发
7. **错误处理**: 完善的错误处理和自动重连机制

## 使用方式对比

| 方式 | 代码量 | 简洁度 | 推荐度 |
|------|--------|--------|--------|
| **异步迭代器** | 3行 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 传统回调 | 6-8行 | ⭐⭐⭐ | ⭐⭐⭐ |

## TCP保活优势

| 特性 | 说明 | 好处 |
|------|------|------|
| **连接稳定** | 定期发送空数据包 | 避免网络设备因空闲断开 |
| **自动重连** | 保活失败时自动重连 | 提高连接可靠性 |
| **可配置** | 支持启用/禁用和间隔设置 | 灵活适应不同网络环境 |
| **不影响数据** | 只发送空包 | 不干扰正常数据传输 |

## 注意事项

1. **数据模式**: 根据需要选择hex或bytes模式
2. **异步使用**: 所有网络操作都是异步的，需要使用await
3. **资源释放**: 程序结束前记得调用disconnect()
4. **性能优化**: 如果只用回调，可以disable迭代器节省内存
5. **TCP保活**: 默认启用，可根据网络环境调整间隔

## 协议扩展示例

异步迭代器让协议扩展非常简单：

```python
async def parse_custom_protocol():
    client = create_client("192.168.1.5", 38, "hex")
    
    if await client.connect():
        async for hex_data in client.listen():
            # 直接处理数据，简洁明了
            if hex_data.startswith("C7 12"):
                device_addr = int(hex_data[6:8], 16)
                print(f"设备地址: {device_addr}")
                # 处理协议数据...
```

## 🌟 最佳实践

```python
import asyncio
from tcp_485_lib import create_client

async def monitor_device():
    """设备监控最佳实践"""
    # 启用TCP保活，确保连接稳定
    client = create_client("192.168.1.5", 38, "hex", tcp_keepalive=True, keepalive_interval=30.0)
    
    if await client.connect():
        print("✅ 开始监听设备数据...")
        
        try:
            async for data in client.listen():
                # 解析和处理数据
                await process_device_data(data)
                
        except KeyboardInterrupt:
            print("🛑 用户停止")
        except Exception as e:
            print(f"❌ 监听出错: {e}")
        finally:
            await client.disconnect()
            print("🔌 已断开连接")

async def process_device_data(data: str):
    """处理设备数据"""
    print(f"📥 {data}")
    # 在这里添加您的数据处理逻辑...

if __name__ == "__main__":
    asyncio.run(monitor_device())
```

## 🔗 TCP保活使用示例

```python
# 基础TCP保活
client = create_client("192.168.1.5", 38, "hex")  # 默认启用

# 自定义TCP保活
client = create_client(
    host="192.168.1.5",
    port=38,
    data_mode="hex",
    tcp_keepalive=True,
    keepalive_interval=15.0  # 15秒间隔
)

# 运行时控制
client.enable_tcp_keepalive(False)  # 禁用
client.set_keepalive_interval(60.0) # 设置60秒间隔

# 监控TCP保活状态
connection_info = client.get_connection_info()
print(f"TCP保活: {connection_info['tcp_keepalive']}")
print(f"保活间隔: {connection_info['keepalive_interval']}s")
print(f"已发送保活包: {connection_info['keepalive_pings']}个")
``` 