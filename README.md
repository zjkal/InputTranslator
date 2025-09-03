# InputTranslator

一个极简的Windows桌面翻译工具，通过全局快捷键实现中文到英文的即时翻译和文本替换功能。

## 功能特点

- 🚀 **极简设计**: 专注核心翻译功能，界面简洁
- ⌨️ **全局快捷键**: 在任意应用中快速触发翻译
- 🔄 **即时替换**: 翻译后自动替换原文本
- 🤖 **本地AI**: 使用本地Ollama服务，保护隐私
- 🎯 **智能识别**: 自动识别中文文本进行翻译
- 📱 **系统托盘**: 后台运行，不占用桌面空间

## 系统要求

- Windows 10/11
- Python 3.7+
- 本地Ollama服务
- 支持的AI模型（推荐：qwen2.5:7b）

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 安装和配置Ollama

1. 下载并安装Ollama：https://ollama.ai/
2. 安装推荐的模型：
   ```bash
   ollama pull qwen2.5:7b
   ```
3. 启动Ollama服务（通常会自动启动）

### 3. 运行程序

```bash
python main.py
```

## 构建可执行文件

如果您想将程序打包成独立的exe文件，可以使用提供的构建脚本：

### 构建步骤

1. **安装构建依赖**:
   ```bash
   pip install pyinstaller
   ```

2. **运行构建脚本**:
   ```bash
   python build.py
   ```

3. **获取exe文件**:
   构建完成后，在 `dist/` 目录中会生成 `InputTranslator.exe` 文件

### 构建特性

- 🎯 **单文件打包**: 生成单个exe文件，无需额外依赖
- 🚀 **自动依赖**: 自动包含所有必要的Python库和模块
- 🎨 **无控制台**: 后台运行，不显示控制台窗口
- 📦 **完整功能**: 包含所有原程序功能
- 🔧 **智能构建**: 自动检测和安装PyInstaller

### 使用打包后的程序

1. 将 `InputTranslator.exe` 复制到任意位置
2. 确保本地Ollama服务正在运行
3. 双击运行 `InputTranslator.exe`
4. 程序将在系统托盘中运行
5. 使用 `Ctrl+Shift+T` 快捷键进行翻译

> **注意**: 打包后的exe文件可以在没有Python环境的Windows系统上独立运行

## 使用方法

### 基本使用

1. **启动程序**: 运行 `python main.py`
2. **选择文本**: 在任意应用中选中需要翻译的中文文本
3. **触发翻译**: 按下快捷键 `Ctrl+Shift+T`
4. **自动替换**: 程序会自动将中文翻译成英文并替换原文本

### 系统托盘操作

程序启动后会在系统托盘显示图标，右键点击可以：

- **设置**: 打开设置窗口
- **状态**: 查看当前运行状态
- **测试翻译**: 测试翻译功能
- **退出**: 退出程序

### 设置配置

在设置窗口中可以配置：

- **快捷键**: 自定义全局快捷键组合
- **Ollama地址**: 配置Ollama服务地址（默认：http://localhost:11434）
- **模型名称**: 指定使用的AI模型（默认：qwen2.5:7b）
- **开机自启**: 设置是否开机自动启动

## 配置文件

程序会在运行目录生成 `config.json` 配置文件：

```json
{
  "hotkey": "ctrl+shift+t",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "qwen2.5:7b",
  "auto_start": false,
  "translation_prompt": "请将以下中文翻译成英文，只返回翻译结果，不要添加任何解释："
}
```

## 支持的快捷键格式

- `ctrl+shift+t`
- `alt+f1`
- `ctrl+alt+z`
- `win+shift+x`

## 故障排除

### 常见问题

**Q: 快捷键不响应？**
A: 
- 检查是否有其他程序占用了相同快捷键
- 尝试以管理员权限运行程序
- 在设置中更换其他快捷键组合

**Q: 翻译失败？**
A:
- 确认Ollama服务正在运行
- 检查模型是否已正确安装
- 在设置中测试Ollama连接

**Q: 无法获取选中文本？**
A:
- 确保文本已正确选中
- 某些应用可能不支持剪贴板操作
- 尝试先复制文本再使用快捷键

**Q: 程序无法启动？**
A:
- 检查Python版本是否为3.7+
- 确认所有依赖已正确安装
- 查看控制台错误信息

### 日志信息

程序运行时会在控制台输出详细的日志信息，包括：
- 组件启动状态
- 翻译过程信息
- 错误和警告信息

## 项目结构

```
InputTranslator/
├── main.py                 # 主程序入口
├── config.py               # 配置管理模块
├── ollama_client.py        # Ollama客户端
├── text_handler.py         # 文本处理模块
├── hotkey_listener.py      # 快捷键监听模块
├── tray_app.py            # 系统托盘应用
├── requirements.txt        # 项目依赖
├── README.md              # 使用说明
├── config.json            # 配置文件（运行时生成）
└── .trae/
    └── documents/
        ├── 产品需求文档.md
        └── 技术架构文档.md
```

## 技术架构

- **前端**: Python + tkinter（设置界面）
- **后端**: 本地Python服务
- **AI服务**: Ollama本地服务
- **核心依赖**: 
  - `pynput`: 全局快捷键监听
  - `pyperclip`: 剪贴板操作
  - `requests`: HTTP请求
  - `pystray`: 系统托盘
  - `Pillow`: 图像处理

## 开发说明

### 模块说明

- **main.py**: 程序入口，负责初始化和协调各模块
- **config.py**: 配置管理，处理配置文件的读写
- **ollama_client.py**: Ollama API客户端，处理翻译请求
- **text_handler.py**: 文本处理，获取、翻译和替换文本
- **hotkey_listener.py**: 全局快捷键监听和处理
- **tray_app.py**: 系统托盘界面和设置窗口

### 扩展开发

如需扩展功能，可以：

1. 在 `config.py` 中添加新的配置项
2. 在 `ollama_client.py` 中支持更多AI模型
3. 在 `text_handler.py` 中添加更多文本处理逻辑
4. 在 `tray_app.py` 中添加新的界面功能

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持中文到英文翻译
- 全局快捷键功能
- 系统托盘界面
- 基本设置功能