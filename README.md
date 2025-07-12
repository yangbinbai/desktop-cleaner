# 桌面整理工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

一个功能强大的桌面文件整理工具，帮助您快速整理桌面文件并保持桌面整洁。

## 功能特性

### 🧹 一键整理
- 自动将桌面文件按类型分类到对应分类文件夹中
- 支持多种文件类型分类：文档、图片、视频、音频、压缩包、程序等
- 自动跳过文件夹和应用图标文件(.lnk, .url)
- 直接在桌面创建分类文件夹，无需额外的"桌面整理"父文件夹
- 自动生成带时间戳的整理记录文件

### 🔄 一键恢复
- 将之前整理的文件恢复到桌面原位置
- 基于JSON格式的整理记录进行精确恢复
- 支持选择特定的整理记录文件进行恢复
- 自动清理空的分类文件夹

### 💾 桌面备份
- 将桌面所有文件打包为ZIP压缩包
- 自动以日期时间命名备份文件
- 用户可选择备份保存位置

### ⚙️ 自定义设置
- **排除文件扩展名**: 可自定义不需要整理的文件类型
- **文件大小限制**: 可设置跳过大于指定大小的文件
- **配置持久化**: 设置自动保存，下次启动时生效
- **分类管理**: 支持添加、编辑、删除自定义分类

## 文件分类规则

| 分类 | 文件扩展名 |
|------|------------|
| 文档 | .txt, .doc, .docx, .pdf, .xls, .xlsx, .ppt, .pptx |
| 图片 | .jpg, .jpeg, .png, .gif, .bmp, .svg, .ico |
| 视频 | .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm |
| 音频 | .mp3, .wav, .flac, .aac, .ogg, .wma |
| 压缩包 | .zip, .rar, .7z, .tar, .gz |
| 程序 | .exe, .msi, .deb, .dmg |
| 其他 | 未匹配的其他文件类型 |

## 安装与使用

### 方法一：直接运行Python脚本

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/desktop-cleaner.git
   cd desktop-cleaner
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   python desktop_cleaner.py
   ```

### 方法二：打包为exe文件

1. **安装构建依赖**
   ```bash
   pip install pyinstaller
   ```

2. **运行打包脚本**
   ```bash
   python build.py
   ```

3. **运行可执行文件**
   - 在`dist`文件夹中找到生成的`桌面整理工具.exe`文件
   - 双击运行即可

## 系统要求

- **操作系统**: Windows 7/8/10/11
- **Python版本**: Python 3.6+ (如果直接运行脚本)
- **磁盘空间**: 约10MB

## 安全说明

- 程序会在移动文件前创建备份记录
- 所有操作都可以通过"一键恢复"功能撤销
- 不会删除任何文件，只是移动位置
- 自动跳过系统重要文件和文件夹

## 注意事项

1. 首次使用建议先备份桌面文件
2. 程序会自动跳过桌面上的文件夹和快捷方式
3. 大文件默认跳过整理，可在设置中调整大小限制
4. 恢复功能依赖于备份记录文件，请勿手动删除

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 问题反馈

如果您遇到任何问题或有功能建议，请：

1. 查看 [Issues](https://github.com/your-username/desktop-cleaner/issues) 页面
2. 创建新的 Issue 描述您的问题
3. 提供详细的错误信息和复现步骤

## 技术实现

- 使用Python + tkinter开发GUI界面
- 通过Windows注册表获取准确的桌面路径
- JSON格式存储配置和备份记录
- PyInstaller打包为独立可执行文件
- 完善的错误处理和日志记录机制

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 版本历史

### v1.9 (2025年1月)
- 📝 自动生成带时间戳的整理记录文件
- 🔧 改进文件夹清理机制
- 🎯 优化用户体验和界面设计
- 📚 完善软件说明和文档
- 🛠️ 增强错误处理和稳定性

### v1.0
- 🎉 初始版本发布
- 🧹 基本的桌面整理功能
- 🔄 一键恢复功能
- 💾 桌面备份功能
- ⚙️ 自定义设置功能

## 致谢

感谢所有为这个项目贡献代码和建议的开发者们！

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！