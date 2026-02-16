"""
添加快捷键对话框模块
负责捕获按键、显示窗口列表、保存配置
"""
import customtkinter as ctk
from core import config, hotkey, window as window_mgr


class AddDialog:
    def __init__(self, parent, hwnd):
        """
        初始化添加对话框
        Args:
            parent: 父窗口
            hwnd: 窗口句柄，用于注册热键
        """
        self.parent = parent
        self.hwnd = hwnd
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

        # 窗口列表
        self.window_listbox = ctk.CTkTextbox(
            self.window_frame,
            yscrollcommand=scrollbar.set,
            font=ctk.CTkFont(size=13)
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

        # 必须有修饰键或者按的是功能键
        if not modifiers and key_name not in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6',
                                               'F7', 'F8', 'F9', 'F10', 'F11', 'F12']:
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

        # 显示分组后的窗口
        self.window_listbox.delete("1.0", "end")
        self.window_listbox.insert("end", "可用窗口:\n\n")

        self.window_options = []
        idx = 0

        for class_name, wins in groups.items():
            # 只显示有标题的窗口
            valid_wins = [w for w in wins if w['title']]
            if not valid_wins:
                continue

            self.window_listbox.insert("end", f"【{class_name}】\n")

            for w in valid_wins:
                idx += 1
                self.window_options.append(w)
                self.window_listbox.insert("end", f"  {idx}. {w['title']}\n")

            self.window_listbox.insert("end", "\n")

        # 绑定点击事件
        self.window_listbox.bind("<Button-1>", self.on_window_select)
        self.window_listbox.configure(state="disabled")

        # 启用确定按钮
        self.confirm_button.configure(state="normal")

    def on_window_select(self, event):
        """窗口选择事件"""
        # 获取点击位置对应的行
        try:
            index = self.window_listbox.index(f"@{event.x},{event.y}")
        except:
            return

        # 解析行号
        line_num = int(index.split('.')[0])

        # 计算选中的是哪个窗口（跳过标题行）
        # 简单逻辑：第一个可点击的窗口对应 idx=1
        if line_num >= 3:  # 跳过前面的说明行
            window_idx = line_num - 3
            if 0 <= window_idx < len(self.window_options):
                self.selected_window = self.window_options[window_idx]
                # 高亮显示
                self.window_listbox.configure(state="normal")
                self.window_listbox.tag_add("selected", f"{line_num}.0", f"{line_num}.end")
                self.window_listbox.tag_config("selected", foreground="green")
                self.window_listbox.configure(state="disabled")

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

        # 关闭对话框
        self.dialog.destroy()

    def on_cancel(self):
        """取消按钮点击"""
        self.dialog.destroy()
