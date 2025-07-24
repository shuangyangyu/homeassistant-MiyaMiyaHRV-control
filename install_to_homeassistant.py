#!/usr/bin/env python3
"""
MIYA HRV 组件安装脚本
用于将组件安装到Home Assistant配置目录
"""

import os
import shutil
import sys
from pathlib import Path

def get_homeassistant_config_dir():
    """获取Home Assistant配置目录"""
    # 常见的Home Assistant配置目录
    possible_paths = [
        os.path.expanduser("~/homeassistant"),
        os.path.expanduser("~/.homeassistant"),
        "/config",  # Docker环境
        "/usr/share/hassio/homeassistant",  # Hass.io环境
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 如果找不到，让用户输入
    print("❓ 未找到Home Assistant配置目录")
    print("请手动输入您的Home Assistant配置目录路径:")
    return input("配置目录路径: ").strip()

def install_component(config_dir):
    """安装组件到Home Assistant"""
    print(f"📁 目标配置目录: {config_dir}")
    
    # 创建custom_components目录
    custom_components_dir = os.path.join(config_dir, "custom_components")
    if not os.path.exists(custom_components_dir):
        os.makedirs(custom_components_dir)
        print("✅ 创建 custom_components 目录")
    
    # 创建miya_hrv目录
    miya_hrv_dir = os.path.join(custom_components_dir, "miya_hrv")
    if os.path.exists(miya_hrv_dir):
        shutil.rmtree(miya_hrv_dir)
        print("🗑️  删除旧的 miya_hrv 目录")
    
    os.makedirs(miya_hrv_dir)
    print("✅ 创建 miya_hrv 目录")
    
    # 复制组件文件
    component_files = [
        "__init__.py",
        "const.py", 
        "config_flow.py",
        "climate.py",
        "switch.py",
        "manifest.json"
    ]
    
    for file in component_files:
        if os.path.exists(file):
            shutil.copy2(file, miya_hrv_dir)
            print(f"📄 复制 {file}")
        else:
            print(f"⚠️  文件不存在: {file}")
    
    # 复制translations目录
    if os.path.exists("translations"):
        translations_dest = os.path.join(miya_hrv_dir, "translations")
        shutil.copytree("translations", translations_dest)
        print("📁 复制 translations 目录")
    
    # 复制库文件到配置目录根目录
    libraries = ["tcp_485_lib", "device_MIYA_HRV"]
    for lib in libraries:
        if os.path.exists(lib):
            lib_dest = os.path.join(config_dir, lib)
            if os.path.exists(lib_dest):
                shutil.rmtree(lib_dest)
            shutil.copytree(lib, lib_dest)
            print(f"📚 复制 {lib} 库")
        else:
            print(f"⚠️  库不存在: {lib}")
    
    print("\n🎉 组件安装完成！")
    print("📋 安装的文件:")
    print(f"   - 组件: {miya_hrv_dir}")
    for lib in libraries:
        if os.path.exists(lib):
            print(f"   - 库: {os.path.join(config_dir, lib)}")
    
    print("\n🔄 请重启Home Assistant以加载新组件")
    print("🔍 然后在配置 -> 设备和服务 -> 添加集成中搜索'MIYA HRV'")

def main():
    """主函数"""
    print("🚀 MIYA HRV 组件安装脚本")
    print("=" * 40)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"📂 当前目录: {current_dir}")
    
    # 检查必要文件
    required_files = ["__init__.py", "const.py", "manifest.json"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 缺少必要文件: {missing_files}")
        print("请确保在项目根目录中运行此脚本")
        return
    
    print("✅ 必要文件检查通过")
    
    # 获取Home Assistant配置目录
    config_dir = get_homeassistant_config_dir()
    
    if not os.path.exists(config_dir):
        print(f"❌ 配置目录不存在: {config_dir}")
        return
    
    # 确认安装
    print(f"\n⚠️  即将安装组件到: {config_dir}")
    response = input("是否继续？(y/n): ").strip().lower()
    
    if response != 'y':
        print("❌ 安装已取消")
        return
    
    # 执行安装
    try:
        install_component(config_dir)
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return

if __name__ == "__main__":
    main() 