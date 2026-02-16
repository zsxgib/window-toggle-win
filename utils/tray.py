"""
系统托盘模块
使用 pystray 实现系统托盘图标
"""
import os
import threading
from PIL import Image, ImageDraw

import pystray
import customtkinter as ctk


class TrayIcon:
    def __init__(self, app, show_callback, quit_callback):
        """
        初始化托盘图标
        Args:
            app: CTk 实例
            show_callback: 显示窗口的回调函数
            quit_callback: 退出程序的回调函数
        """
        self.app = app
        self.show_callback = show_callback
        self.quit_callback = quit_callback
        self.running = True

        # 创建图标图像
        self.icon_image = self.create_icon_image()

        # 创建托盘图标
        self.icon = pystray.Icon(
            "window-toggle",
            self.icon_image,
            "Window Toggle",
            self.create_menu()
        )

        # 在单独线程中运行托盘
        self.icon_thread = threading.Thread(target=self.run, daemon=True)
        self.icon_thread.start()

    def create_icon_image(self):
        """创建托盘图标图像"""
        # 创建 64x64 的图像
        image = Image.new('RGB', (64, 64), color='black')
        draw = ImageDraw.Draw(image)

        # 画一个简单的窗口图标
        # 外框
        draw.rectangle([8, 16, 56, 48], outline='white', width=2)
        # 窗口标题栏
        draw.rectangle([8, 16, 56, 24], fill='white')
        # 窗口内容
        draw.rectangle([12, 28, 52, 44], outline='white', width=1)

        return image

    def create_menu(self):
        """创建托盘菜单"""
        menu = pystray.Menu(
            pystray.MenuItem("显示", self.on_show),
            pystray.MenuItem("退出", self.on_quit)
        )
        return menu

    def run(self):
        """运行托盘图标"""
        self.icon.run()

    def on_show(self, icon, item):
        """显示窗口"""
        if self.show_callback:
            self.app.after(0, self.show_callback)

    def on_quit(self, icon, item):
        """退出程序"""
        self.running = False
        self.icon.stop()
        if self.quit_callback:
            self.app.after(0, self.quit_callback)


def create_tray_icon(app, show_callback, quit_callback):
    """
    创建托盘图标
    Args:
        app: CTk 实例
        show_callback: 显示窗口的回调函数
        quit_callback: 退出程序的回调函数
    """
    return TrayIcon(app, show_callback, quit_callback)
