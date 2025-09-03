#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InputTranslator 构建脚本
使用PyInstaller将Python程序打包成单文件exe
支持调试模式和发布模式
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path


def check_pyinstaller():
    """检查并安装PyInstaller"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller已安装，版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller安装失败: {e}")
            return False


def clean_build_dirs():
    """清理之前的构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 清理目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理.spec文件
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        print(f"🧹 清理文件: {spec_file}")
        spec_file.unlink()


def create_icon():
    """创建应用图标（如果不存在）"""
    icon_path = "icon.ico"
    if not os.path.exists(icon_path):
        print("ℹ️  未找到图标文件，将使用默认图标")
        return None
    return icon_path


def build_exe(debug_mode=False):
    """构建exe文件
    
    Args:
        debug_mode: 是否启用调试模式（显示控制台窗口）
    """
    mode_str = "调试模式" if debug_mode else "发布模式"
    print(f"🚀 开始构建InputTranslator.exe ({mode_str})...")
    
    # 基本PyInstaller命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 单文件模式
        "--name=InputTranslator",  # 输出文件名
        "--clean",  # 清理临时文件
    ]
    
    # 根据模式添加不同参数
    if debug_mode:
        cmd.append("--console")  # 显示控制台窗口（调试模式）
        print("调试模式：将显示控制台窗口，便于查看日志输出")
    else:
        cmd.append("--windowed")  # 无控制台窗口（发布模式）
        print("发布模式：后台运行，无控制台窗口")
    
    # 添加图标（如果存在）
    icon_path = create_icon()
    if icon_path:
        cmd.extend(["--icon", icon_path])
    
    # 添加隐藏导入（确保所有依赖都被包含）
    hidden_imports = [
        "pynput",
        "pynput.keyboard",
        "pynput.mouse", 
        "pyperclip",
        "pyautogui",
        "requests",
        "pystray",
        "PIL",
        "PIL.Image",
        "tkinter",
        "tkinter.messagebox",
        "tkinter.simpledialog",
        "threading",
        "json",
        "time",
        "os",
        "sys",
        "logger"  # 添加日志模块
    ]
    
    for module in hidden_imports:
        cmd.extend(["--hidden-import", module])
    
    # 添加数据文件
    if os.path.exists("config.json"):
        cmd.extend(["--add-data", "config.json;."])
    
    if os.path.exists("README.md"):
        cmd.extend(["--add-data", "README.md;."])
    
    # 主程序文件
    cmd.append("main.py")
    
    print(f"📋 执行命令: {' '.join(cmd)}")
    
    try:
        # 执行构建
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 构建成功！")
            
            # 根据模式重命名输出文件
            original_exe = Path('dist/InputTranslator.exe')
            if debug_mode:
                debug_exe = Path('dist/InputTranslator_Debug.exe')
                if original_exe.exists():
                    if debug_exe.exists():
                        debug_exe.unlink()
                    original_exe.rename(debug_exe)
                    print(f"📦 调试版本: {os.path.abspath(debug_exe)}")
                    exe_path = debug_exe
                else:
                    exe_path = original_exe
            else:
                print(f"📦 发布版本: {os.path.abspath(original_exe)}")
                exe_path = original_exe
            
            # 显示文件大小
            if exe_path.exists():
                file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
                print(f"📏 文件大小: {file_size:.2f} MB")
                print("\n🎉 构建完成！")
                print("💡 提示: 该exe文件可以独立运行，无需安装Python环境")
                return True
            else:
                print("❌ 构建失败：未找到输出文件")
                return False
        else:
            print("❌ 构建失败！")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='InputTranslator 构建工具')
    parser.add_argument('--debug', action='store_true', 
                       help='构建调试版本（显示控制台窗口）')
    parser.add_argument('--release', action='store_true', 
                       help='构建发布版本（无控制台窗口）')
    args = parser.parse_args()
    
    print("🔨 InputTranslator 构建工具")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists("main.py"):
        print("❌ 错误：未找到main.py文件，请在项目根目录运行此脚本")
        return False
    
    # 检查并安装PyInstaller
    if not check_pyinstaller():
        return False
    
    # 清理之前的构建
    clean_build_dirs()
    
    # 确定构建模式
    if args.debug and args.release:
        print("❌ 错误：不能同时指定 --debug 和 --release")
        return False
    elif args.debug:
        debug_mode = True
        print("构建模式：调试版本")
    elif args.release:
        debug_mode = False
        print("构建模式：发布版本")
    else:
        # 交互式选择模式
        print("请选择构建模式:")
        print("1. 发布模式（推荐）- 后台运行，无控制台窗口")
        print("2. 调试模式 - 显示控制台窗口，便于查看日志")
        
        while True:
            choice = input("请输入选择 (1/2) [默认: 1]: ").strip()
            if choice == '' or choice == '1':
                debug_mode = False
                break
            elif choice == '2':
                debug_mode = True
                break
            else:
                print("无效选择，请输入 1 或 2")
    
    # 构建exe
    success = build_exe(debug_mode)
    
    if success:
        print("\n🎯 构建完成！")
        print("📁 输出目录: dist/")
        if debug_mode:
            print("🚀 调试版本: dist/InputTranslator_Debug.exe")
            print("\n调试版本说明:")
            print("- 显示控制台窗口，可以看到详细的运行日志")
            print("- 便于调试快捷键和翻译功能问题")
            print("- 日志文件同时保存在 logs/ 目录中")
        else:
            print("🚀 发布版本: dist/InputTranslator.exe")
            print("\n发布版本说明:")
            print("- 后台运行，无控制台窗口")
            print("- 日志文件保存在程序目录的 logs/ 文件夹中")
        
        print("\n📋 通用使用说明:")
        print("1. 将exe文件复制到任意位置")
        print("2. 确保本地Ollama服务正在运行")
        print("3. 双击运行exe文件")
        print("4. 程序将在系统托盘中运行")
        print("5. 使用Ctrl+Shift+T快捷键进行翻译")
        print("6. 如遇问题，可查看 logs/ 目录中的日志文件")
    else:
        print("\n❌ 构建失败，请检查错误信息")
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 构建过程中发生未预期的错误: {e}")
        sys.exit(1)