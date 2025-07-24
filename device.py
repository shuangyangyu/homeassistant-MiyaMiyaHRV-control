"""MIYA HRV 设备类."""
import asyncio
import logging
import sys
import os

_LOGGER = logging.getLogger(__name__)

# 设置库路径
def setup_library_paths():
    """设置库路径，确保能找到自定义库."""
    # 获取当前组件目录（库文件就在这个目录下）
    component_dir = os.path.dirname(os.path.abspath(__file__))
    if component_dir not in sys.path:
        sys.path.insert(0, component_dir)
        _LOGGER.debug(f"添加库路径: {component_dir}")

# 初始化时设置路径
setup_library_paths()


class MiyaHRVDevice:
    """MIYA HRV设备类."""
    
    def __init__(self, host: str, port: int):
        """初始化设备."""
        self.host = host
        self.port = port
        self.client = None
        self._listeners = []
        
    async def connect(self):
        """连接到设备."""
        try:
            print(f"🔌 正在连接到设备 {self.host}:{self.port}...")
            from tcp_485_lib import create_client
            self.client = create_client(self.host, self.port, "hex")
            if await self.client.connect():
                _LOGGER.info(f"✅ 成功连接到MIYA HRV设备 {self.host}:{self.port}")
                print(f"✅ 成功连接到MIYA HRV设备 {self.host}:{self.port}")
                # 启动监听任务
                asyncio.create_task(self._listen_for_data())
                return True
            else:
                _LOGGER.error(f"❌ 无法连接到MIYA HRV设备 {self.host}:{self.port}")
                print(f"❌ 无法连接到MIYA HRV设备 {self.host}:{self.port}")
                return False
        except Exception as e:
            _LOGGER.error(f"连接设备时出错: {e}")
            print(f"❌ 连接设备时出错: {e}")
            return False
    
    async def disconnect(self):
        """断开设备连接."""
        if self.client:
            print(f"🔌 正在断开设备连接 {self.host}:{self.port}...")
            await self.client.disconnect()
            self.client = None
            _LOGGER.info(f"✅ 已断开设备连接 {self.host}:{self.port}")
            print(f"✅ 已断开设备连接 {self.host}:{self.port}")
        else:
            print("ℹ️ 设备未连接，无需断开")
    
    async def send_command(self, command: str):
        """发送命令到设备."""
        if self.client:
            try:
                # 使用send_hex方法发送十六进制命令
                await self.client.send_hex(command)
                _LOGGER.info(f"📤 发送命令: {command}")
                print(f"📤 发送命令: {command}")
            except Exception as e:
                _LOGGER.error(f"发送命令时出错: {e}")
                print(f"❌ 发送命令时出错: {e}")
        else:
            _LOGGER.warning("设备未连接，无法发送命令")
            print("⚠️ 设备未连接，无法发送命令")
    
    async def _listen_for_data(self):
        """监听设备数据."""
        if not self.client:
            return
            
        try:
            async for data in self.client.listen():
                # 打印原始数据
                _LOGGER.info(f"📥 接收到原始数据: {data}")
                print(f"📥 接收到原始数据: {data}")
                
                # 解析数据
                from device_MIYA_HRV.miya_command_analyzer import MiyaCommandAnalyzer
                analyzer = MiyaCommandAnalyzer()
                command_result = analyzer.analyze_command(data)
                
                # 打印解析结果
                _LOGGER.info(f"🔍 解析结果: {command_result}")
                print(f"🔍 解析结果: {command_result}")
                
                # 详细打印解析结果
                if command_result:
                    print("📋 详细数据:")
                    for key, value in command_result.items():
                        print(f"   {key}: {value}")
                
                # 通知监听器
                for listener in self._listeners:
                    try:
                        await listener(command_result)
                    except Exception as e:
                        _LOGGER.error(f"通知监听器时出错: {e}")
                        print(f"❌ 通知监听器时出错: {e}")
                        
        except Exception as e:
            _LOGGER.error(f"监听数据时出错: {e}")
            print(f"❌ 监听数据时出错: {e}")
    
    def add_listener(self, listener):
        """添加数据监听器."""
        self._listeners.append(listener)
    
    def remove_listener(self, listener):
        """移除数据监听器."""
        if listener in self._listeners:
            self._listeners.remove(listener) 