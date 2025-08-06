# MIYA HRV Fresh Air System Integration for Home Assistant

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/shuangyangyu/homeassistant-MiyaMiyaHRV-control)](https://github.com/shuangyangyu/homeassistant-MiyaMiyaHRV-control/releases)
[![GitHub license](https://img.shields.io/github/license/shuangyangyu/homeassistant-MiyaMiyaHRV-control)](https://github.com/shuangyangyu/homeassistant-MiyaMiyaHRV-control/blob/main/LICENSE)

MIYA HRV 新风系统 Home Assistant 集成组件，支持通过 TCP 连接控制 MIYA HRV 新风系统设备。

## 功能特性

- ✅ **Climate 实体**：支持 HVAC 模式控制（关机、自动、手动）
- ✅ **Switch 实体**：支持各种功能开关控制
  - 负离子功能
  - UV 杀菌功能
  - 睡眠模式
  - 内循环功能
  - 辅助加热功能
  - 旁通功能
- ✅ **实时状态监控**：自动监听设备状态变化
- ✅ **多设备支持**：支持配置多个 MIYA HRV 设备
- ✅ **设备地址配置**：支持在 UI 中配置设备地址
- ✅ **风扇模式控制**：支持多档风速调节

## 安装方法

### 方法一：HACS 安装（推荐）

1. 确保已安装 [HACS](https://hacs.xyz/)
2. 在 HACS 中添加自定义仓库：
   - 仓库：`shuangyangyu/homeassistant-MiyaMiyaHRV-control`
   - 类别：`Integration`
3. 搜索 "MIYA HRV" 并安装
4. 重启 Home Assistant

### 方法二：手动安装

1. 下载此仓库到 `config/custom_components/` 目录
2. 重命名文件夹为 `miya_hrv`
3. 重启 Home Assistant

## 配置方法

1. 在 Home Assistant 中进入 **设置** → **设备与服务** → **集成**
2. 点击 **添加集成**
3. 搜索 **MIYA HRV**
4. 填写配置信息：
   - **主机地址**：设备 IP 地址（如：192.168.1.5）
   - **端口**：设备端口（默认：38）
   - **设备地址**：设备地址（默认：01）

## 支持的实体

### Climate 实体

- **实体ID**：`climate.miya_hrv_climate`
- **功能**：
  - HVAC 模式：关机、自动、手动
  - 风扇模式：低速、中速、高速

### Switch 实体

| 功能 | 实体ID | 描述 |
|------|--------|------|
| 负离子 | `switch.miya_hrv_negative_ion` | 负离子功能开关 |
| UV杀菌 | `switch.miya_hrv_uv_sterilization` | UV杀菌功能开关 |
| 睡眠模式 | `switch.miya_hrv_sleep_mode` | 睡眠模式开关 |
| 内循环 | `switch.miya_hrv_inner_cycle` | 内循环功能开关 |
| 辅助加热 | `switch.miya_hrv_auxiliary_heat` | 辅助加热功能开关 |
| 旁通 | `switch.miya_hrv_bypass` | 旁通功能开关 |

## 技术特性

- **异步通信**：使用异步 TCP 通信，提高性能
- **状态解析**：自动解析设备状态数据
- **错误处理**：完善的错误处理和日志记录
- **模块化设计**：清晰的代码结构，易于维护
- **多语言支持**：支持中英文界面

## 版本历史

### v1.0.0
- 初始版本发布
- 支持基本的 Climate 和 Switch 实体
- 支持实时状态监控
- 支持多设备配置

## 故障排除

### 常见问题

1. **连接失败**
   - 检查设备 IP 地址和端口是否正确
   - 确认网络连接正常
   - 检查防火墙设置

2. **实体状态不更新**
   - 检查设备地址配置
   - 查看日志中的错误信息
   - 确认设备支持的功能

3. **命令发送失败**
   - 检查设备是否在线
   - 确认命令格式正确
   - 查看设备日志

### 日志查看

在 Home Assistant 配置文件中添加：

```yaml
logger:
  default: info
  logs:
    custom_components.miya_hrv: debug
```

## 开发信息

- **作者**：shuangyangyu
- **许可证**：MIT
- **支持版本**：Home Assistant 2023.8+

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。 