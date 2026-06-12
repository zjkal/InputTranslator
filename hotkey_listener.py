# -*- coding: utf-8 -*-
"""
全局快捷键监听模块
负责监听全局快捷键并触发翻译功能
"""

import threading
import time
from typing import Callable, Optional
from pynput import keyboard
from config import config
from text_handler import text_handler
from logger import logger, log_exception


class HotkeyListener:
    """全局快捷键监听器"""
    
    def __init__(self):
        """初始化快捷键监听器"""
        self.listener: Optional[keyboard.GlobalHotKeys] = None
        self.is_running = False
        self.is_translating = False
        self.hotkey_string = config.get_hotkey()
        self.callback_func: Optional[Callable] = None
        self.last_trigger_time = 0
        self.min_trigger_interval = 1.0  # 最小触发间隔（秒），防止重复触发
        self.translation_lock = threading.Lock()
        logger.info("快捷键监听器初始化完成")
    
    def _parse_hotkey(self, hotkey_string: str) -> str:
        """解析快捷键字符串为pynput格式
        
        Args:
            hotkey_string: 快捷键字符串，如 'ctrl+shift+t'
            
        Returns:
            pynput格式的快捷键字符串
        """
        # 将常见的快捷键名称转换为pynput格式
        key_mapping = {
            'ctrl': '<ctrl>',
            'shift': '<shift>',
            'alt': '<alt>',
            'win': '<cmd>',
            'cmd': '<cmd>',
            'super': '<cmd>'
        }
        
        parts = hotkey_string.lower().split('+')
        converted_parts = []
        
        for part in parts:
            part = part.strip()
            if part in key_mapping:
                converted_parts.append(key_mapping[part])
            else:
                # 对于字母和数字，直接使用
                converted_parts.append(part)
        
        return '+'.join(converted_parts)
    
    def _on_hotkey_triggered(self):
        """快捷键触发时的回调函数"""
        current_time = time.time()
        
        # 防止重复触发
        if current_time - self.last_trigger_time < self.min_trigger_interval:
            return

        if self.is_translating:
            logger.info("上一条翻译尚未完成，忽略本次触发")
            self._notify_user("上一条翻译仍在进行中，请稍候。", "InputTranslator")
            return
        
        self.last_trigger_time = current_time
        
        logger.log_hotkey_trigger(self.hotkey_string)
        
        try:
            # 在新线程中执行翻译，避免阻塞快捷键监听
            translation_thread = threading.Thread(
                target=self._safe_execute_translation,
                daemon=True
            )
            translation_thread.start()
        except Exception as e:
            logger.exception(f"启动翻译线程失败: {e}")
    
    def _safe_execute_translation(self):
        """安全的翻译执行函数"""
        try:
            self._execute_translation()
        except Exception as e:
            logger.exception(f"翻译执行失败: {e}")

    def _notify_user(self, message: str, title: str = "InputTranslator") -> None:
        """通过托盘通知向用户反馈状态"""
        try:
            from tray_app import tray_app
            tray_app.notify(message, title)
        except Exception as exc:
            logger.warning(f"发送用户通知失败: {exc}")
            logger.info(f"{title}: {message}")

    def _set_tray_status(self, status_text: Optional[str] = None) -> None:
        """更新托盘提示文本"""
        try:
            from tray_app import tray_app
            tray_app.set_status(status_text)
        except Exception as exc:
            logger.warning(f"更新托盘状态失败: {exc}")
    
    def _execute_translation(self):
        """执行翻译操作"""
        if not self.translation_lock.acquire(blocking=False):
            self._notify_user("上一条翻译仍在进行中，请稍候。", "InputTranslator")
            return

        self.is_translating = True

        try:
            # 短暂延迟，确保快捷键释放
            time.sleep(0.1)
            self._set_tray_status("正在翻译")
            self._notify_user("正在翻译，请稍候...", "InputTranslator")
            
            # 执行智能翻译
            success = text_handler.smart_translate()
            result = text_handler.get_last_result()
            message = result.get("message", "翻译已结束")

            if success:
                logger.info(message)
            else:
                logger.warning(message)
                self._notify_user(message, "翻译失败")
                
            # 如果有自定义回调函数，调用它
            if self.callback_func:
                self.callback_func(success)
                
        except Exception as e:
            logger.exception(f"执行翻译时发生错误: {e}")
            self._notify_user(f"执行翻译时发生错误: {e}", "翻译失败")
        finally:
            self.is_translating = False
            self.translation_lock.release()
            self._set_tray_status(None)
    
    @log_exception
    def start_listening(self, callback: Optional[Callable] = None) -> bool:
        """开始监听快捷键
        
        Args:
            callback: 翻译完成后的回调函数
            
        Returns:
            是否成功开始监听
        """
        if self.is_running:
            logger.warning("快捷键监听器已在运行")
            return True
        
        try:
            self.callback_func = callback
            
            # 解析快捷键
            parsed_hotkey = self._parse_hotkey(self.hotkey_string)
            logger.info(f"开始监听快捷键: {self.hotkey_string} ({parsed_hotkey})")
            
            # 创建快捷键映射
            hotkey_mapping = {
                parsed_hotkey: self._on_hotkey_triggered
            }
            
            # 创建并启动监听器
            self.listener = keyboard.GlobalHotKeys(hotkey_mapping)
            self.listener.start()
            
            self.is_running = True
            logger.info("快捷键监听器启动成功")
            return True
            
        except Exception as e:
            logger.exception(f"启动快捷键监听器失败: {e}")
            return False
    
    @log_exception
    def stop_listening(self) -> bool:
        """停止监听快捷键
        
        Returns:
            是否成功停止监听
        """
        if not self.is_running:
            logger.warning("快捷键监听器未在运行")
            return True
        
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            self.is_running = False
            logger.info("快捷键监听器已停止")
            return True
            
        except Exception as e:
            logger.exception(f"停止快捷键监听器失败: {e}")
            return False
    
    def restart_listening(self, new_hotkey: Optional[str] = None) -> bool:
        """重启快捷键监听器（用于更改快捷键后）
        
        Args:
            new_hotkey: 新的快捷键字符串
            
        Returns:
            是否成功重启
        """
        # 停止当前监听
        self.stop_listening()
        
        # 更新快捷键
        if new_hotkey:
            self.hotkey_string = new_hotkey
        else:
            self.hotkey_string = config.get_hotkey()
        
        # 重新开始监听
        return self.start_listening(self.callback_func)
    
    def update_hotkey(self, new_hotkey: str) -> bool:
        """更新快捷键配置
        
        Args:
            new_hotkey: 新的快捷键字符串
            
        Returns:
            是否成功更新
        """
        try:
            # 验证快捷键格式
            parsed_hotkey = self._parse_hotkey(new_hotkey)
            
            # 保存到配置
            config.set_hotkey(new_hotkey)
            
            # 重启监听器
            return self.restart_listening(new_hotkey)
            
        except Exception as e:
            logger.error(f"更新快捷键失败: {e}")
            return False
    
    def get_current_hotkey(self) -> str:
        """获取当前快捷键
        
        Returns:
            当前快捷键字符串
        """
        return self.hotkey_string
    
    def is_listening(self) -> bool:
        """检查是否正在监听
        
        Returns:
            是否正在监听
        """
        return self.is_running
    
    def test_hotkey(self, hotkey_string: str) -> bool:
        """测试快捷键格式是否有效
        
        Args:
            hotkey_string: 要测试的快捷键字符串
            
        Returns:
            快捷键格式是否有效
        """
        try:
            parsed_hotkey = self._parse_hotkey(hotkey_string)
            
            # 尝试创建一个临时的快捷键映射来验证格式
            test_mapping = {parsed_hotkey: lambda: None}
            test_listener = keyboard.GlobalHotKeys(test_mapping)
            test_listener.stop()  # 立即停止，只是为了测试格式
            
            return True
        except Exception as e:
            logger.error(f"快捷键格式无效: {e}")
            return False
    
    def get_status(self) -> dict:
        """获取监听器状态信息
        
        Returns:
            状态信息字典
        """
        return {
            "is_running": self.is_running,
            "hotkey": self.hotkey_string,
            "last_trigger_time": self.last_trigger_time,
            "min_trigger_interval": self.min_trigger_interval
        }


# 全局快捷键监听器实例
hotkey_listener = HotkeyListener()
