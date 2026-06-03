# -*- coding: utf-8 -*-
"""
文本处理模块
负责获取选中文本、翻译文本和替换文本的核心功能
"""

import time
from typing import Any, Dict, Optional, Tuple

import pyautogui
import pyperclip

from logger import logger, log_exception
from ollama_client import ollama_client


class TextHandler:
    """文本处理类"""

    def __init__(self):
        """初始化文本处理器"""
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        self.last_result: Dict[str, Any] = {
            "success": False,
            "message": "尚未执行翻译",
            "source": None
        }

    def _set_last_result(self, success: bool, message: str, source: Optional[str] = None) -> None:
        """记录最近一次翻译结果，供托盘提示使用"""
        self.last_result = {
            "success": success,
            "message": message,
            "source": source
        }

    def get_last_result(self) -> Dict[str, Any]:
        """获取最近一次翻译结果"""
        return self.last_result.copy()

    def _get_clipboard_safely(self) -> Optional[str]:
        """安全地获取剪贴板内容"""
        try:
            return pyperclip.paste()
        except Exception:
            return None

    def _restore_clipboard(self, original_clipboard: Optional[str]) -> None:
        """恢复剪贴板，尽量减少对用户当前剪贴板的影响"""
        try:
            if original_clipboard is not None:
                pyperclip.copy(original_clipboard)
        except Exception as exc:
            logger.warning(f"恢复剪贴板失败: {exc}")

    def _copy_current_selection(self) -> Optional[str]:
        """复制当前选区内容并返回文本"""
        pyperclip.copy("")
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        copied_text = self._get_clipboard_safely()
        if copied_text and copied_text.strip():
            return copied_text.strip()
        return None

    @log_exception
    def get_selected_text(self) -> Optional[str]:
        """获取当前选中的文本"""
        original_clipboard = self._get_clipboard_safely()
        try:
            selected_text = self._copy_current_selection()
            if selected_text:
                logger.log_text_operation("获取选中文本", selected_text, True)
                return selected_text

            logger.warning("未检测到选中的文本")
            return None
        except Exception as exc:
            logger.error(f"获取选中文本失败: {exc}")
            return None
        finally:
            self._restore_clipboard(original_clipboard)

    @log_exception
    def get_all_text(self) -> Optional[str]:
        """使用 Ctrl+A 全选获取输入框中的文本"""
        original_clipboard = self._get_clipboard_safely()
        try:
            pyperclip.copy("")
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.2)
            pyautogui.hotkey("ctrl", "c")
            time.sleep(0.3)

            all_text = self._get_clipboard_safely()
            if all_text and all_text.strip():
                cleaned_text = all_text.strip()
                logger.log_text_operation("全选获取文本", cleaned_text, True)
                return cleaned_text

            logger.warning("全选未获取到文本")
            return None
        except Exception as exc:
            logger.error(f"全选获取文本失败: {exc}")
            return None
        finally:
            self._restore_clipboard(original_clipboard)

    @log_exception
    def get_text_at_cursor(self) -> Optional[str]:
        """获取光标附近的文本，作为兜底方案"""
        original_clipboard = self._get_clipboard_safely()
        try:
            pyperclip.copy("")
            time.sleep(0.1)

            pyautogui.doubleClick()
            time.sleep(0.1)
            selected_text = self._copy_current_selection()

            if not selected_text:
                pyautogui.hotkey("home")
                time.sleep(0.1)
                pyautogui.hotkey("shift", "end")
                time.sleep(0.1)
                selected_text = self._copy_current_selection()

            if selected_text:
                logger.log_text_operation("获取光标附近文本", selected_text, True)
                return selected_text

            logger.warning("未检测到光标附近可翻译文本")
            return None
        except Exception as exc:
            logger.error(f"获取光标附近文本失败: {exc}")
            return None
        finally:
            self._restore_clipboard(original_clipboard)

    @log_exception
    def replace_text(self, new_text: str) -> bool:
        """替换当前选中的文本"""
        if not new_text:
            return False

        original_clipboard = self._get_clipboard_safely()
        try:
            pyperclip.copy(new_text)
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.2)
            return True
        except Exception as exc:
            logger.error(f"替换文本失败: {exc}")
            return False
        finally:
            self._restore_clipboard(original_clipboard)

    @log_exception
    def translate_text(self, chinese_text: str) -> Optional[str]:
        """兼容旧接口，仅返回翻译结果"""
        translated_text, _ = self.translate_text_with_status(chinese_text)
        return translated_text

    def translate_text_with_status(self, chinese_text: str) -> Tuple[Optional[str], str]:
        """翻译中文文本并返回更明确的状态信息"""
        if not chinese_text or not chinese_text.strip():
            return None, "未检测到可翻译文本，请先选中文本后再按快捷键。"

        if not self._contains_chinese(chinese_text):
            logger.info("文本不包含中文字符，跳过翻译")
            return None, "当前文本不包含中文，已跳过翻译。"

        preview = chinese_text[:50]
        logger.info(f"正在翻译: {preview}..." if len(chinese_text) > 50 else f"正在翻译: {preview}")

        translated_text, message = ollama_client.translate_with_status(chinese_text)
        if translated_text:
            logger.log_translation(chinese_text, translated_text, True)
            return translated_text, message

        logger.log_translation(chinese_text, "", False)
        return None, message

    def _contains_chinese(self, text: str) -> bool:
        """检查文本是否包含中文字符"""
        for char in text:
            if "\u4e00" <= char <= "\u9fff":
                return True
        return False

    def process_translation(self) -> bool:
        """兼容旧接口，执行完整翻译流程"""
        return self.smart_translate()

    def smart_translate(self) -> bool:
        """智能翻译：优先选中文本，其次光标附近文本，最后才尝试整框翻译"""
        try:
            text_sources = [
                ("选中文本", self.get_selected_text),
                ("光标附近文本", self.get_text_at_cursor),
                ("整个输入框", self.get_all_text),
            ]

            text_to_translate = None
            source_name = None

            for source_name, getter in text_sources:
                text_to_translate = getter()
                if text_to_translate:
                    break

            if not text_to_translate:
                message = "未检测到可翻译文本，请先选中文本后再按快捷键。"
                self._set_last_result(False, message)
                logger.warning(message)
                return False

            translated_text, message = self.translate_text_with_status(text_to_translate)
            if not translated_text:
                self._set_last_result(False, message, source_name)
                return False

            if not self.replace_text(translated_text):
                message = "翻译完成，但替换文本失败，请重试。"
                self._set_last_result(False, message, source_name)
                logger.error(message)
                return False

            if source_name == "整个输入框":
                success_message = "已翻译整个输入框内容。"
            elif source_name == "光标附近文本":
                success_message = "已翻译光标附近文本。"
            else:
                success_message = "已翻译选中文本。"

            self._set_last_result(True, success_message, source_name)
            logger.info(success_message)
            return True
        except Exception as exc:
            message = f"智能翻译失败: {exc}"
            self._set_last_result(False, message)
            logger.exception(message)
            return False


# 全局文本处理器实例
text_handler = TextHandler()
