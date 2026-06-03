#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InputTranslator 主程序
一个极简的Windows桌面翻译工具
"""

import sys
import signal
import time
import traceback
from logger import logger
from hotkey_listener import hotkey_listener
from tray_app import tray_app


class InputTranslator:
    """InputTranslator主应用类"""
    
    def __init__(self):
        """初始化应用"""
        self.is_running = False
        self.startup_success = False
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
def signal_handler(signum, frame):
    """信号处理函数"""
    logger.info("接收到退出信号，正在关闭程序...")
    cleanup_and_exit()
    
    def _check_dependencies(self) -> bool:
        """检查依赖项是否满足
        
        Returns:
            依赖项是否满足
        """
        try:
            # 检查必要的模块是否可以导入
            import pynput
            import pyperclip
            import requests
            import pystray
            import PIL
            
            print("✓ 所有依赖项检查通过")
            return True
            
        except ImportError as e:
            print(f"✗ 缺少依赖项: {e}")
            print("请运行: pip install -r requirements.txt")
            return False
    
    def _check_ollama_service(self) -> bool:
        """检查Ollama服务状态
        
        Returns:
            Ollama服务是否可用
        """
        print("正在检查Ollama服务...")
        
        if ollama_client.test_connection():
            print("✓ Ollama服务连接成功")
            
            if ollama_client.check_model_available():
                print(f"✓ 模型 {config.get_ollama_model()} 可用")
                return True
            else:
                print(f"✗ 模型 {config.get_ollama_model()} 不可用")
                print("请确保已下载指定的模型")
                return False
        else:
            print("✗ 无法连接到Ollama服务")
            print(f"请确保Ollama服务正在运行，地址: {config.get_ollama_url()}")
            return False
    
    def _initialize_components(self) -> bool:
        """初始化各个组件
        
        Returns:
            初始化是否成功
        """
        try:
            print("正在初始化组件...")
            
            # 启动快捷键监听器
            from hotkey_listener import hotkey_listener
            if hotkey_listener.start_listening():
                print(f"✓ 快捷键监听器启动成功 ({config.get_hotkey()})")
            else:
                print("✗ 快捷键监听器启动失败")
                return False
            
            print("✓ 所有组件初始化完成")
            return True
            
        except Exception as e:
            print(f"✗ 组件初始化失败: {e}")
            return False
    
    def _show_startup_info(self):
        """显示启动信息"""
        print("="*50)
        print("InputTranslator - 中英文翻译工具")
        print("="*50)
        print(f"版本: 1.0.0")
        print(f"快捷键: {config.get_hotkey()}")
        print(f"Ollama地址: {config.get_ollama_url()}")
        print(f"模型: {config.get_ollama_model()}")
        print("="*50)
    
    def _show_usage_info(self):
        """显示使用说明"""
        print("\n使用说明:")
        print(f"1. 在任意应用中选中中文文本")
        print(f"2. 按下快捷键 {config.get_hotkey()}")
        print(f"3. 程序会自动翻译并替换为英文")
        print(f"4. 右键点击托盘图标可以进行设置")
        print(f"5. 按 Ctrl+C 退出程序")
        print("\n程序已在后台运行...")
    
    def startup(self) -> bool:
        """启动应用
        
        Returns:
            启动是否成功
        """
        try:
            self._show_startup_info()
            
            # 检查依赖项
            if not self._check_dependencies():
                return False
            
            # 检查Ollama服务（非阻塞，只是警告）
            ollama_available = self._check_ollama_service()
            if not ollama_available:
                print("警告: Ollama服务不可用，翻译功能将无法正常工作")
                print("您可以稍后在设置中配置Ollama服务")
            
            # 初始化组件
            if not self._initialize_components():
                return False
            
            self.startup_success = True
            self.is_running = True
            
            self._show_usage_info()
            return True
            
        except Exception as e:
            print(f"启动失败: {e}")
            return False
    
    def run(self):
        """运行应用主循环"""
        if not self.startup_success:
            print("应用未成功启动")
            return
        
        try:
            # 在单独线程中启动托盘应用
            tray_thread = threading.Thread(target=tray_app.start, daemon=True)
            tray_thread.start()
            
            # 等待托盘应用启动
            time.sleep(1)
            
            # 主循环：保持程序运行
            while self.is_running and tray_app.is_running:
                time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n收到中断信号，正在退出...")
        except Exception as e:
            print(f"运行时错误: {e}")
        finally:
            self.shutdown()
    
def cleanup_and_exit():
    """清理资源并退出"""
    try:
        logger.info("开始清理资源...")
        
        # 停止快捷键监听
        hotkey_listener.stop_listening()
        
        # 停止托盘应用
        tray_app.stop()
        
        logger.info("程序已安全退出")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"清理资源时发生错误: {e}")
        sys.exit(1)


def setup_global_exception_handler():
    """设置全局异常处理器"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # 键盘中断正常处理
            logger.info("用户中断程序")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # 记录未捕获的异常
        logger.error("未捕获的异常:")
        logger.error(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    
    sys.excepthook = handle_exception

def main():
    """主函数"""
    try:
        # 设置全局异常处理器
        setup_global_exception_handler()
        
        logger.info("="*50)
        logger.info("InputTranslator - 中英文翻译工具")
        logger.info("="*50)
        logger.info("功能说明:")
        logger.info("1. 在任意软件中选中中文文本")
        logger.info("2. 按下快捷键进行翻译")
        logger.info("3. 翻译结果会自动替换原文本")
        logger.info("4. 右键点击托盘图标可以进行设置")
        logger.info("程序已在后台运行...")
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 启动快捷键监听
        if not hotkey_listener.start_listening():
            logger.error("启动快捷键监听失败")
            return False
        
        # 启动托盘应用。pystray 的 run() 会阻塞，直到用户从托盘菜单退出。
        if not tray_app.start():
            logger.error("启动托盘应用失败")
            return False
        
        logger.info("托盘应用已退出，开始清理资源")
        cleanup_and_exit()
            
    except Exception as e:
        logger.exception(f"程序运行时发生错误: {e}")
        cleanup_and_exit()
        return False
    
    return True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 最后的异常捕获
        try:
            logger.exception(f"主程序异常退出: {e}")
        except:
            # 如果连日志都无法记录，则输出到标准错误
            print(f"严重错误，无法记录日志: {e}", file=sys.stderr)
        sys.exit(1)
