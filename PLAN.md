# window-toggle-win 实现计划

## 项目目标

将 Linux 下的 window-toggle 工具移植到 Windows，实现用快捷键 toggle 窗口显示/隐藏的功能。

## 技术方案

### 技术栈

- **Python 3.8+**
- **pywin32** - Windows API（窗口操作、热键注册）
- **customtkinter** - 现代 GUI 样式（需要 `pip install customtkinter`）
- **pystray** - 系统托盘

### 文件结构

```
window-toggle-win/
├── main.py              # 入口
├── gui/
│   ├── __init__.py
│   ├── main_window.py  # 主窗口
│   └── add_dialog.py   # 添加对话框
├── core/
│   ├── __init__.py
│   ├── hotkey.py       # 热键管理
│   ├── window.py       # 窗口管理
│   └── config.py       # 配置管理
├── utils/
│   ├── __init__.py
│   └── logger.py       # 日志
├── requirements.txt
└── README.md
```

---

## 阶段划分

### 阶段 1：项目骨架

**目标：** 建立项目结构，配置依赖

**任务：**
1. 创建目录结构
2. 创建 requirements.txt：pywin32, customtkinter, pystray, Pillow
3. 创建空的 `__init__.py` 文件
4. 安装依赖并验证

**验收标准：** `pip install -r requirements.txt` 成功

---

### 阶段 2：配置管理 (core/config.py)

**目标：** 实现配置的持久化

**任务：**
1. 确定配置文件路径（`%APPDATA%\window-toggle-win\config.json`）
2. 如果目录不存在，自动创建
3. 实现配置加载：读取 JSON 文件，返回字典
4. 实现配置保存：写入 JSON 文件
5. 实现快捷键添加：根据现有数量生成新 ID
6. 实现快捷键删除：根据 ID 删除

**数据格式：**
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

**验收标准：** 配置能正确保存和读取，添加删除后文件内容正确

---

### 阶段 3：窗口管理 (core/window.py)

**目标：** 实现窗口枚举和 toggle 功能

**任务：**
1. 枚举所有可见顶层窗口（使用 EnumWindows API）
2. 获取每个窗口的标题和类名
3. 过滤掉不可见、无标题的窗口
4. 实现窗口分组：按 window_class 分组显示
5. 实现 toggle：最小化 → 恢复并激活，正常 → 最小化

**关键逻辑：**
- 如何判断窗口是否最小化：使用 IsIconic
- 如何找到目标窗口：通过 window_class 匹配（可能有多个，取第一个）
- 隐藏使用 SW_MINIMIZE，显示使用 SW_RESTORE + SetForegroundWindow

**验收标准：**
- 能列出当前所有窗口
- toggle 功能正常（最小化能恢复，恢复能最小化）

---

### 阶段 4：热键管理 (core/hotkey.py)

**目标：** 实现全局热键注册

**任务：**
1. 定义虚拟键码映射表（F1-F12, A-Z, 0-9 等）
2. 定义修饰键码（Ctrl, Alt, Shift, Win）
3. 实现热键注册函数：参数为 hwnd, id, modifiers, key
4. 实现热键注销函数
5. 处理 WM_HOTKEY 消息

**关键逻辑：**
- RegisterHotKey 需要一个窗口句柄来接收消息
- 修饰键需要组合（Ctrl+Alt = 0x0002 | 0x0001 = 0x0003）
- 热键 ID 不能重复

**验收标准：** 注册热键后，按下对应键能触发回调

---

### 阶段 5：主窗口 GUI (gui/main_window.py)

**目标：** 实现主界面

**任务：**
1. 创建主窗口，设置标题和尺寸
2. 创建快捷键列表区域（Listbox）
3. 创建"添加"和"删除"按钮
4. 窗口启动时加载配置，刷新列表
5. 点击"添加"打开添加对话框
6. 点击"删除"删除选中的快捷键
7. 窗口关闭时隐藏到托盘而不是退出

**验收标准：** 界面显示正常，按钮能点击，列表能显示

---

### 阶段 6：添加对话框 (gui/add_dialog.py)

**目标：** 实现添加快捷键的交互流程

**任务：**
1. 第一步：捕获按键
   - 显示提示"请按下快捷键"
   - 监听键盘事件（使用键盘钩子或 customtkinter bind）
   - 捕获到按键后显示组合（如 "Ctrl+Alt+F1"）
2. 第二步：显示窗口列表
   - 调用 core/window.py 枚举窗口
   - 按应用分组显示（类似 Linux 版的分组逻辑）
3. 第三步：保存
   - 用户选择窗口后，生成新 ID
   - 调用 core/config.py 保存配置
   - 调用 core/hotkey.py 注册热键

**验收标准：** 能完整走完添加流程，添加后列表更新

---

### 阶段 7：消息循环整合

**目标：** 让 GUI 和热键同时工作

**任务：**
1. 在 main.py 中创建 customtkinter root 窗口
2. 获取 root 窗口的句柄（用于 RegisterHotKey）
3. 启动时注册所有已配置的熱鍵
4. 实现消息循环：同时处理 customtkinter 事件和 Win32 消息
5. 热键触发时调用 window.toggle_window()

**关键问题：**
- customtkinter 基于 tkinter，其 mainloop 和 Win32 消息循环需要整合
- 解决方案：使用 root.after() 轮询或单独线程处理 Win32 消息

**验收标准：** 启动程序后，按下配置的熱鍵能 toggle 窗口

---

### 阶段 8：托盘支持

**目标：** 实现系统托盘图标

**任务：**
1. 使用 pystray 创建托盘图标
2. 点击托盘图标显示主窗口
3. 右键托盘图标显示菜单（显示/退出）
4. 关闭主窗口时隐藏到托盘而不是退出
5. 程序启动时最小化到托盘（可选）

**验收标准：** 关闭主窗口后程序仍在托盘运行，点击托盘能恢复窗口

---

## 模块依赖关系

```
main.py
  ├── gui/main_window.py
  │     └── gui/add_dialog.py
  │           ├── core/window.py
  │           └── core/config.py
  ├── core/config.py
  ├── core/hotkey.py
  └── core/window.py
```

---

## 验收检查点

| 阶段 | 检查点 |
|------|--------|
| 1 | 依赖安装成功 |
| 2 | 配置能保存和读取 |
| 3 | 窗口枚举正常，toggle 正常 |
| 4 | 热键注册成功并触发 |
| 5 | 主界面显示正常 |
| 6 | 添加流程完整 |
| 7 | 热键和 GUI 同时工作 |
| 8 | 托盘功能正常 |

---

## 潜在问题

1. **窗口类名匹配问题**：不同窗口实例可能有不同的类名后缀
   - 解决：使用模糊匹配或让用户选择具体窗口

2. **热键冲突**：系统或其他软件可能占用相同热键
   - 解决：RegisterHotKey 返回失败时提示用户

3. **管理员权限**：某些操作可能需要管理员权限
   - 解决：提示用户以管理员身份运行

4. **消息循环阻塞**：customtkinter(tkinter) 和 Win32 消息循环可能冲突
   - 解决：使用线程或轮询方式整合
