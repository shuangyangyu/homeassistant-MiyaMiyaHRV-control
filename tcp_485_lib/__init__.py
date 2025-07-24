"""
TCP 485通信库
============

一个通用的Python异步TCP通信库，整合了TCP客户端和数据转换功能。

主要功能:
- 异步TCP连接管理
- 自动重连机制  
- 十六进制与字节数据转换
- 连接统计和监控
- 支持hex和bytes两种数据模式
- 简洁的异步迭代器API
- TCP保活功能（保持连接稳定）

最简用法:
    >>> from tcp_485_lib import create_client
    >>> client = create_client("192.168.1.5", 38, "hex")
    >>> await client.connect()
    >>> async for data in client.listen():
    ...     print(f"收到: {data}")

TCP保活用法:
    >>> client = create_client("192.168.1.5", 38, "hex", tcp_keepalive=True, keepalive_interval=30)
    >>> await client.connect()
    >>> # 自动发送TCP保活包保持连接稳定
"""

from .tcp_client_lib import (
    Tcp485Client,
    create_client
)
from .tool import (
    DataConverter,
    hex_to_bytes,
    bytes_to_hex,
    format_data
)

__version__ = "1.2.0"
__author__ = "MIIY HRV Project"
__email__ = ""
__description__ = "简洁的TCP 485通信库 - 异步迭代器 + TCP保活"

# 导出的公共API
__all__ = [
    "Tcp485Client",
    "DataConverter", 
    "create_client",
    "hex_to_bytes",
    "bytes_to_hex",
    "format_data",
    "__version__"
] 