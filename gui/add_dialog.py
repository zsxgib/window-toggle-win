"""
添加快捷键对话框模块
负责捕获按键、显示窗口列表、保存配置
"""
import customtkinter as ctk
import tkinter as tk
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

        # 创建对话框
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("添加快捷键")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 绑定键盘事件
        self.dialog.bind("<KeyPress>", self.on_key_press)

        self.create_widgets()
        self.capture_hotkey()

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
            text="等待按键...",
            font=ctk.CTkFont(size=24),
            text_color="gray"
        )
        self.hotkey_label.pack(pady=10)

        # 说明
        info = ctk.CTkLabel(
            self.dialog,
            text="例如: Ctrl+Alt+F1, Super+F2, F3",
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

    def capture_hotkey(self):
        """开始捕获快捷键"""
        self.step_label.configure(text="步骤 1: 请按下要使用的快捷键")
        self.hotkey_label.configure(text="等待按键...", text_color="gray")
        self.hotkey_label.focus_set()

    def on_key_press(self, event):
        """
        键盘按键事件
        Args:
            event: 键盘事件
        """
        if not self.capture_mode:
            return

        # 过滤掉 Alt 键本身（防止误判）
        if event.keycode == 18:  # Alt 键的 keycode
            return

        # 获取修饰键状态
        modifiers = []
        if event.state & 1:  # Shift
            modifiers.append('Shift')
        if event.state & 4:  # Ctrl
            modifiers.append('Ctrl')
        if event.state & 8:  # Alt
            modifiers.append('Alt')
        if event.state & 0x100:  # Win
            modifiers.append('Win')

        # 获取按键名称
        key_name = self.get_key_name(event.keycode)

        if not key_name:
            return

        # 必须有修饰键或者按的是功能键/数字字母键
        allowed_keys = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6',
                       'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
                       'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                       'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                       '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        if not modifiers and key_name not in allowed_keys:
            return

        # 保存捕获的快捷键
        mod_str = '+'.join(modifiers) if modifiers else ''
        self.selected_hotkey = {
            'modifiers': mod_str,
            'key': key_name
        }

        # 显示捕获的快捷键
        if mod_str:
            hotkey_str = f"{mod_str}+{key_name}"
        else:
            hotkey_str = key_name

        self.hotkey_label.configure(text=hotkey_str, text_color="green")

        # 切换到窗口选择模式
        self.capture_mode = False
        self.show_window_list()

    def get_key_name(self, keycode):
        """
        根据 keycode 获取键名
        Args:
            keycode: 键盘码
        Returns:
            str: 键名
        """
        # 功能键映射
        f_keys = {
            112: 'F1', 113: 'F2', 114: 'F3', 115: 'F4',
            116: 'F5', 117: 'F6', 118: 'F7', 119: 'F8',
            120: 'F9', 121: 'F10', 122: 'F11', 123: 'F12'
        }

        if keycode in f_keys:
            return f_keys[keycode]

        # 字母键
        if 65 <= keycode <= 90:
            return chr(keycode)

        # 数字键
        if 48 <= keycode <= 57:
            return chr(keycode)

        return None

    def show_window_list(self):
        """显示窗口列表"""
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

            # 添加分组标题（作为不可选择的项）
            self.window_listbox.insert("end", f"--- {class_name} ---")
            # 设置该项不可选择
            self.window_listbox.itemconfig(self.window_listbox.size() - 1, fg="#888888", selectbackground="#1f1f1f")

            for w in valid_wins:
                self.window_options.append(w)
                # 只显示窗口标题
                self.window_listbox.insert("end", f"  {w['title']}")

        # 绑定选择事件
        self.window_listbox.bind("<<ListboxSelect>>", self.on_window_select)

        # 启用确定按钮
        self.confirm_button.configure(state="normal")

    def on_window_select(self, event):
        """窗口选择事件"""
        # 获取选中的索引
        selection = self.window_listbox.curselection()
        if not selection:
            return

        idx = selection[0]

        # 检查是否选中的是分组标题（奇数行，因为每组后面还有子项）
        # 分组标题不可选择，这里我们用一种简单方法：
        # 检查该项的文本是否是分组标题格式
        selected_text = self.window_listbox.get(idx)
        if selected_text.startswith("---"):
            # 取消选择
            self.window_listbox.selection_clear(idx)
            return

        # 计算实际窗口索引（跳过分组标题）
        # 找到该窗口在 window_options 中的索引
        # 因为每个分组标题占一行
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
            # 注册热键
            hotkey.register(
                self.hwnd,
                saved['id'],
                saved['modifiers'],
                saved['key']
            )

            # 获取主窗口实例并设置回调
            # 通过 parent 查找主窗口
            from gui.main_window import MainWindow
            # 这里简化处理：让回调在 on_close_callback 中统一处理

        # 关闭对话框
        self.dialog.destroy()

        # 调用关闭回调
        if self.on_close_callback:
            self.on_close_callback()

    def on_cancel(self):
        """取消按钮点击"""
        self.dialog.destroy()
