'''
通讯层
实现与硬件设备的通信接口，如串口读写、握手、重试机制等。

'''

"""MIYA HRV 设备类."""
from .common_imports import asyncio, logging, _LOGGER

try:
    from .tcp_485_lib import create_client
except ImportError:
    from tcp_485_lib import create_client

class TCP_485_Device:
    """MIYA HRV设备类."""
    
    def __init__(self, host: str, port: int):
        """初始化设备."""
        self.host = host
        self.port = port
        self.client = None
        
    async def connect(self):
        """Connect to the device."""
        try:
            print(f"🔌 正在连接到设备 {self.host}:{self.port}...")
            self.client = create_client(self.host, self.port, "hex")
            if await self.client.connect():
                _LOGGER.info(f"✅ 成功连接到MIYA HRV设备 {self.host}:{self.port}")
                return True
            else:
                _LOGGER.error(f"❌ 无法连接到MIYA HRV设备 {self.host}:{self.port}")
                return False
        except Exception as e:
            _LOGGER.error(f"连接设备时出错: {e}")
            return False
    
    async def disconnect(self):
        """断开设备连接."""
        if self.client:
            await self.client.disconnect()
            self.client = None
            _LOGGER.info(f"已断开设备连接 {self.host}:{self.port}")
        else:
            print(" 设备未连接，无需断开")
    
    async def send_command(self, command: str):
        """Send command to the device."""
        if self.client:
            try:
                # 使用send_hex方法发送十六进制命令
                await self.client.send_hex(command)
                _LOGGER.info(f"发送命令: {command}")
            except Exception as e:
                _LOGGER.error(f"发送命令时出错: {e}")
        else:
            _LOGGER.warning("设备未连接，无法发送命令")

    async def listen_for_data(self):
        """监听设备数据 - 异步迭代器."""
        if not self.client:
            _LOGGER.warning("设备未连接，无法监听数据")
            return
            
        try:
            _LOGGER.info("🎧 开始监听设备数据...")
            async for data in self.client.listen():
                # _LOGGER.info(f"📥 收到原始数据: {data}")
                # 返回数据，让调用者处理
                yield data
                        
        except Exception as e:
            _LOGGER.error(f"监听数据时出错: {e}")
    

    

if __name__ == "__main__":
    async def main():
        device = TCP_485_Device("192.168.1.5", 38)
        
        try:
            # 连接设备
            await device.connect()

            await device.listen_for_data()
            
        except KeyboardInterrupt:
            print("\n用户中断，正在退出...")
        finally:
            # 断开连接
            await device.disconnect()
    
    asyncio.run(main())
    
