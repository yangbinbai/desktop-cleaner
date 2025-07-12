import os
import subprocess
import sys

def build_exe():
    """打包应用为exe文件"""
    print("开始打包桌面整理工具...")
    
    # 检查是否安装了pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包为单个文件
        "--windowed",  # 无控制台窗口
        "--name=桌面整理工具",  # 可执行文件名
        "--clean",  # 清理临时文件
        "desktop_cleaner.py"
    ]
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("打包成功！")
        print("可执行文件位置: dist/桌面整理工具.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        print(f"错误输出: {e.stderr}")
    except FileNotFoundError:
        print("PyInstaller未找到，请确保已正确安装")

if __name__ == "__main__":
    build_exe()