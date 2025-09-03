# -*- coding: utf-8 -*-
"""
文本处理模块
负责获取选中文本、翻译文本和替换文本的核心功能
"""

import time
import pyperclip
import pyautogui
from typing import Optional
from ollama_client import ollama_client
from logger import logger, log_exception


class TextHandler:
    """文本处理类"""
    
    def __init__(self):
        """初始化文本处理器"""
        # 设置pyautogui的安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    
    @log_exception
    def get_selected_text(self) -> Optional[str]:
        """获取当前选中的文本
        
        Returns:
            选中的文本内容，失败时返回None
        """
        try:
            # 保存当前剪贴板内容
            original_clipboard = self._get_clipboard_safely()
            
            # 清空剪贴板
            pyperclip.copy('')
            time.sleep(0.1)
            
            # 模拟Ctrl+C复制选中文本
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)  # 等待复制完成
            
            # 获取复制的文本
            selected_text = self._get_clipboard_safely()
            
            # 恢复原剪贴板内容
            if original_clipboard is not None:
                pyperclip.copy(original_clipboard)
            
            # 检查是否成功获取到文本
            if selected_text and selected_text.strip():
                logger.log_text_operation("获取选中文本", selected_text.strip(), True)
                return selected_text.strip()
            else:
                logger.warning("未检测到选中的文本")
                return None
                
        except Exception as e:
            logger.error(f"获取选中文本失败: {e}")
            return None
    
    def _get_clipboard_safely(self) -> Optional[str]:
        """安全地获取剪贴板内容
        
        Returns:
            剪贴板内容，失败时返回None
        """
        try:
            return pyperclip.paste()
        except Exception:
            return None
    
    @log_exception
    def get_all_text(self) -> Optional[str]:
        """使用Ctrl+A全选获取所有文本
        
        Returns:
            全选的文本内容，失败时返回None
        """
        try:
            # 保存当前剪贴板内容
            original_clipboard = self._get_clipboard_safely()
            
            # 清空剪贴板
            pyperclip.copy('')
            time.sleep(0.1)
            
            # 全选所有内容
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            
            # 复制选中内容
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)  # 稍微延长等待时间
            
            # 获取复制的文本
            selected_text = self._get_clipboard_safely()
            
            # 恢复原剪贴板内容
            if original_clipboard is not None:
                pyperclip.copy(original_clipboard)
            
            if selected_text and selected_text.strip():
                logger.log_text_operation("全选获取文本", selected_text.strip(), True)
                return selected_text.strip()
            else:
                logger.warning("全选未获取到文本")
                return None
                
        except Exception as e:
            logger.error(f"全选获取文本失败: {e}")
            return None
    
    @log_exception
    def replace_text(self, new_text: str) -> bool:
        """替换当前选中的文本
        
        Args:
            new_text: 要替换的新文本
            
        Returns:
            替换是否成功
        """
        if not new_text:
            return False
        
        try:
            # 保存当前剪贴板内容
            original_clipboard = self._get_clipboard_safely()
            
            # 将新文本复制到剪贴板
            pyperclip.copy(new_text)
            time.sleep(0.1)
            
            # 模拟Ctrl+V粘贴新文本
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)  # 等待粘贴完成
            
            # 恢复原剪贴板内容
            if original_clipboard is not None:
                pyperclip.copy(original_clipboard)
            
            return True
            
        except Exception as e:
            logger.error(f"替换文本失败: {e}")
            return False
    
    @log_exception
    def translate_text(self, chinese_text: str) -> Optional[str]:
        """翻译中文文本为英文
        
        Args:
            chinese_text: 待翻译的中文文本
            
        Returns:
            翻译后的英文文本，失败时返回None
        """
        if not chinese_text or not chinese_text.strip():
            return None
        
        # 检查文本是否包含中文字符
        if not self._contains_chinese(chinese_text):
            logger.info("文本不包含中文字符，跳过翻译")
            return None
        
        logger.info(f"正在翻译: {chinese_text[:50]}..." if len(chinese_text) > 50 else f"正在翻译: {chinese_text}")
        
        # 调用ollama进行翻译
        translated_text = ollama_client.translate_text(chinese_text)
        
        if translated_text:
            logger.log_translation(chinese_text, translated_text, True)
            return translated_text
        else:
            logger.log_translation(chinese_text, "", False)
            return None
    
    def _contains_chinese(self, text: str) -> bool:
        """检查文本是否包含中文字符
        
        Args:
            text: 待检查的文本
            
        Returns:
            是否包含中文字符
        """
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False
    
    def process_translation(self) -> bool:
        """执行完整的翻译流程：获取文本 -> 翻译 -> 替换
        优先使用全选功能获取所有文本
        
        Returns:
            翻译流程是否成功完成
        """
        try:
            # 1. 先尝试全选获取文本
            selected_text = self.get_all_text()
            if not selected_text:
                # 降级到获取选中文本
                selected_text = self.get_selected_text()
            if not selected_text:
                logger.warning("未能获取任何文本")
                return False
            
            # 2. 翻译文本
            translated_text = self.translate_text(selected_text)
            if not translated_text:
                logger.error("翻译失败")
                return False
            
            # 3. 替换文本
            success = self.replace_text(translated_text)
            if success:
                logger.info("翻译替换完成")
                return True
            else:
                logger.error("文本替换失败")
                return False
                
        except Exception as e:
            print(f"翻译流程执行失败: {e}")
            return False
    
    def get_text_at_cursor(self) -> Optional[str]:
        """获取光标位置的文本（尝试选择当前行或单词）
        
        Returns:
            光标位置的文本，失败时返回None
        """
        try:
            # 保存当前剪贴板内容
            original_clipboard = self._get_clipboard_safely()
            
            # 清空剪贴板
            pyperclip.copy('')
            time.sleep(0.1)
            
            # 尝试选择当前单词（双击）
            pyautogui.doubleClick()
            time.sleep(0.1)
            
            # 复制选中内容
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)
            
            # 获取复制的文本
            selected_text = self._get_clipboard_safely()
            
            # 如果没有获取到文本，尝试选择整行
            if not selected_text or not selected_text.strip():
                # 移动到行首
                pyautogui.hotkey('home')
                time.sleep(0.1)
                
                # 选择整行
                pyautogui.hotkey('shift', 'end')
                time.sleep(0.1)
                
                # 复制选中内容
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.2)
                
                selected_text = self._get_clipboard_safely()
            
            # 恢复原剪贴板内容
            if original_clipboard is not None:
                pyperclip.copy(original_clipboard)
            
            if selected_text and selected_text.strip():
                return selected_text.strip()
            else:
                return None
                
        except Exception as e:
            print(f"获取光标位置文本失败: {e}")
            return None
    
    def get_all_text(self) -> Optional[str]:
        """获取输入框中的全部文本（使用Ctrl+A全选）
        
        Returns:
            输入框中的全部文本，失败时返回None
        """
        try:
            # 保存当前剪贴板内容
            original_clipboard = self._get_clipboard_safely()
            
            # 清空剪贴板
            pyperclip.copy('')
            time.sleep(0.1)
            
            # 使用Ctrl+A全选所有内容
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)  # 等待全选完成
            
            # 复制全选的内容
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)  # 等待复制完成
            
            # 获取复制的文本
            all_text = self._get_clipboard_safely()
            
            # 恢复原剪贴板内容
            if original_clipboard is not None:
                pyperclip.copy(original_clipboard)
            
            # 检查是否成功获取到文本
            if all_text and all_text.strip():
                return all_text.strip()
            else:
                print("未检测到输入框中的文本")
                return None
                
        except Exception as e:
            print(f"获取全部文本失败: {e}")
            return None
    
    def smart_translate(self) -> bool:
        """智能翻译：优先全选所有内容，如果没有则尝试获取选中文本或光标位置文本
        
        Returns:
            翻译是否成功
        """
        try:
            # 首先尝试全选获取所有文本
            text_to_translate = self.get_all_text()
            
            # 如果全选没有获取到文本，尝试获取选中文本
            if not text_to_translate:
                text_to_translate = self.get_selected_text()
            
            # 如果还是没有文本，尝试获取光标位置文本
            if not text_to_translate:
                text_to_translate = self.get_text_at_cursor()
            
            if not text_to_translate:
                print("未能获取到任何文本")
                return False
            
            # 翻译文本
            translated_text = self.translate_text(text_to_translate)
            if not translated_text:
                return False
            
            # 替换文本
            return self.replace_text(translated_text)
            
        except Exception as e:
            print(f"智能翻译失败: {e}")
            return False


# 全局文本处理器实例
text_handler = TextHandler()