"""
添加快捷键对话框模块
负责捕获按键、显示窗口列表、保存配置
"""
import customtkinter as ctk
import tkinter as tk
from pynput import keyboard
from core import config, hotkey, window as window_mgr


class AddDialog:
    def __init__(self, parent, hwnd, on_close_callback=None):
        """
        初始化添加对话框
        Args:
            parent: 父窗口
            hwnd: 窗口句柄，用于注册热键
            on_close_callback: 对话框关闭后的回调函数
        """
        self.parent = parent
        self.hwnd = hwnd
        self.on_close_callback = on_close_callback
        self.result = None
        self.selected_hotkey = None
        self.selected_window = None
        self.capture_mode = True  # True=捕获按键, False=选择窗口
        self.listener = None

        # 创建对话框
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("添加快捷键")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()

        # 开始捕获键盘
        self.start_keyboard_listener()

    def create_widgets(self):
        """创建界面元素"""
        # 步骤说明
        self.step_label = ctk.CTkLabel(
            self.dialog,
            text="步骤 1: 请按下要使用的快捷键",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.step_label.pack(pady=20)

        # 快捷键显示
        self.hotkey_label = ctk.CTkLabel(
            self.dialog,
            text="等待按键...（按 ESC 取消）",
            font=ctk.CTkFont(size=24),
            text_color="gray"
        )
        self.hotkey_label.pack(pady=10)

        # 说明
        info = ctk.CTkLabel(
            self.dialog,
            text="例如: F1, Ctrl+F1, Alt+F2, Ctrl+Shift+F3",
            font=ctk.CTkFont(size=12)
        )
        info.pack(pady=(0, 20))

        # 窗口列表框架（初始隐藏）
        self.window_frame = ctk.CTkFrame(self.dialog)
        self.window_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.window_frame.pack_forget()  # 隐藏

        # 窗口列表说明
        window_label = ctk.CTkLabel(
            self.window_frame,
            text="步骤 2: 选择目标窗口",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        window_label.pack(pady=10)

        # 滚动条
        scrollbar = ctk.CTkScrollbar(self.window_frame)
        scrollbar.pack(side="right", fill="y")

        # 使用 tkinter Listbox 支持选中
        self.window_listbox = tk.Listbox(
            self.window_frame,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 12),
            bg="#1f1f1f",
            fg="white",
            selectbackground="#3b8ed0",
            selectforeground="white",
            bd=0,
            highlightthickness=0
        )
        self.window_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self.window_listbox.yview)

        # 按钮框架
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(pady=15)

        self.confirm_button = ctk.CTkButton(
            button_frame,
            text="确定",
            width=100,
            command=self.on_confirm,
            state="disabled"
        )
        self.confirm_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="取消",
            width=100,
            fg_color="gray",
            command=self.on_cancel
        )
        cancel_button.pack(side="left", padx=10)

        # 绑定 ESC 键
        self.dialog.bind("<Escape>", lambda e: self.on_cancel())

    def start_keyboard_listener(self):
        """启动键盘监听器"""
        self.listener = keyboard.Listener(
            on_press=self.on_key_press
        )
        self.listener.start()

    def on_key_press(self, key):
        """键盘按键事件"""
        if not self.capture_mode:
            return

        try:
            # 获取按键名称
            key_name = key.char
        except AttributeError:
            # 功能键等特殊按键
            key_name = str(key).replace('Key.', '')

        # ESC 取消
        if key_name == 'esc':
            self.on_cancel()
            return

        # 跳过修饰键单独按下
        if key_name in ['shift', 'ctrl', 'alt', 'win']:
            return

        # 获取当前按下的修饰键
        modifiers = []
        if keyboard.Key.ctrl in keyboard._current_keys:
            modifiers.append('Ctrl')
        if keyboard.Key.alt in keyboard._current_keys:
            modifiers.append('Alt')
        if keyboard.Key.shift in keyboard._current_keys:
            modifiers.append('Shift')
        if keyboard.Key.cmd in keyboard._current_keys:
            modifiers.append('Win')

        # 保存捕获的快捷键
        mod_str = '+'.join(modifiers) if modifiers else ''

        # 格式化显示
        if mod_str:
            hotkey_str = f"{mod_str}+{key_name}"
        else:
            hotkey_str = key_name

        self.selected_hotkey = {
            'modifiers': mod_str,
            'key': key_name
        }

        # 显示捕获的快捷键
        self.hotkey_label.configure(text=hotkey_str, text_color="green")

        # 切换到窗口选择模式
        self.capture_mode = False
        self.show_window_list()

    def show_window_list(self):
        """显示窗口列表"""
        # 停止键盘监听
        if self.listener:
            self.listener.stop()
            self.listener = None

        # 切换界面
        self.step_label.configure(text="步骤 2: 选择目标窗口")
        self.window_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 枚举窗口
        windows = window_mgr.get_all_windows()

        # 按窗口类分组
        groups = window_mgr.group_by_class(windows)

        # 清空列表
        self.window_listbox.delete(0, "end")

        self.window_options = []

        for class_name, wins in groups.items():
            # 只显示有标题的窗口
            valid_wins = [w for w in wins if w['title']]
            if not valid_wins:
                continue

            # 添加分组标题
            self.window_listbox.insert("end", f"--- {class_name} ---")
            self.window_listbox.itemconfig(self.window_listbox.size() - 1, fg="#888888", selectbackground="#1f1f1f")

            for w in valid_wins:
                self.window_options.append(w)
                self.window_listbox.insert("end", f"  {w['title']}")

        # 绑定选择事件
        self.window_listbox.bind("<<ListboxSelect>>", self.on_window_select)

        # 启用确定按钮
        self.confirm_button.configure(state="normal")

    def on_window_select(self, event):
        """窗口选择事件"""
        selection = self.window_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        selected_text = self.window_listbox.get(idx)

        # 检查是否选中分组标题
        if selected_text.startswith("---"):
            self.window_listbox.selection_clear(idx)
            return

        # 计算实际窗口索引
        window_idx = idx
        for i in range(idx):
            if self.window_listbox.get(i).startswith("---"):
                window_idx -= 1

        if 0 <= window_idx < len(self.window_options):
            self.selected_window = self.window_options[window_idx]

    def on_confirm(self):
        """确定按钮点击"""
        if not self.selected_hotkey or not self.selected_window:
            return

        # 保存配置
        shortcut = {
            'key': self.selected_hotkey['key'],
            'modifiers': self.selected_hotkey['modifiers'],
            'window_title': self.selected_window['title'],
            'window_class': self.selected_window['class_name']
        }

        saved = config.add_shortcut(shortcut)

        if saved:
            hotkey.register(
                self.hwnd,
                saved['id'],
                saved['modifiers'],
                saved['key']
            )

        self.dialog.destroy()

        if self.on_close_callback:
            self.on_close_callback()

    def on_cancel(self):
        """取消按钮点击"""
        # 停止键盘监听
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.dialog.destroy()
