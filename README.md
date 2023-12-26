开发环境:Python(3.11.6)+VSCode

打包工具:pyinstaller

# 简介

这是一个把文件及文件夹压缩为**zip**文件的工具

## 当前实现功能

- 鼠标右键文件、文件夹菜单的交互
- 单文件压缩（只能选中单个文件）
- 单文件夹压缩（只能选中单个文件夹，文件夹内可以是多层、多个文件和文件夹）
- 分卷压缩
- zip格式文件解压（不支持其他软件和工具的分卷文件解压）

# 快速上手

当前只使用了python原生库
下载或拉取本仓库所有代码即可
完成环境配置后，运行**Setup.py**文件即可

# 环境配置

- **Setup.py**为配置环境变量和配置注册表，右键菜单功能的实现

- **FileToZip.py**为压缩和解压功能实现，在**def __init__(self):**中配置运行环境

- **config.json**为运行环境和分卷大小配置

- **run_py.bat**为运行py环境下的**FileToZip.py**文件，并传递数据

- **run_exe.bat**为运行windows环境下的**FileToZip.exe**文件，并传递数据

- **Uninstall.bat**为卸载程序，功能为删除注册表项、环境变量、删除同文件夹下的所有文件
