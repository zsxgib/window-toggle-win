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
from ctypes import windll, Structure, c_long, c_ulong, byref

import customtkinter as ctk

from core import config, hotkey
from gui.main_window import MainWindow
from utils.tray import TrayIcon


# 定义 MSG 结构体
class MSG(Structure):
    _fields_ = [
        ("hwnd", c_long),
        ("message", c_ulong),
        ("wParam", c_long),
        ("lParam", c_long),
        ("time", c_long),
        ("pt_x", c_long),
        ("pt_y", c_long)
    ]


class WindowToggleApp:
    def __init__(self):
        # 创建 customtkinter 应用
        self.app = ctk.CTk()
        self.app.title("Window Toggle")
        self.app.geometry("500x400")

        # 先创建主窗口（会创建 tkinter 窗口）
        self.main_window = MainWindow(self.app, None)

        # 获取窗口句柄（在窗口创建之后）
        self.app.update()  # 强制更新以获取正确的句柄
        self.hwnd = self.get_hwnd()

        # 设置 hwnd 到主窗口
        self.main_window.hwnd = self.hwnd

        # 注册热键
        self.main_window.register_all_hotkeys()

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

    def get_hwnd(self):
        """获取 tkinter 窗口的正确句柄"""
        # 方法：通过窗口标题查找
        def find_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title == "Window Toggle":
                    return False  # 找到后停止枚举
            return True

        win32gui.EnumWindows(find_callback, None)

        # 如果找不到，用备用方法
        try:
            return int(self.app.winfo_id())
        except:
            return win32gui.GetForegroundWindow()

    def message_loop(self):
        """Win32 消息循环（在单独线程中运行）"""
        # 使用 windll 调用 PeekMessage
        user32 = windll.user32

        msg = MSG()

        print(f"Message loop started, hwnd={self.hwnd}")  # 调试

        while self.running:
            # 使用 PeekMessage 非阻塞获取消息
            ret = user32.PeekMessageA(byref(msg), None, 0, 0, 1)  # PM_REMOVE = 1
            if ret:
                if msg.message == 0x0002:  # WM_DESTROY
                    break

                # 调试：打印所有消息
                if msg.message != 0x0113:  # 忽略 WM_TIMER
                    print(f"Message: {msg.message}, wParam={msg.wParam}")  # 调试

                if msg.message == hotkey.WM_HOTKEY:
                    # 热键触发
                    shortcut_id = msg.wParam
                    print(f">>> Hotkey triggered: {shortcut_id}")  # 调试
                    self.app.after(0, lambda: self.main_window.on_hotkey_triggered(shortcut_id))

                user32.TranslateMessage(byref(msg))
                user32.DispatchMessageA(byref(msg))
            else:
                # 没有消息时短暂休眠，避免CPU占用过高
                time.sleep(0.05)

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
