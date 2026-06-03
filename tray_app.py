# -*- coding: utf-8 -*-
"""
系统托盘应用模块
负责系统托盘图标显示和设置界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional
import pystray
from PIL import Image, ImageDraw
from config import config
from logger import logger
from ollama_client import ollama_client


class SettingsWindow:
    """设置窗口类"""
    
    def __init__(self):
        """初始化设置窗口"""
        self.window = None
        self.hotkey_var = None
        self.ollama_url_var = None
        self.ollama_model_var = None
        self.auto_start_var = None
        self.status_label = None
    
    def show(self):
        """显示设置窗口"""
        # 使用线程安全的方式显示窗口
        print("设置窗口请求已接收")
        print("由于线程安全限制，设置功能暂时通过控制台显示")
        print("当前配置:")
        print(f"  快捷键: {config.get_hotkey()}")
        print(f"  Ollama地址: {config.get_ollama_url()}")
        print(f"  模型: {config.get_ollama_model()}")
        print(f"  自启动: {config.get_auto_start()}")
        print("如需修改配置，请直接编辑config.json文件")
    
    def _create_window(self):
        """创建设置窗口"""
        self.window = tk.Toplevel()
        self.window.title(config.get_window_title() + " - 设置")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        # 设置窗口图标（如果有的话）
        try:
            self.window.iconbitmap(default="icon.ico")
        except:
            pass
        
        # 创建主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 快捷键设置区域
        self._create_hotkey_section(main_frame)
        
        # Ollama设置区域
        self._create_ollama_section(main_frame)
        
        # 其他设置区域
        self._create_other_section(main_frame)
        
        # 状态显示区域
        self._create_status_section(main_frame)
        
        # 按钮区域
        self._create_button_section(main_frame)
        
        # 加载当前配置
        self._load_current_config()
        
        # 更新状态
        self._update_status()
        
        # 设置窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _create_hotkey_section(self, parent):
        """创建快捷键设置区域"""
        # 快捷键设置框架
        hotkey_frame = ttk.LabelFrame(parent, text="快捷键设置", padding="10")
        hotkey_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 快捷键输入
        ttk.Label(hotkey_frame, text="全局快捷键:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.hotkey_var = tk.StringVar()
        hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, width=20)
        hotkey_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 测试按钮
        test_hotkey_btn = ttk.Button(hotkey_frame, text="测试", command=self._test_hotkey)
        test_hotkey_btn.grid(row=0, column=2, padx=(0, 10))
        
        # 重置按钮
        reset_hotkey_btn = ttk.Button(hotkey_frame, text="重置", command=self._reset_hotkey)
        reset_hotkey_btn.grid(row=0, column=3)
        
        # 说明文本
        help_text = "格式示例: ctrl+shift+t, alt+f1, ctrl+alt+z"
        ttk.Label(hotkey_frame, text=help_text, font=("Arial", 8), foreground="gray").grid(
            row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0)
        )
        
        hotkey_frame.columnconfigure(1, weight=1)
    
    def _create_ollama_section(self, parent):
        """创建Ollama设置区域"""
        # Ollama设置框架
        ollama_frame = ttk.LabelFrame(parent, text="Ollama设置", padding="10")
        ollama_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 服务地址
        ttk.Label(ollama_frame, text="服务地址:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.ollama_url_var = tk.StringVar()
        url_entry = ttk.Entry(ollama_frame, textvariable=self.ollama_url_var, width=30)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 连接测试按钮
        test_conn_btn = ttk.Button(ollama_frame, text="测试连接", command=self._test_connection)
        test_conn_btn.grid(row=0, column=2)
        
        # 模型名称
        ttk.Label(ollama_frame, text="模型名称:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.ollama_model_var = tk.StringVar()
        model_entry = ttk.Entry(ollama_frame, textvariable=self.ollama_model_var, width=30)
        model_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        # 检查模型按钮
        check_model_btn = ttk.Button(ollama_frame, text="检查模型", command=self._check_model)
        check_model_btn.grid(row=1, column=2, pady=(10, 0))
        
        ollama_frame.columnconfigure(1, weight=1)
    
    def _create_other_section(self, parent):
        """创建其他设置区域"""
        # 其他设置框架
        other_frame = ttk.LabelFrame(parent, text="其他设置", padding="10")
        other_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 开机自启动
        self.auto_start_var = tk.BooleanVar()
        auto_start_check = ttk.Checkbutton(
            other_frame, 
            text="开机自启动", 
            variable=self.auto_start_var
        )
        auto_start_check.grid(row=0, column=0, sticky=tk.W)
    
    def _create_status_section(self, parent):
        """创建状态显示区域"""
        # 状态框架
        status_frame = ttk.LabelFrame(parent, text="状态信息", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态标签
        self.status_label = ttk.Label(status_frame, text="正在检查状态...", font=("Arial", 9))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        status_frame.columnconfigure(0, weight=1)
    
    def _create_button_section(self, parent):
        """创建按钮区域"""
        # 按钮框架
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 保存按钮
        save_btn = ttk.Button(button_frame, text="保存设置", command=self._save_settings)
        save_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=self._on_window_close)
        cancel_btn.grid(row=0, column=1, padx=(0, 10))
        
        # 刷新状态按钮
        refresh_btn = ttk.Button(button_frame, text="刷新状态", command=self._update_status)
        refresh_btn.grid(row=0, column=2)
    
    def _load_current_config(self):
        """加载当前配置到界面"""
        self.hotkey_var.set(config.get_hotkey())
        self.ollama_url_var.set(config.get_ollama_url())
        self.ollama_model_var.set(config.get_ollama_model())
        self.auto_start_var.set(config.get_auto_start())
    
    def _test_hotkey(self):
        """测试快捷键格式"""
        hotkey = self.hotkey_var.get().strip()
        if not hotkey:
            messagebox.showwarning("警告", "请输入快捷键")
            return
        
        # 延迟导入避免循环导入
        from hotkey_listener import hotkey_listener
        if hotkey_listener.test_hotkey(hotkey):
            messagebox.showinfo("成功", "快捷键格式有效")
        else:
            messagebox.showerror("错误", "快捷键格式无效")
    
    def _reset_hotkey(self):
        """重置快捷键为默认值"""
        self.hotkey_var.set("ctrl+alt+q")
    
    def _test_connection(self):
        """测试Ollama连接"""
        url = self.ollama_url_var.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入服务地址")
            return
        
        # 临时更新配置进行测试
        original_url = config.get_ollama_url()
        config.config_data["ollama_url"] = url
        ollama_client.update_config()
        
        if ollama_client.test_connection():
            messagebox.showinfo("成功", "连接成功")
        else:
            messagebox.showerror("错误", "连接失败")
        
        # 恢复原配置
        config.config_data["ollama_url"] = original_url
        ollama_client.update_config()
    
    def _check_model(self):
        """检查模型可用性"""
        model = self.ollama_model_var.get().strip()
        if not model:
            messagebox.showwarning("警告", "请输入模型名称")
            return
        
        # 临时更新配置进行测试
        original_model = config.get_ollama_model()
        config.config_data["ollama_model"] = model
        ollama_client.update_config()
        
        if ollama_client.check_model_available():
            messagebox.showinfo("成功", "模型可用")
        else:
            messagebox.showerror("错误", "模型不可用")
        
        # 恢复原配置
        config.config_data["ollama_model"] = original_model
        ollama_client.update_config()
    
    def _save_settings(self):
        """保存设置"""
        try:
            # 验证快捷键
            hotkey = self.hotkey_var.get().strip()
            if not hotkey:
                messagebox.showwarning("警告", "请输入快捷键")
                return
            
            # 延迟导入避免循环导入
            from hotkey_listener import hotkey_listener
            if not hotkey_listener.test_hotkey(hotkey):
                messagebox.showerror("错误", "快捷键格式无效")
                return
            
            # 验证URL
            url = self.ollama_url_var.get().strip()
            if not url:
                messagebox.showwarning("警告", "请输入服务地址")
                return
            
            # 验证模型名称
            model = self.ollama_model_var.get().strip()
            if not model:
                messagebox.showwarning("警告", "请输入模型名称")
                return
            
            # 保存配置
            config.set_hotkey(hotkey)
            config.set_ollama_url(url)
            config.set_ollama_model(model)
            config.set_auto_start(self.auto_start_var.get())
            
            # 更新ollama客户端配置
            ollama_client.update_config()
            
            # 更新快捷键监听器
            hotkey_listener.update_hotkey(hotkey)
            
            messagebox.showinfo("成功", "设置已保存")
            self._update_status()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {e}")
    
    def _update_status(self):
        """更新状态信息"""
        try:
            # 延迟导入避免循环导入
            from hotkey_listener import hotkey_listener
            # 获取各组件状态
            hotkey_status = "运行中" if hotkey_listener.is_listening() else "已停止"
            ollama_status = "连接正常" if ollama_client.test_connection() else "连接失败"
            model_status = "可用" if ollama_client.check_model_available() else "不可用"
            
            status_text = f"快捷键监听: {hotkey_status}\n"
            status_text += f"Ollama连接: {ollama_status}\n"
            status_text += f"模型状态: {model_status}"
            
            if self.status_label:
                self.status_label.config(text=status_text)
                
        except Exception as e:
            if self.status_label:
                self.status_label.config(text=f"状态检查失败: {e}")
    
    def _on_window_close(self):
        """窗口关闭事件"""
        if self.window:
            self.window.destroy()
            self.window = None


class TrayApp:
    """系统托盘应用类"""
    
    def __init__(self):
        """初始化托盘应用"""
        self.icon = None
        self.settings_window = SettingsWindow()
        self.is_running = False

    def notify(self, message: str, title: str = "InputTranslator") -> None:
        """发送托盘通知，托盘未就绪时退化为日志"""
        normalized_message = " ".join(str(message).split())
        if not normalized_message:
            return

        try:
            if self.icon and hasattr(self.icon, "notify"):
                self.icon.notify(normalized_message, title)
            else:
                logger.info(f"{title}: {normalized_message}")
        except Exception as exc:
            logger.warning(f"发送托盘通知失败: {exc}")
            logger.info(f"{title}: {normalized_message}")

    def set_status(self, status_text: Optional[str] = None) -> None:
        """临时更新托盘悬停提示，反馈当前翻译状态"""
        if not self.icon:
            return

        tooltip = config.get_tray_tooltip()
        if status_text:
            tooltip = f"{tooltip} - {status_text}"

        try:
            self.icon.title = tooltip
        except Exception as exc:
            logger.warning(f"更新托盘提示失败: {exc}")
    
    def _create_icon_image(self) -> Image.Image:
        """创建托盘图标
        
        Returns:
            PIL图像对象
        """
        # 创建一个简单的图标
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 绘制一个简单的翻译图标（两个矩形表示文档）
        # 背景矩形
        draw.rectangle([10, 10, 50, 50], fill=(0, 122, 204, 255), outline=(0, 100, 180, 255))
        
        # 前景矩形
        draw.rectangle([14, 14, 54, 54], fill=(255, 255, 255, 255), outline=(0, 122, 204, 255))
        
        # 绘制箭头表示翻译
        draw.polygon([(20, 25), (30, 20), (30, 30)], fill=(0, 122, 204, 255))
        draw.polygon([(34, 35), (44, 30), (44, 40)], fill=(0, 122, 204, 255))
        
        return image
    
    def _create_menu(self) -> pystray.Menu:
        """创建右键菜单
        
        Returns:
            pystray菜单对象
        """
        return pystray.Menu(
            pystray.MenuItem(
                "设置",
                self._show_settings,
                default=True
            ),
            pystray.MenuItem(
                "状态",
                self._show_status
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "测试翻译",
                self._test_translation
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "退出",
                self._quit_app
            )
        )
    
    def _show_settings(self, icon=None, item=None):
        """显示设置窗口"""
        # 在主线程中显示设置窗口
        threading.Thread(target=self.settings_window.show, daemon=True).start()
    
    def _show_status(self, icon=None, item=None):
        """显示状态信息"""
        def show_status_dialog():
            try:
                # 延迟导入避免循环导入
                from hotkey_listener import hotkey_listener
                hotkey_status = hotkey_listener.get_status()
                ollama_status = ollama_client.get_status()
                
                status_msg = f"快捷键: {hotkey_status['hotkey']}\n"
                status_msg += f"监听状态: {'运行中' if hotkey_status['is_running'] else '已停止'}\n\n"
                status_msg += f"Ollama地址: {ollama_status['base_url']}\n"
                status_msg += f"模型: {ollama_status['model']}\n"
                status_msg += f"连接状态: {'正常' if ollama_status['connected'] else '失败'}\n"
                status_msg += f"模型状态: {'可用' if ollama_status['model_available'] else '不可用'}"

                self.notify(status_msg, "当前状态")
            except Exception as e:
                logger.error(f"获取状态失败: {e}")
                self.notify(f"获取状态失败: {e}", "状态异常")
        
        threading.Thread(target=show_status_dialog, daemon=True).start()
    
    def _test_translation(self, icon=None, item=None):
        """测试翻译功能"""
        def test():
            try:
                self.notify("正在测试翻译能力...", "InputTranslator")
                # 测试翻译一个简单的中文句子
                test_text = "你好世界"
                result, message = ollama_client.translate_with_status(test_text)
                
                if result:
                    notify_message = f"翻译测试成功。原文: {test_text} 译文: {result}"
                    logger.info(notify_message)
                    self.notify(notify_message, "测试翻译")
                else:
                    logger.warning(f"翻译测试失败: {message}")
                    self.notify(message, "测试翻译失败")
                
            except Exception as e:
                logger.exception(f"翻译测试失败: {e}")
                self.notify(f"翻译测试失败: {e}", "测试翻译失败")
        
        threading.Thread(target=test, daemon=True).start()
    
    def _quit_app(self, icon=None, item=None):
        """退出应用"""
        logger.info("正在退出应用...")
        
        self.is_running = False
        
        # 停止快捷键监听
        try:
            from hotkey_listener import hotkey_listener
            hotkey_listener.stop_listening()
        except ImportError:
            pass
        
        # 停止托盘图标
        if self.icon:
            self.icon.stop()
            self.icon = None
    

    
    def start(self):
        """启动托盘应用"""
        try:
            # 创建托盘图标
            image = self._create_icon_image()
            menu = self._create_menu()
            
            self.icon = pystray.Icon(
                "InputTranslator",
                image,
                config.get_tray_tooltip(),
                menu
            )
            
            self.is_running = True
            logger.info("托盘应用启动成功")
            
            # 运行托盘图标（这会阻塞当前线程）
            self.icon.run()
            self.is_running = False
            return True
        except Exception as e:
            logger.exception(f"启动托盘应用失败: {e}")
            self.is_running = False
            return False
    
    def stop(self):
        """停止托盘应用"""
        self._quit_app()


# 全局托盘应用实例
tray_app = TrayApp()
