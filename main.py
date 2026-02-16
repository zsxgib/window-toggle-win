"""
Window Toggle 主程序
使用 keyboard 库实现热键
"""
import sys
import os

import customtkinter as ctk

from core import config, hotkey
from gui.main_window import MainWindow
from utils.tray import TrayIcon


class WindowToggleApp:
    def __init__(self):
        # 创建 customtkinter 应用
        self.app = ctk.CTk()
        self.app.title("Window Toggle")
        self.app.geometry("500x400")

        # 创建主窗口
        self.main_window = MainWindow(self.app, None)

        # 注册热键
        self.main_window.register_all_hotkeys()

        # 创建托盘图标
        self.tray = TrayIcon(
            self.app,
            show_callback=self.show_window,
            quit_callback=self.quit_app
        )

        # 处理窗口关闭事件
        self.app.protocol("WM_DELETE_WINDOW", self.on_close)

        # 启动 GUI
        self.app.mainloop()

    def show_window(self):
        """显示窗口"""
        self.app.deiconify()
        self.app.lift()
        self.app.focus_force()

    def on_close(self):
        """窗口关闭事件"""
        # 隐藏到托盘而不是退出
        self.app.withdraw()

    def quit_app(self):
        """退出程序"""
        hotkey.unregister_all()
        self.app.quit()


def main():
    """主函数"""
    try:
        app = WindowToggleApp()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
