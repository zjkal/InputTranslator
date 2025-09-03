# -*- coding: utf-8 -*-
"""
日志模块
提供统一的日志记录功能，支持控制台和文件输出
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional


class Logger:
    """统一日志管理器"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """设置日志记录器"""
        # 创建日志记录器
        self._logger = logging.getLogger('InputTranslator')
        self._logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if self._logger.handlers:
            return
        
        # 检查是否启用日志记录
        if not self._is_logging_enabled():
            return
        
        # 创建日志目录
        log_dir = self._get_log_directory()
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件路径
        log_file = os.path.join(log_dir, f"InputTranslator_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器（如果有控制台）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        
        # 记录启动信息
        self._logger.info("=" * 50)
        self._logger.info("InputTranslator 启动")
        self._logger.info(f"日志文件: {log_file}")
        self._logger.info(f"Python版本: {sys.version}")
        self._logger.info(f"工作目录: {os.getcwd()}")
        self._logger.info("=" * 50)
    
    def _get_log_directory(self) -> str:
        """获取日志目录路径"""
        if getattr(sys, 'frozen', False):
            # 打包后的exe程序
            app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(app_dir, 'logs')
    
    def reinitialize_logger(self):
        """重新初始化日志器（用于配置更改后）"""
        # 清除现有处理器
        if self._logger and self._logger.handlers:
            for handler in self._logger.handlers[:]:
                self._logger.removeHandler(handler)
                handler.close()
        
        # 重新设置日志器
        self._setup_logger()
    
    def _is_logging_enabled(self) -> bool:
        """检查日志记录是否启用
        
        Returns:
            是否启用日志记录
        """
        try:
            # 延迟导入避免循环依赖
            from config import config
            return config.get_enable_logging()
        except ImportError:
            # 如果无法导入config，默认启用日志
            return True
    
    def debug(self, message: str):
        """记录调试信息"""
        if self._logger and self._is_logging_enabled():
            self._logger.debug(message)
    
    def info(self, message: str):
        """记录一般信息"""
        if self._logger and self._is_logging_enabled():
            self._logger.info(message)
    
    def warning(self, message: str):
        """记录警告信息"""
        if self._logger and self._is_logging_enabled():
            self._logger.warning(message)
    
    def error(self, message: str):
        """记录错误信息"""
        if self._logger and self._is_logging_enabled():
            self._logger.error(message)
    
    def exception(self, message: str):
        """记录异常信息（包含堆栈跟踪）"""
        if self._logger and self._is_logging_enabled():
            self._logger.exception(message)
    
    def log_function_call(self, func_name: str, *args, **kwargs):
        """记录函数调用"""
        args_str = ', '.join([str(arg) for arg in args])
        kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
        params = ', '.join(filter(None, [args_str, kwargs_str]))
        self.debug(f"调用函数: {func_name}({params})")
    
    def log_hotkey_trigger(self, hotkey: str):
        """记录快捷键触发"""
        self.info(f"快捷键 {hotkey} 被触发")
    
    def log_translation(self, original: str, translated: str, success: bool):
        """记录翻译结果"""
        if success:
            self.info(f"翻译成功: '{original}' -> '{translated}'")
        else:
            self.error(f"翻译失败: '{original}'")
    
    def log_text_operation(self, operation: str, text: str, success: bool):
        """记录文本操作"""
        status = "成功" if success else "失败"
        self.info(f"{operation}{status}: '{text[:50]}{'...' if len(text) > 50 else ''}'")


# 全局日志实例
logger = Logger()


def log_exception(func):
    """装饰器：自动记录函数异常"""
    def wrapper(*args, **kwargs):
        try:
            if logger._is_logging_enabled():
                logger.log_function_call(func.__name__, *args, **kwargs)
            return func(*args, **kwargs)
        except Exception as e:
            if logger._is_logging_enabled():
                logger.exception(f"函数 {func.__name__} 执行异常: {e}")
            raise
    return wrapper