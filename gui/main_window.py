"""
主窗口模块
显示快捷键列表，提供添加/删除功能
"""
import customtkinter as ctk
import tkinter as tk
from core import config, hotkey, window as window_mgr


class MainWindow:
    def __init__(self, app, hwnd=None):
        """
        初始化主窗口
        Args:
            app: CTk 实例
            hwnd: 窗口句柄，用于注册热键（可以后设置）
        """
        self.app = app
        self.hwnd = hwnd
        self.registered_hotkeys = {}

        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 创建主窗口
        self.app.title("Window Toggle")
        self.app.geometry("500x400")

        # 创建界面元素
        self.create_widgets()

        # 加载配置并刷新列表
        self.refresh_list()

    def create_widgets(self):
        """创建界面元素"""
        # 标题
        title = ctk.CTkLabel(
            self.app,
            text="Window Toggle",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        # 说明
        info = ctk.CTkLabel(
            self.app,
            text="按下配置的快捷键可切换窗口显示/隐藏",
            font=ctk.CTkFont(size=12)
        )
        info.pack(pady=(0, 10))

        # 列表框框架
        list_frame = ctk.CTkFrame(self.app)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        # 使用 tkinter Listbox 支持选中
        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 12),
            bg="#1f1f1f",
            fg="white",
            selectbackground="#3b8ed0",
            selectforeground="white",
            bd=0,
            highlightthickness=0,
            justify="left"
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self.listbox.yview)

        # 绑定选择事件
        self.listbox.bind("<<ListboxSelect>>", self.on_list_select)

        # 按钮框架
        button_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        button_frame.pack(pady=15)

        # 添加按钮
        self.add_button = ctk.CTkButton(
            button_frame,
            text="+ 添加",
            width=100,
            command=self.on_add_click
        )
        self.add_button.pack(side="left", padx=10)

        # 删除按钮
        self.delete_button = ctk.CTkButton(
            button_frame,
            text="- 删除",
            width=100,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.on_delete_click
        )
        self.delete_button.pack(side="left", padx=10)

        # 保存选中的索引（用于删除）
        self.listbox.bind("<Button-1>", self.on_list_click)

    def refresh_list(self):
        """刷新快捷键列表"""
        # 清空列表
        self.listbox.delete(0, "end")

        # 加载配置
        data = config.load()
        shortcuts = data.get('shortcuts', [])

        if not shortcuts:
            self.listbox.insert("end", "暂无配置的快捷键")
            self.listbox.insert("end", "点击「添加」配置新快捷键")
        else:
            for s in shortcuts:
                mod = s.get('modifiers', '')
                key = s.get('key', '')
                title = s.get('window_title', '')

                if mod:
                    hotkey_str = f"{mod}+{key}"
                else:
                    hotkey_str = key

                self.listbox.insert("end", f"{hotkey_str} → {title}")

    def register_all_hotkeys(self):
        """注册所有已配置的热键"""
        data = config.load()
        shortcuts = data.get('shortcuts', [])

        for s in shortcuts:
            shortcut_id = s.get('id')
            modifiers = s.get('modifiers', '')
            key = s.get('key', '')

            if shortcut_id and key:
                # 保存窗口信息（包括 hwnd）
                self.registered_hotkeys[shortcut_id] = {
                    'modifiers': modifiers,
                    'key': key,
                    'window_title': s.get('window_title', ''),
                    'window_class': s.get('window_class', ''),
                    'hwnd': s.get('hwnd')
                }

                # 注册热键并设置回调
                if hotkey.register(self.hwnd, shortcut_id, modifiers, key):
                    # 设置回调
                    window_class = s.get('window_class', '')
                    hotkey.set_callback(shortcut_id, lambda sid=shortcut_id: self.on_hotkey_triggered(sid))

    def on_add_click(self):
        """添加按钮点击事件"""
        from gui.add_dialog import AddDialog

        # 保存主窗口引用
        main_window = self

        # 定义对话框关闭后的回调
        def on_dialog_close():
            main_window.refresh_list()
            main_window.register_all_hotkeys()

        # 创建对话框，传入回调函数
        dialog = AddDialog(self.app, self.hwnd, on_dialog_close)

    def on_delete_click(self):
        """删除按钮点击事件"""
        # 获取选中的项
        selection = self.listbox.curselection()
        if not selection:
            return

        idx = selection[0]

        # 加载配置
        data = config.load()
        shortcuts = data.get('shortcuts', [])

        if not shortcuts or idx >= len(shortcuts):
            return

        # 获取要删除的快捷键
        shortcut = shortcuts[idx]
        shortcut_id = shortcut.get('id')

        # 注销热键（通过重新注册所有来清除）
        hotkey.unregister_all()
        self.registered_hotkeys.clear()

        # 删除配置
        config.remove_shortcut(shortcut_id)

        # 刷新列表
        self.refresh_list()

        # 重新注册剩余热键
        self.register_all_hotkeys()

    def on_list_select(self, event):
        """列表选择事件"""
        pass

    def on_list_click(self, event):
        """列表点击事件"""
        pass

    def on_hotkey_triggered(self, shortcut_id):
        """
        热键触发事件
        Args:
            shortcut_id: 热键 ID
        """
        if shortcut_id not in self.registered_hotkeys:
            return

        shortcut_info = self.registered_hotkeys[shortcut_id]
        
        # 优先使用保存的 hwnd
        hwnd = shortcut_info.get('hwnd')
        
        # 如果 hwnd 无效，尝试用 window_class 查找
        if not hwnd or not window_mgr.is_valid_window(hwnd):
            window_class = shortcut_info.get('window_class', '')
            if window_class:
                hwnd = window_mgr.find_window_by_class(window_class)
        
        if hwnd:
            # 切换窗口显示/隐藏
            result = window_mgr.toggle_window(hwnd)
            if not result:
                print(f"[hotkey] 窗口操作失败，可能需要重新配置")
        else:
            print(f"[hotkey] 未找到窗口，可能需要重新配置")
