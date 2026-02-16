"""
主窗口模块
显示快捷键列表，提供添加/删除功能
"""
import customtkinter as ctk
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
        scrollbar = ctk.CTkScrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        # 快捷键列表
        self.listbox = ctk.CTkTextbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=ctk.CTkFont(size=14)
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self.listbox.yview)

        # 列表框只读，不能直接编辑
        self.listbox.configure(state="disabled")

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
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")

        # 加载配置
        data = config.load()
        shortcuts = data.get('shortcuts', [])

        if not shortcuts:
            self.listbox.insert("end", "暂无配置的快捷键\n")
            self.listbox.insert("end", "\n点击「添加」配置新快捷键")
        else:
            for s in shortcuts:
                mod = s.get('modifiers', '')
                key = s.get('key', '')
                title = s.get('window_title', '')

                if mod:
                    hotkey_str = f"{mod}+{key}"
                else:
                    hotkey_str = key

                self.listbox.insert("end", f"{hotkey_str} → {title}\n")

        self.listbox.configure(state="disabled")

    def register_all_hotkeys(self):
        """注册所有已配置的热键"""
        data = config.load()
        shortcuts = data.get('shortcuts', [])

        for s in shortcuts:
            shortcut_id = s.get('id')
            modifiers = s.get('modifiers', '')
            key = s.get('key', '')

            if shortcut_id and key:
                if hotkey.register(self.hwnd, shortcut_id, modifiers, key):
                    self.registered_hotkeys[shortcut_id] = {
                        'modifiers': modifiers,
                        'key': key,
                        'window_title': s.get('window_title', ''),
                        'window_class': s.get('window_class', '')
                    }

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
        # 获取当前选中的行
        try:
            current = self.listbox.index("insert")
        except:
            current = None

        if current is None:
            return

        # 计算对应哪一行（减去空行等）
        data = config.load()
        shortcuts = data.get('shortcuts', [])

        if not shortcuts:
            return

        # 根据点击位置估算要删除的快捷键
        line_num = int(current)
        # 粗略估算：每两行一个快捷键（因为有空行）
        idx = (line_num - 1) // 2

        if 0 <= idx < len(shortcuts):
            shortcut = shortcuts[idx]
            shortcut_id = shortcut.get('id')

            # 注销热键
            hotkey.unregister(self.hwnd, shortcut_id)

            # 删除配置
            config.remove_shortcut(shortcut_id)

            # 刷新列表
            self.refresh_list()

            # 重新注册剩余热键
            self.register_all_hotkeys()

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
        window_class = shortcut_info.get('window_class', '')

        if not window_class:
            return

        # 查找窗口
        hwnd = window_mgr.find_window_by_class(window_class)

        if hwnd:
            # 切换窗口显示/隐藏
            window_mgr.toggle_window(hwnd)
