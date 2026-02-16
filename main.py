"""
Window Toggle 主程序
整合 GUI、热键消息循环和系统托盘
"""
import sys
import os
import threading
import time

import win32gui
import win32con
import win32api

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

        # 获取窗口句柄
        self.hwnd = int(self.app.winfo_id())

        # 创建主窗口
        self.main_window = MainWindow(self.app, self.hwnd)

        # 启动 Win32 消息处理线程
        self.running = True
        self.msg_thread = threading.Thread(target=self.message_loop, daemon=True)
        self.msg_thread.start()

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

    def message_loop(self):
        """Win32 消息循环（在单独线程中运行）"""
        msg = win32gui.MSG()

        while self.running:
            # 使用 PeekMessage 非阻塞获取消息
            if win32gui.PeekMessage(msg, None, 0, 0, win32con.PM_REMOVE):
                if msg.message == win32con.WM_DESTROY:
                    break

                if msg.message == hotkey.WM_HOTKEY:
                    # 热键触发
                    shortcut_id = msg.wParam
                    self.app.after(0, lambda: self.main_window.on_hotkey_triggered(shortcut_id))

                win32gui.TranslateMessage(msg)
                win32gui.DispatchMessage(msg)
            else:
                # 没有消息时短暂休眠，避免CPU占用过高
                time.sleep(0.01)

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
        self.running = False
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
