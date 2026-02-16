# window-toggle-win 实现计划

## 项目目标

将 Linux 下的 window-toggle 工具移植到 Windows，实现相同的功能体验。

## 功能需求

### 1. Configure 模式（交互式配置）

- **捕获任意按键组合**：监听全局键盘事件
- **扫描并显示窗口**：枚举所有顶层窗口，按进程/应用分组显示
- **用户选择**：显示窗口列表，用户输入编号选择
- **保存配置**：将 热键 → 窗口 映射保存到配置文件
- **注册系统快捷键**：将热键注册到 Windows 系统

### 2. Run 模式

- 根据按键查找对应窗口
- 检测窗口状态（隐藏/显示）
- Toggle：隐藏→显示，显示→隐藏

### 3. Show 模式

- 显示当前所有已配置的快捷键

### 4. Clean 模式

- 清除所有已配置的快捷键
- 删除配置文件

## 技术方案

### 技术栈选择

**AutoHotkey v2** - 最简单方案，原生支持：
- 全局热键注册 (`Hotkey` 命令)
- 窗口枚举和操作
- GUI 交互界面
- 配置文件读写

### 核心 API

| 功能 | Windows API |
|------|-------------|
| 枚举窗口 | `EnumWindows()` + `GetWindowText()` |
| 隐藏窗口 | `ShowWindow(hwnd, SW_MINIMIZE)` |
| 显示窗口 | `SetForegroundWindow(hwnd)` + `ShowWindow(hwnd, SW_RESTORE)` |
| 注册热键 | `Hotkey` 命令或 `RegisterHotKey()` |
| 获取窗口类 | `GetClassName()` |

### 配置文件格式

JSON 格式，存储在用户目录：

```json
{
  "shortcuts": [
    {
      "key": "F1",
      "modifiers": "Ctrl+Alt",
      "window_title": "Terminator",
      "window_class": "Xterminal-emulator"
    }
  ]
}
```

### 状态跟踪

使用临时文件记录窗口状态：
- `~/.config/window-toggle/state` - 隐藏/显示状态

## 文件结构

```
window-toggle-win/
├── window-toggle.ahk      # 主程序
├── config.json            # 配置文件（运行时生成）
└── README.md              # 使用说明
```

## 实现步骤

### Phase 1: 基础框架

1. 创建主程序框架
2. 实现命令行参数解析（--configure, --run, --show, --clean）
3. 实现配置文件读写

### Phase 2: Configure 模式

1. 实现全局按键捕获
2. 实现窗口枚举
3. 实现窗口分组和显示
4. 实现用户选择交互
5. 实现系统热键注册

### Phase 3: Run 模式

1. 实现按键到窗口的映射查找
2. 实现窗口状态检测
3. 实现 toggle 逻辑

### Phase 4: 完善

1. 实现 --show 命令
2. 实现 --clean 命令
3. 错误处理和用户提示

## 使用方式

```bash
# 配置新快捷键
window-toggle.ahk --configure

# 运行（由热键触发）
window-toggle.ahk --run --key F1

# 显示配置
window-toggle.ahk --show

# 清除配置
window-toggle.ahk --clean
```
