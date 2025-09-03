# -*- coding: utf-8 -*-
"""
配置管理模块
负责应用配置的读取、保存和管理
"""

import json
import os
import sys
from typing import Dict, Any


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config.json"):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        # 获取exe文件所在目录或脚本所在目录
        if getattr(sys, 'frozen', False):
            # 打包后的exe环境
            base_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 确保配置文件在程序目录下
        self.config_file = os.path.join(base_dir, config_file)
        self.config_data = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "hotkey": "ctrl+shift+a",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "qwen2.5:latest",
            "auto_start": False,
            "translation_prompt": "请将以下中文翻译成英文, 只返回翻译结果, 不要添加任何解释, 注意符合欧美英文的使用习惯:",
            "window_title": "InputTranslator",
            "tray_tooltip": "InputTranslator - 中英文翻译工具",
            "enable_logging": True
        }
    
    def load_config(self) -> None:
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    # 合并配置，保留默认值
                    self.config_data.update(file_config)
            else:
                # 配置文件不存在，创建默认配置文件
                print(f"配置文件不存在，创建默认配置: {self.config_file}")
                self.save_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 使用默认配置，并尝试创建配置文件
            try:
                self.save_config()
            except:
                pass
    
    def save_config(self) -> bool:
        """保存配置到文件
        
        Returns:
            保存是否成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_hotkey(self) -> str:
        """获取快捷键配置
        
        Returns:
            快捷键字符串
        """
        return self.config_data.get("hotkey", "ctrl+shift+t")
    
    def set_hotkey(self, hotkey: str) -> None:
        """设置快捷键配置
        
        Args:
            hotkey: 快捷键字符串
        """
        self.config_data["hotkey"] = hotkey
        self.save_config()
    
    def get_ollama_url(self) -> str:
        """获取Ollama服务地址
        
        Returns:
            Ollama服务URL
        """
        return self.config_data.get("ollama_url", "http://localhost:11434")
    
    def set_ollama_url(self, url: str) -> None:
        """设置Ollama服务地址
        
        Args:
            url: Ollama服务URL
        """
        self.config_data["ollama_url"] = url
        self.save_config()
    
    def get_ollama_model(self) -> str:
        """获取Ollama模型名称
        
        Returns:
            模型名称
        """
        return self.config_data.get("ollama_model", "qwen2.5:7b")
    
    def set_ollama_model(self, model: str) -> None:
        """设置Ollama模型名称
        
        Args:
            model: 模型名称
        """
        self.config_data["ollama_model"] = model
        self.save_config()
    
    def get_translation_prompt(self) -> str:
        """获取翻译提示词
        
        Returns:
            翻译提示词
        """
        return self.config_data.get("translation_prompt", 
                                   "请将以下中文翻译成英文，只返回翻译结果，不要添加任何解释：")
    
    def set_translation_prompt(self, prompt: str) -> None:
        """设置翻译提示词
        
        Args:
            prompt: 翻译提示词
        """
        self.config_data["translation_prompt"] = prompt
        self.save_config()
    
    def get_auto_start(self) -> bool:
        """获取开机自启动配置
        
        Returns:
            是否开机自启动
        """
        return self.config_data.get("auto_start", False)
    
    def set_auto_start(self, auto_start: bool) -> None:
        """设置开机自启动配置
        
        Args:
            auto_start: 是否开机自启动
        """
        self.config_data["auto_start"] = auto_start
        self.save_config()
    
    def get_window_title(self) -> str:
        """获取窗口标题
        
        Returns:
            窗口标题
        """
        return self.config_data.get("window_title", "InputTranslator")
    
    def get_tray_tooltip(self) -> str:
        """获取托盘提示文本
        
        Returns:
            托盘提示文本
        """
        return self.config_data.get("tray_tooltip", "InputTranslator - 中英文翻译工具")
    
    def get_enable_logging(self) -> bool:
        """获取日志记录开关状态
        
        Returns:
            是否启用日志记录
        """
        return self.config_data.get("enable_logging", True)
    
    def set_enable_logging(self, enable: bool) -> None:
        """设置日志记录开关状态
        
        Args:
            enable: 是否启用日志记录
        """
        self.config_data["enable_logging"] = enable
        self.save_config()
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置
        
        Returns:
            配置字典
        """
        return self.config_data.copy()
    
    def update_config(self, config_dict: Dict[str, Any]) -> bool:
        """批量更新配置
        
        Args:
            config_dict: 配置字典
            
        Returns:
            更新是否成功
        """
        try:
            self.config_data.update(config_dict)
            return self.save_config()
        except Exception as e:
            print(f"更新配置失败: {e}")
            return False


# 全局配置实例
config = Config()