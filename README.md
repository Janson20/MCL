# Minecraft Launcher / Minecraft启动器

## Description / 描述

A feature-rich Minecraft launcher with multi-threaded download support, Forge installation, and GUI version selection.

一个功能丰富的Minecraft启动器，支持多线程下载、Forge安装和GUI版本选择。

## Features / 功能特点

- **Multi-threaded Downloading** - Faster downloads using 4 parallel threads  
  **多线程下载** - 使用4个并行线程实现更快的下载速度
- **Forge Support** - Easy installation of Forge mod loader  
  **Forge支持** - 轻松安装Forge模组加载器
- **Version Management** - Browse and install different Minecraft versions  
  **版本管理** - 浏览和安装不同的Minecraft版本
- **Progress Tracking** - Real-time download progress with progress bar  
  **进度跟踪** - 带有进度条的实时下载进度显示
- **GUI Interface** - User-friendly version selection interface  
  **图形界面** - 用户友好的版本选择界面
- **Logging System** - Detailed operation logs  
  **日志系统** - 详细的操作日志记录

## Requirements / 需求

- Python 3.7+  
- Required packages (see `pyproject.toml`)  
  所需包（见`pyproject.toml`）

## Installation / 安装

1. Clone this repository  
   克隆本仓库
   ```
   git clone https://github.com/Janson20/MCL.git
   ```
2. Install dependencies  
   安装依赖
   ```
   uv init
   ```
3. Run the launcher  
   运行启动器
   ```
   python main.py
   ```

## Usage / 使用方法

1. The launcher will automatically check and create necessary directories  
   启动器会自动检查并创建必要的目录
2. Choose whether to install a new version  
   选择是否安装新版本
3. Select a version from the list  
   从列表中选择版本
4. Optionally install Forge  
   可选安装Forge
5. Launch the selected version  
   启动选定的版本

## File Structure / 文件结构

```
.
├── .minecraft/          # Minecraft game directory
│   └── versions/        # Installed versions
├── latest.log           # Log file
├── pos.txt              # Mouse position log (debug)
├── main.py              # Main program
└── pyproject.toml       # Dependency list
```

## Notes / 注意事项

- First run will download the latest stable Minecraft version  
  首次运行会下载最新的稳定版Minecraft
- Forge installation requires manual execution of the downloaded installer  
  Forge安装需要手动执行下载的安装程序
- Logs are saved in `latest.log`  
  日志保存在`latest.log`中

## License / 许可证

This project is licensed under the MIT License.  
本项目采用MIT许可证。