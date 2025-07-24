import asyncio
from tcp_485_lib import create_client

async def main():
    client=create_client("192.168.1.5", 38, "hex")
    if await client.connect():
        print("连接成功")
        async for data in client.listen():
            #引入miya_command_analyzer.py
            from device_MIYA_HRV.miya_command_analyzer import MiyaCommandAnalyzer
            analyzer = MiyaCommandAnalyzer()
            command_result = analyzer.analyze_command(data)
            print(command_result)

if __name__ == "__main__":
    asyncio.run(main())