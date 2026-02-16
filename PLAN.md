# window-toggle-win 实现计划

## 项目目标

将 Linux 下的 window-toggle 工具移植到 Windows，使用 Python + customtkinter 实现 GUI，pywin32 处理窗口和热键。

## 功能需求

### 1. GUI 主界面

- 显示当前已配置的快捷键列表
- "添加" 按钮 → 弹出窗口选择对话框
- "删除" 按钮 → 删除选中的快捷键
- 托盘图标支持（后台运行）

### 2. 添加快捷键流程

- 点击 "添加" 按钮
- 弹出对话框：提示用户按下快捷键
- 扫描并显示当前所有窗口（按应用分组）
- 用户选择目标窗口
- 保存配置，自动注册热键

### 3. Toggle 功能

- 热键触发时检测窗口状态
- 隐藏 → 显示（激活窗口）
- 显示 → 隐藏（最小化窗口）

### 4. 删除快捷键

- 选中列表中的快捷键
- 点击删除，移除配置和热键

## 技术方案

### 技术栈

- **Python 3**
- **pywin32** - Windows API 封装（窗口操作、热键注册）
- **customtkinter** - 现代 GUI 样式

### 核心 API

| 功能 | pywin32 |
|------|---------|
| 枚举窗口 | `win32gui.EnumWindows()` |
| 获取窗口标题 | `win32gui.GetWindowText()` |
| 获取窗口类 | `win32gui.GetClassName()` |
| 隐藏窗口 | `win32gui.ShowWindow(hwnd, SW_MINIMIZE)` |
| 显示窗口 | `win32gui.SetForegroundWindow()` + `ShowWindow(hwnd, SW_RESTORE)` |
| 注册全局热键 | `win32gui.RegisterHotKey()` |
| 消息循环 | `win32gui.PumpMessages()` |

### 配置文件格式

JSON 格式，存储在用户配置目录：

```json
{
  "shortcuts": [
    {
      "id": 1,
      "key": "F1",
      "modifiers": "Ctrl+Alt",
      "window_title": "Terminator",
      "window_class": "Xterminal-emulator"
    }
  ]
}
```

### 配置文件路径

- Windows: `%APPDATA%\window-toggle-win\config.json`

## 文件结构

```
window-toggle-win/
├── window-toggle.py      # 主程序
├── config.json           # 配置文件（运行时生成）
├── requirements.txt      # 依赖
└── README.md            # 使用说明
```

## 依赖安装

```bash
pip install pywin32 customtkinter
```

## 实现步骤

### Phase 1: 基础框架

1. 创建主窗口 GUI（customtkinter）
2. 实现配置文件读写
3. 实现窗口枚举函数

### Phase 2: 添加快捷键功能

1. 实现快捷键捕获对话框
2. 实现窗口列表显示（按应用分组）
3. 实现用户选择交互
4. 实现热键注册（RegisterHotKey）

### Phase 3: Toggle 功能

1. 实现热键回调处理
2. 实现窗口状态检测（IsIconic）
3. 实现 toggle 逻辑

### Phase 4: GUI 完善

1. 实现删除快捷键功能
2. 实现托盘图标
3. 界面美化

## 使用方式

```bash
# 运行程序
python window-toggle.py

# 程序启动后显示 GUI
# - 点击"添加"配置新快捷键
# - 按下配置的快捷键可 toggle 窗口
# - 关闭窗口最小化到托盘
```

## GUI 界面设计

```
┌─────────────────────────────────────────┐
│  Window Toggle                    _ X  │
├─────────────────────────────────────────┤
│  已配置的快捷键:                        │
│  ┌─────────────────────────────────┐   │
│  │ Ctrl+Alt+F1 → Terminator       │   │
│  │ Ctrl+Alt+F2 → VS Code          │   │
│  │ Super+F3 → Chrome             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [+ 添加]  [- 删除]                     │
│                                         │
│  按下快捷键可 toggle 对应窗口           │
└─────────────────────────────────────────┘
```
