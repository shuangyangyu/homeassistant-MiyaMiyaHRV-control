#!/usr/bin/env python3
"""485-TCP通信库 - 通用版本"""

import asyncio
import logging
from typing import Optional, Callable, Union, Dict, Any, AsyncGenerator, Tuple
from asyncio import StreamReader, StreamWriter, Queue
from datetime import datetime
from .tool import DataConverter

_LOGGER = logging.getLogger(__name__)


class Tcp485Client:
    """485-TCP通信客户端库"""
    
    def __init__(self, 
                 host: str, 
                 port: int = 80, 
                 data_mode: str = "hex",
                 tcp_keepalive: bool = True,
                 keepalive_interval: float = 30.0):
        """初始化485-TCP客户端
        
        Args:
            host: 服务器IP地址
            port: 服务器端口 (默认80)
            data_mode: 数据模式 "hex" 或 "bytes" (默认hex)
            tcp_keepalive: 是否启用TCP保活 (默认True)
            keepalive_interval: TCP保活间隔(秒) (默认30秒)
        """
        self.host = host
        self.port = port
        self.data_mode = data_mode.lower()
        
        # TCP保活配置
        self.tcp_keepalive = tcp_keepalive
        self.keepalive_interval = keepalive_interval
        self._keepalive_task: Optional[asyncio.Task] = None
        
        # TCP连接相关
        self.reader: Optional[StreamReader] = None
        self.writer: Optional[StreamWriter] = None
        self.connected = False
        self.lock = asyncio.Lock()
        
        # 回调和任务
        self.data_callback: Optional[Callable] = None
        self.reconnect_task: Optional[asyncio.Task] = None
        self.receive_task: Optional[asyncio.Task] = None
        
        # 异步迭代器支持
        self.data_queue: Queue = Queue(maxsize=100)
        self._enable_iterator = True
        
        # 统计信息
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'keepalive_pings': 0,
            'connection_time': None,
            'last_activity': None
        }
        
        _LOGGER.info(f"初始化TCP客户端: {host}:{port}, 数据模式: {data_mode}, TCP保活: {tcp_keepalive}")
    
    async def connect(self, timeout: float = 10.0) -> bool:
        """连接到服务器"""
        try:
            _LOGGER.debug(f"正在连接到 {self.host}:{self.port}")
            
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=timeout
            )
            
            self.connected = True
            self.stats['connection_time'] = datetime.now()
            self.stats['last_activity'] = datetime.now()
            
            _LOGGER.info(f"成功连接到 {self.host}:{self.port}")
            
            # 启动数据接收任务
            if self.receive_task is None or self.receive_task.done():
                self.receive_task = asyncio.create_task(self._receive_data())
            
            # 启动TCP保活任务
            if self.tcp_keepalive and (self._keepalive_task is None or self._keepalive_task.done()):
                self._keepalive_task = asyncio.create_task(self._tcp_keepalive_loop())
            
            return True
            
        except Exception as e:
            _LOGGER.error(f"连接失败: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """断开连接"""
        self.connected = False
        
        # 取消TCP保活任务
        if self._keepalive_task and not self._keepalive_task.done():
            self._keepalive_task.cancel()
            try:
                await self._keepalive_task
            except asyncio.CancelledError:
                pass
        
        # 取消接收任务
        if self.receive_task and not self.receive_task.done():
            self.receive_task.cancel()
            try:
                await self.receive_task
            except asyncio.CancelledError:
                pass
        
        # 取消重连任务
        if self.reconnect_task and not self.reconnect_task.done():
            self.reconnect_task.cancel()
            try:
                await self.reconnect_task
            except asyncio.CancelledError:
                pass
        
        # 关闭连接
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                _LOGGER.debug(f"关闭连接时出错: {e}")
            finally:
                self.writer = None
                self.reader = None
        
        _LOGGER.info("已断开TCP连接")
    
    async def send_data(self, data: Union[str, bytes]) -> bool:
        """发送数据 - 支持hex字符串或bytes"""
        async with self.lock:
            if not self.connected or not self.writer:
                _LOGGER.error("TCP连接未建立，无法发送数据")
                return False
            
            try:
                # 根据数据类型转换数据
                if isinstance(data, str):
                    tcp_data = DataConverter.hex_to_tcp(data)
                else:
                    tcp_data = data
                
                self.writer.write(tcp_data)
                await self.writer.drain()
                
                # 更新统计
                self.stats['messages_sent'] += 1
                self.stats['bytes_sent'] += len(tcp_data)
                self.stats['last_activity'] = datetime.now()
                
                if self.data_mode == "hex":
                    _LOGGER.debug(f"发送数据: {DataConverter.tcp_to_hex(tcp_data)}")
                else:
                    _LOGGER.debug(f"发送数据: {tcp_data}")
                
                return True
                
            except Exception as e:
                _LOGGER.error(f"发送数据失败: {e}")
                self.connected = False
                asyncio.create_task(self._reconnect())
                return False
    
    async def send_hex(self, hex_string: str) -> bool:
        """发送十六进制字符串"""
        return await self.send_data(hex_string)
    
    async def send_bytes(self, data: bytes) -> bool:
        """发送字节数据"""
        return await self.send_data(data)
    
    async def _tcp_keepalive_loop(self):
        """TCP保活循环 - 发送空数据包保持连接"""
        while self.connected and self.tcp_keepalive:
            try:
                await asyncio.sleep(self.keepalive_interval)
                
                if not self.connected:
                    break
                
                # 发送TCP保活包（空数据）
                try:
                    if self.writer and not self.writer.is_closing():
                        # 发送一个空字节来保持TCP连接活跃
                        self.writer.write(b'')
                        await self.writer.drain()
                        self.stats['keepalive_pings'] += 1
                        _LOGGER.debug(f"TCP保活包已发送 #{self.stats['keepalive_pings']}")
                except Exception as e:
                    _LOGGER.warning(f"TCP保活包发送失败: {e}")
                    # 保活失败可能表示连接已断开
                    self.connected = False
                    asyncio.create_task(self._reconnect())
                    break
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                _LOGGER.error(f"TCP保活循环出错: {e}")
                break
    
    def enable_tcp_keepalive(self, enabled: bool = True):
        """启用或禁用TCP保活
        
        Args:
            enabled: True启用TCP保活，False禁用
        """
        self.tcp_keepalive = enabled
        if not enabled and self._keepalive_task and not self._keepalive_task.done():
            self._keepalive_task.cancel()
    
    def set_keepalive_interval(self, interval: float):
        """设置TCP保活间隔
        
        Args:
            interval: 保活间隔(秒)
        """
        self.keepalive_interval = interval
        _LOGGER.info(f"TCP保活间隔已更新: {interval}s")
    
    async def listen(self) -> AsyncGenerator[Union[str, bytes], None]:
        """异步迭代器监听数据 - 推荐用法
        
        用法:
            async for data in client.listen():
                print(f"收到: {data}")
                # 处理数据...
        """
        while self.connected:
            try:
                if self._enable_iterator:
                    # 从队列获取数据
                    hex_data, raw_data = await asyncio.wait_for(
                        self.data_queue.get(), timeout=1.0
                    )
                    
                    if self.data_mode == "hex":
                        yield hex_data
                    else:
                        yield raw_data
                else:
                    # 如果禁用了迭代器，等待一下再检查
                    await asyncio.sleep(1.0)
                    
            except asyncio.TimeoutError:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                _LOGGER.error(f"监听数据时出错: {e}")
                break
    
    def enable_iterator(self, enabled: bool = True):
        """启用或禁用异步迭代器
        
        Args:
            enabled: True启用迭代器，False禁用（仅回调模式，节省内存）
        """
        self._enable_iterator = enabled
        if not enabled:
            # 清空队列
            while not self.data_queue.empty():
                try:
                    self.data_queue.get_nowait()
                except:
                    break
    
    async def _receive_data(self):
        """持续接收数据的任务"""
        while self.connected and self.reader:
            try:
                data = await self.reader.read(1024)
                if not data:
                    _LOGGER.warning("接收到空数据，连接可能已断开")
                    self.connected = False
                    break
                
                # 更新统计
                self.stats['messages_received'] += 1
                self.stats['bytes_received'] += len(data)
                self.stats['last_activity'] = datetime.now()
                
                hex_data = DataConverter.tcp_to_hex(data)
                
                if self.data_mode == "hex":
                    _LOGGER.debug(f"接收数据: {hex_data}")
                else:
                    _LOGGER.debug(f"接收数据: {data}")
                
                # 如果启用迭代器，添加到队列中
                if self._enable_iterator:
                    try:
                        self.data_queue.put_nowait((hex_data, data))
                    except asyncio.QueueFull:
                        # 队列满时，移除最旧的数据
                        try:
                            self.data_queue.get_nowait()
                            self.data_queue.put_nowait((hex_data, data))
                        except:
                            pass
                
                # 调用数据回调（向后兼容）
                if self.data_callback:
                    try:
                        if self.data_mode == "hex":
                            await self.data_callback(hex_data, data)
                        else:
                            await self.data_callback(data)
                    except Exception as e:
                        _LOGGER.error(f"数据回调处理失败: {e}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                _LOGGER.error(f"接收数据失败: {e}")
                self.connected = False
                break
        
        # 连接断开时尝试重连
        if not self.connected:
            asyncio.create_task(self._reconnect())
    
    async def _reconnect(self):
        """自动重连"""
        if self.reconnect_task and not self.reconnect_task.done():
            return
        
        self.reconnect_task = asyncio.create_task(self._do_reconnect())
    
    async def _do_reconnect(self):
        """执行重连逻辑"""
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            if self.connected:
                return
            
            retry_count += 1
            wait_time = min(retry_count * 2, 30)
            
            _LOGGER.info(f"尝试重连 ({retry_count}/{max_retries})，等待 {wait_time} 秒...")
            await asyncio.sleep(wait_time)
            
            if await self.connect():
                _LOGGER.info("重连成功")
                return
        
        _LOGGER.error(f"重连失败，已达到最大重试次数 ({max_retries})")
    
    def set_data_callback(self, callback: Callable):
        """设置数据接收回调函数（向后兼容）"""
        self.data_callback = callback
    
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        return {
            'host': self.host,
            'port': self.port,
            'data_mode': self.data_mode,
            'connected': self.connected,
            'tcp_keepalive': self.tcp_keepalive,
            'keepalive_interval': self.keepalive_interval,
            'keepalive_pings': self.stats['keepalive_pings'],
            'stats': self.stats.copy()
        }
    
    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.connected and self.writer is not None
    
    def __repr__(self) -> str:
        status = "已连接" if self.is_connected else "未连接"
        keepalive = "保活" if self.tcp_keepalive else "无保活"
        return f"Tcp485Client({self.host}:{self.port}, {self.data_mode}, {status}, {keepalive})"


# 便捷函数
def create_client(host: str, 
                 port: int = 80, 
                 data_mode: str = "hex",
                 tcp_keepalive: bool = True,
                 keepalive_interval: float = 30.0) -> Tcp485Client:
    """创建TCP客户端的便捷函数
    
    Args:
        host: IP地址
        port: 端口号 (默认80)
        data_mode: 数据模式 "hex" 或 "bytes" (默认hex)
        tcp_keepalive: 是否启用TCP保活 (默认True)
        keepalive_interval: TCP保活间隔(秒) (默认30秒)
    """
    return Tcp485Client(host, port, data_mode, tcp_keepalive, keepalive_interval) 