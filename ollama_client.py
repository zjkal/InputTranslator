# -*- coding: utf-8 -*-
"""
Ollama客户端模块
负责与本地Ollama服务通信，调用AI模型进行翻译
"""

import requests
import json
import time
from typing import Optional, Dict, Any
from config import config
from logger import logger, log_exception


class OllamaClient:
    """Ollama API客户端"""
    
    def __init__(self):
        """初始化Ollama客户端"""
        self.base_url = config.get_ollama_url()
        self.model = config.get_ollama_model()
        self.translation_prompt = config.get_translation_prompt()
        self.timeout = 30  # 请求超时时间（秒）
        logger.info(f"Ollama客户端初始化: {self.base_url}, 模型: {self.model}")
    
    @log_exception
    def test_connection(self) -> bool:
        """测试与Ollama服务的连接
        
        Returns:
            连接是否成功
        """
        try:
            logger.info("测试Ollama连接...")
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                logger.info("Ollama连接正常")
                return True
            else:
                logger.error(f"Ollama服务响应异常，状态码: {response.status_code}")
                return False
        except Exception as e:
            logger.exception(f"连接Ollama服务失败: {e}")
            return False
    
    def check_model_available(self) -> bool:
        """检查指定模型是否可用
        
        Returns:
            模型是否可用
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
                return self.model in available_models
            return False
        except Exception as e:
            print(f"检查模型可用性失败: {e}")
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
        
        try:
            # 构建翻译提示词
            prompt = f"{self.translation_prompt}{chinese_text}"
            
            # 构建请求数据
            request_data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # 降低随机性，提高翻译一致性
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            logger.debug(f"发送翻译请求: {self.base_url}/api/generate")
            logger.debug(f"请求数据: 模型={self.model}, 文本长度={len(chinese_text)}")
            
            # 发送请求
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get('response', '').strip()
                
                # 记录响应时间
                response_time = time.time() - start_time
                logger.info(f"翻译完成，耗时: {response_time:.2f}秒")
                
                # 简单的后处理：移除可能的引号和多余空格
                translated_text = self._post_process_translation(translated_text)
                
                if translated_text:
                    logger.info(f"翻译成功，响应长度: {len(translated_text)}")
                    return translated_text
                else:
                    logger.error("翻译结果为空")
                    return None
            else:
                logger.error(f"翻译请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("翻译请求超时")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("无法连接到Ollama服务")
            return None
        except Exception as e:
            logger.exception(f"翻译过程中发生错误: {e}")
            return None
    
    def _post_process_translation(self, text: str) -> str:
        """后处理翻译结果
        
        Args:
            text: 原始翻译文本
            
        Returns:
            处理后的翻译文本
        """
        if not text:
            return text
        
        # 移除首尾的引号
        text = text.strip('"\'')
        
        # 移除多余的空格和换行
        text = ' '.join(text.split())
        
        # 移除常见的AI回复前缀
        prefixes_to_remove = [
            "翻译结果：",
            "翻译：",
            "英文：",
            "English:",
            "Translation:",
            "Result:"
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        
        return text
    
    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """获取当前模型信息
        
        Returns:
            模型信息字典，失败时返回None
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": self.model},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"获取模型信息失败: {e}")
            return None
    
    def update_config(self) -> None:
        """更新配置（当配置文件改变时调用）"""
        self.base_url = config.get_ollama_url()
        self.model = config.get_ollama_model()
        self.translation_prompt = config.get_translation_prompt()
    
    def get_status(self) -> Dict[str, Any]:
        """获取客户端状态信息
        
        Returns:
            状态信息字典
        """
        return {
            "base_url": self.base_url,
            "model": self.model,
            "connected": self.test_connection(),
            "model_available": self.check_model_available()
        }


# 全局Ollama客户端实例
ollama_client = OllamaClient()