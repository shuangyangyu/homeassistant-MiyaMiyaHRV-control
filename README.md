# MIYA HRV 新风系统 Home Assistant 集成

这是一个用于MIYA HRV新风系统的Home Assistant自定义集成组件。

## 项目结构

```
MIIY_HRV/ (开发目录)
├── __init__.py              # 主初始化文件
├── const.py                 # 常量定义
├── config_flow.py           # 配置流程
├── climate.py               # Climate平台
├── switch.py                # Switch平台
├── manifest.json            # 组件清单
├── README.md                # 说明文档
├── example_configuration.yaml # 配置示例
├── translations/            # 多语言支持
├── tcp_485_lib/             # TCP通信库
├── device_MIYA_HRV/         # 设备命令解析库
├── test_miya_hrv.py         # 测试脚本
├── test_installation.py     # 安装测试脚本
└── test_symlink.py          # 符号链接测试脚本

Home Assistant 配置目录结构:
/config/
├── custom_components/
│   └── MIIY_HRV/            # 组件目录（包含所有库文件）
│       ├── 组件文件
│       ├── tcp_485_lib/     # TCP通信库
│       └── device_MIYA_HRV/ # 设备命令解析库
```

## 功能特性

### Climate 平台功能
- **风扇模式控制**：高、中、低三档风速调节
- **运行模式**：开启/关闭新风系统
- **场景模式**：睡眠模式、假期模式、会客模式
- **温度控制**：支持温度设定和显示

### Switch 平台功能
- **净化功能**：开启/关闭空气净化
- **内循环**：开启/关闭内循环模式
- **外循环**：开启/关闭外循环模式

## 安装方法

### 方法一：直接开发（推荐）
1. 将整个 `MIIY_HRV/` 项目文件夹直接放在您的Home Assistant配置目录的 `custom_components/` 中
2. 库文件 `tcp_485_lib/` 和 `device_MIYA_HRV/` 已经包含在项目目录中
3. 重启Home Assistant
4. 在配置 -> 设备和服务 -> 添加集成中搜索"MIYA HRV"

**优势**：直接在Home Assistant的插件目录中开发，修改立即生效，无需额外配置。

### 方法二：自动安装（推荐）
使用提供的安装脚本自动安装：

```bash
python3 install_to_homeassistant.py
```

脚本会自动：
- 检测Home Assistant配置目录
- 创建必要的目录结构
- 复制组件文件和库文件
- 提供安装确认

### 方法三：手动安装
1. 在您的Home Assistant配置目录中创建 `custom_components/miya_hrv/` 文件夹
2. 将以下文件复制到 `custom_components/miya_hrv/` 中：
   - `__init__.py`
   - `const.py`
   - `config_flow.py`
   - `climate.py`
   - `switch.py`
   - `manifest.json`
   - `translations/` 文件夹
3. 确保 `tcp_485_lib/` 和 `device_MIYA_HRV/` 库文件在Home Assistant配置目录中
4. 重启Home Assistant
5. 在配置 -> 设备和服务 -> 添加集成中搜索"MIYA HRV"

### 方法四：HACS安装
1. 确保已安装HACS
2. 在HACS中添加自定义仓库
3. 搜索并安装此集成

## 配置

### 基本配置
1. 在Home Assistant中，进入 **配置** -> **设备和服务** -> **集成**
2. 点击右下角的 **添加集成** 按钮
3. 搜索 **MIYA HRV**
4. 输入设备信息：
   - **主机地址**：设备的IP地址（默认：192.168.1.5）
   - **端口**：设备端口（默认：38）

### 高级配置
可以通过 `configuration.yaml` 进行高级配置：

```yaml
miya_hrv:
  host: 192.168.1.5
  port: 38
```

## 使用方法

### Climate 控制
- 在Home Assistant的概览页面中，您会看到MIYA HRV Climate实体
- 可以控制：
  - 系统开关
  - 风扇速度（高/中/低）
  - 场景模式（睡眠/假期/会客）
  - 温度设定

### Switch 控制
- 在概览页面中，您会看到三个开关实体：
  - **净化功能**：控制空气净化功能
  - **内循环**：控制内循环模式
  - **外循环**：控制外循环模式

### 自动化示例

#### 自动开启净化功能
```yaml
automation:
  - alias: "空气质量差时开启净化"
    trigger:
      platform: numeric_state
      entity_id: sensor.air_quality
      above: 100
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.miya_hrv_新风系统_净化功能
```

#### 睡眠模式自动化
```yaml
automation:
  - alias: "晚上10点开启睡眠模式"
    trigger:
      platform: time
      at: "22:00:00"
    action:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.miya_hrv_新风系统
        data:
          preset_mode: sleep
```

## 故障排除

### 连接问题
1. 检查设备IP地址和端口是否正确
2. 确保设备在同一个网络中
3. 检查防火墙设置

### 命令不响应
1. 检查网络连接
2. 查看Home Assistant日志中的错误信息
3. 确认设备支持的命令格式

## 库依赖

### 必需的本地库
本组件依赖于以下本地库，这些库必须存在于Home Assistant配置目录中：

#### 1. tcp_485_lib
- **位置**: `config_dir/tcp_485_lib/`
- **功能**: TCP通信库，提供异步TCP连接和数据传输
- **主要类**: `Tcp485Client`, `create_client`
- **用法**: `from tcp_485_lib import create_client`

#### 2. device_MIYA_HRV
- **位置**: `config_dir/device_MIYA_HRV/`
- **功能**: 设备命令解析库，解析MIYA HRV设备的数据
- **主要类**: `MiyaCommandAnalyzer`
- **用法**: `from device_MIYA_HRV.miya_command_analyzer import MiyaCommandAnalyzer`

### 目录结构要求
```
config_dir/
├── custom_components/
│   └── miya_hrv/          # 本组件
├── tcp_485_lib/           # TCP通信库
│   ├── __init__.py
│   ├── tcp_client_lib.py
│   └── tool.py
└── device_MIYA_HRV/       # 设备解析库
    ├── __init__.py
    ├── miya_command_analyzer.py
    └── crc16_utils.py
```

## 开发信息

### 技术架构
- 使用 `tcp_485_lib` 库进行TCP通信
- 使用 `device_MIYA_HRV.miya_command_analyzer` 解析设备数据
- 基于Home Assistant的Climate和Switch平台
- **动态命令计算**：在初始化时自动计算设备命令，包含CRC校验
- **智能命令映射**：支持计算后的命令和默认命令的自动切换

### 命令格式
所有命令都使用十六进制格式，通过TCP发送到设备。

#### 动态命令计算
系统在初始化时会自动执行 `command_calculate.py` 来计算完整的设备命令：

1. **原始命令**：从 `config_input.py` 读取基础命令
2. **设备地址**：自动设置设备地址（默认：01）
3. **CRC校验**：自动计算并添加CRC16校验码
4. **命令映射**：将计算后的命令映射到Home Assistant实体

#### 命令优先级
1. **计算后的命令**：优先使用初始化时计算的命令（包含CRC校验）
2. **默认命令**：如果计算失败，使用 `const.py` 中的默认命令
3. **错误处理**：如果命令未找到，记录错误日志并跳过操作

### 日志
启用调试日志以查看详细信息：
```yaml
logger:
  default: info
  logs:
    custom_components.miya_hrv: debug
```

## 开发和调试

### 本地测试
项目包含多个测试脚本，可以用于验证不同功能：

#### 命令计算测试
```bash
python3 test_command_calculation.py
```
验证命令计算和CRC校验功能。

#### 命令映射测试
```bash
python3 test_command_mapping.py
```
验证命令映射逻辑和查找功能。

#### 基本功能测试
```bash
python3 test_miya_hrv.py
```
验证库引用和基本功能。

### 调试模式
启用调试日志以查看详细信息：

```yaml
logger:
  default: info
  logs:
    custom_components.miya_hrv: debug
```

### 项目结构说明
- **根目录结构**：所有组件文件直接在项目根目录，便于开发和调试
- **库引用**：自动设置Python路径，确保能找到 `tcp_485_lib` 和 `device_MIYA_HRV` 库
- **模块化设计**：组件、库、测试脚本分离，便于维护

## 支持

如果您遇到问题或有建议，请：
1. 查看Home Assistant日志
2. 检查设备连接状态
3. 确认配置参数正确
4. 运行测试脚本验证库引用

## 许可证

本项目采用MIT许可证。 