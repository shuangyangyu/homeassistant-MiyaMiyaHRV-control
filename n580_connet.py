import asyncio
from tcp_485_lib import create_client
from device_MIYA_HRV.miya_command_analyzer import MiyaCommandAnalyzer

class DataChangeDetector:
    """数据变化检测器"""
    
    def __init__(self):
        self.previous_data = None
        self.is_first_data = True
    
    def detect_changes(self, current_data):
        """
        检测数据变化并返回变化的部分
        
        Args:
            current_data: 当前状态数据字典
            
        Returns:
            dict: 变化的数据字典，如果没有变化返回None
        """
        if self.is_first_data:
            self.previous_data = current_data.copy()
            self.is_first_data = False
            return None
        
        changes = {}
        has_changes = False
        
        # 比较所有字段
        for key in current_data:
            if key not in self.previous_data:
                # 新字段
                changes[key] = {
                    'previous': 'N/A',
                    'current': current_data[key],
                    'type': '新增'
                }
                has_changes = True
            elif self.previous_data[key] != current_data[key]:
                # 字段值发生变化
                changes[key] = {
                    'previous': self.previous_data[key],
                    'current': current_data[key],
                    'type': '变化'
                }
                has_changes = True
        
        # 检查是否有删除的字段
        for key in self.previous_data:
            if key not in current_data:
                changes[key] = {
                    'previous': self.previous_data[key],
                    'current': 'N/A',
                    'type': '删除'
                }
                has_changes = True
        
        # 更新上一次数据
        self.previous_data = current_data.copy()
        
        return changes if has_changes else None
    
    def print_changes(self, changes):
        """
        格式化打印变化信息
        
        Args:
            changes: 变化数据字典
        """
        if not changes:
            return
        
        print("\n" + "="*50)
        print("🔍 检测到数据变化:")
        print("="*50)
        
        for field, change_info in changes.items():
            change_type = change_info['type']
            previous = change_info['previous']
            current = change_info['current']
            
            if change_type == '新增':
                print(f"➕ {field}: {current}")
            elif change_type == '删除':
                print(f"➖ {field}: {previous}")
            elif change_type == '变化':
                print(f"🔄 {field}: {previous} → {current}")
        
        print("="*50 + "\n")

async def main():
    client = create_client("192.168.1.5", 38, "hex")
    change_detector = DataChangeDetector()
    
    if await client.connect():
        # 异步迭代器 - 最简洁优雅的用法
        async for data in client.listen():
            analyzer = MiyaCommandAnalyzer()
            status_data = analyzer.get_status_data(data)
            
            # 检测数据变化
            changes = change_detector.detect_changes(status_data)
            
            # 如果数据发生变化打印出变化部分
            if changes:
                change_detector.print_changes(changes)
            
            print(status_data)
            # 处理数据...

asyncio.run(main())