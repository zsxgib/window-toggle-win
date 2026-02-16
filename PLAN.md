# window-toggle-win 实现计划

## 项目目标

将 Linux 下的 window-toggle 工具移植到 Windows，使用 Python 实现 GUI。

## 技术方案

### 技术栈

- **Python 3.8+**
- **pywin32** - Windows API（窗口操作、热键）
- **tkinter** - GUI（Python 内置）
- **pystray** - 系统托盘

### 文件结构

```
window-toggle-win/
├── main.py              # 入口，启动 GUI 和消息循环
├── gui/
│   ├── __init__.py
│   ├── main_window.py  # 主窗口（快捷键列表）
│   └── add_dialog.py   # 添加快捷键对话框
├── core/
│   ├── __init__.py
│   ├── hotkey.py       # 热键注册和管理
│   ├── window.py       # 窗口枚举和操作
│   └── config.py       # 配置文件读写
├── utils/
│   ├── __init__.py
│   └── logger.py       # 日志
├── requirements.txt
└── README.md
```

## 详细实现

### 1. 核心模块 (core/)

#### config.py - 配置管理

```python
# 功能：配置文件读写
# 方法：
- load() -> dict: 加载配置
- save(data): 保存配置
- add_shortcut(shortcut): 添加快捷键
- remove_shortcut(id): 删除快捷键

# 配置文件格式：
# {
#   "shortcuts": [
#     {
#       "id": 1,
#       "key": "F1",
#       "modifiers": "Ctrl+Alt",
#       "window_title": "Terminator",
#       "window_class": "Xterminal-emulator"
#     }
#   ]
# }
```

#### window.py - 窗口操作

```python
# 功能：枚举窗口、toggle 窗口
# 方法：
- get_all_windows() -> list: 获取所有可见窗口
- get_window_info(hwnd) -> dict: 获取窗口信息（标题、类名）
- group_by_class(windows) -> dict: 按窗口类分组
- toggle_window(hwnd): 切换窗口显示/隐藏
- is_window_visible(hwnd) -> bool: 判断窗口是否可见
- find_window_by_class(window_class) -> hwnd: 通过类名找窗口
```

#### hotkey.py - 热键管理

```python
# 功能：注册、注销全局热键
# 方法：
- register(hwnd, id, modifiers, key) -> bool: 注册热键
- unregister(id): 注销热键
- get_modifiers(vk) -> str: 虚拟键码转修饰键字符串
- get_key_name(vk) -> str: 虚拟键码转按键名
- WM_HOTKEY = 0x0312: 热键消息ID
```

### 2. GUI 模块 (gui/)

#### main_window.py - 主窗口

```python
class MainWindow:
    def __init__(self):
        # 创建主窗口
        # 显示快捷键列表（Listbox）
        # "添加" 按钮 → 打开添加对话框
        # "删除" 按钮 → 删除选中项

    def refresh_list(self):
        # 重新加载配置，刷新列表

    def on_add_click(self):
        # 打开添加对话框

    def on_delete_click(self):
        # 删除选中的快捷键

    def on_hotkey_triggered(self, shortcut_id):
        # 热键触发时调用 core/hotkey.py 切换窗口
```

#### add_dialog.py - 添加对话框

```python
class AddDialog:
    def __init__(self, parent):
        # 第一步：提示用户按下快捷键
        # 捕获按键组合，显示如 "Ctrl+Alt+F1"

        # 第二步：显示窗口列表
        # 调用 core/window.py 枚举窗口
        # 按应用分组显示

        # 第三步：用户选择窗口
        # 点击确定 → 保存配置 → 注册热键
```

### 3. 消息循环整合

关键问题：tkinter 和 pywin32 消息循环整合

```python
# main.py
import tkinter as tk
import win32gui
import win32con

def main():
    root = tk.Tk()
    app = MainWindow(root)

    # 创建隐藏窗口用于接收热键消息
    hwnd = windll.user32.GetParent(root.winfo_id())

    # 注册热键
    for shortcut in config.load()["shortcuts"]:
        hotkey.register(hwnd, shortcut["id"], shortcut["modifiers"], shortcut["key"])

    # 消息循环
    def msg_loop():
        # 处理 WM_HOTKEY 消息
        msg = win32gui.GetMessage(None, 0, 0)
        if msg[1]:
            if msg[0].message == win32con.WM_HOTKEY:
                shortcut_id = msg[0].wParam
                app.on_hotkey_triggered(shortcut_id)
            win32gui.TranslateMessage(msg[0])
            win32gui.DispatchMessage(msg[0])
        root.after(100, msg_loop)  # 同时处理 tkinter

    msg_loop()
    root.mainloop()
```

## 实现步骤

### Step 1: 创建目录结构和基础文件

```
window-toggle-win/
├── main.py
├── gui/
│   ├── __init__.py
│   ├── main_window.py
│   └── add_dialog.py
├── core/
│   ├── __init__.py
│   ├── hotkey.py
│   ├── window.py
│   └── config.py
└── requirements.txt
```

### Step 2: 实现 core/config.py

- 配置文件路径：`%APPDATA%\window-toggle-win\config.json`
- 实现 load/save/add/remove 方法

### Step 3: 实现 core/window.py

- 实现 get_all_windows() 枚举窗口
- 实现 toggle_window() 切换窗口
- 测试窗口枚举和 toggle

### Step 4: 实现 core/hotkey.py

- 实现 register/unregister 热键
- 定义修饰键和虚拟键常量

### Step 5: 实现 gui/main_window.py

- 创建主窗口
- 显示快捷键列表
- 添加/删除按钮事件绑定

### Step 6: 实现 gui/add_dialog.py

- 第一步：捕获按键
- 第二步：枚举并显示窗口
- 第三步：保存配置并注册热键

### Step 7: 整合消息循环

- 在 main.py 中整合 tkinter 和 win32 消息循环

### Step 8: 添加托盘支持

- 用 pystray 实现托盘图标
- 关闭窗口时最小化到托盘

## 关键数据结构

### 窗口信息
```python
{
    "hwnd": 12345678,      # 窗口句柄
    "title": "Terminator", # 窗口标题
    "class": "Xterminal"  # 窗口类名
}
```

### 快捷键配置
```python
{
    "id": 1,                # 唯一ID
    "key": "F1",            # 键名
    "modifiers": "Ctrl+Alt",# 修饰键
    "window_title": "Terminator",
    "window_class": "Xterminal-emulator"
}
```

### 虚拟键码映射
```python
VK_CODES = {
    0x70: "F1", 0x71: "F2", 0x72: "F3", ...,
    0x41: "A", 0x42: "B", ...,
    0x30: "0", 0x31: "1", ...
}

MOD_CODES = {
    "Ctrl": 0x0002,
    "Alt": 0x0001,
    "Shift": 0x0004,
    "Win": 0x0008
}
```

## 依赖

```
pywin32
pystray
Pillow  # pystray 需要
```

## 测试要点

1. 窗口枚举是否返回所有可见窗口
2. toggle 窗口是否正常工作
3. 热键注册是否成功
4. 配置文件读写是否正常
5. GUI 交互是否流畅
