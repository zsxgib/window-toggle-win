"""
热键管理模块
负责全局热键的注册、注销
"""
import win32gui
import win32con

# WM_HOTKEY 消息 ID
WM_HOTKEY = 0x0312

# 修饰键码
MOD_CODES = {
    'Alt': win32con.MOD_ALT,
    'Ctrl': win32con.MOD_CONTROL,
    'Shift': win32con.MOD_SHIFT,
    'Win': win32con.MOD_WIN,
}

# 虚拟键码映射
VK_CODES = {
    # 功能键
    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
    'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
    'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B,
    # 字母键
    'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44, 'E': 0x45,
    'F': 0x46, 'G': 0x47, 'H': 0x48, 'I': 0x49, 'J': 0x4A,
    'K': 0x4B, 'L': 0x4C, 'M': 0x4D, 'N': 0x4E, 'O': 0x4F,
    'P': 0x50, 'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54,
    'U': 0x55, 'V': 0x56, 'W': 0x57, 'X': 0x58, 'Y': 0x59, 'Z': 0x5A,
    # 数字键
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    # 符号键
    'Space': 0x20,
    'Tab': 0x09,
    'Enter': 0x0D,
    'Escape': 0x1B,
    'Backspace': 0x08,
    # 方向键
    'Left': 0x25, 'Up': 0x26, 'Right': 0x27, 'Down': 0x28,
}

# 反向映射：虚拟键码转键名
VK_TO_NAME = {v: k for k, v in VK_CODES.items()}


def parse_modifiers(modifiers_str):
    """
    解析修饰键字符串
    Args:
        modifiers_str: 如 "Ctrl+Alt" 或 "Ctrl+Alt+Shift"
    Returns:
        int: 修饰键码组合
    """
    if not modifiers_str:
        return 0

    mod = 0
    parts = modifiers_str.split('+')
    for part in parts:
        part = part.strip()
        if part in MOD_CODES:
            mod |= MOD_CODES[part]
    return mod


def parse_key(key_str):
    """
    解析键名字符串
    Args:
        key_str: 如 "F1", "A", "Space"
    Returns:
        int: 虚拟键码
    """
    return VK_CODES.get(key_str, 0)


def get_key_name(vk):
    """
    根据虚拟键码获取键名
    Args:
        vk: 虚拟键码
    Returns:
        str: 键名
    """
    return VK_TO_NAME.get(vk, '')


def get_modifiers_name(mod):
    """
    根据修饰键码获取修饰键名
    Args:
        mod: 修饰键码
    Returns:
        str: 修饰键名字符串
    """
    parts = []
    if mod & win32con.MOD_ALT:
        parts.append('Alt')
    if mod & win32con.MOD_CONTROL:
        parts.append('Ctrl')
    if mod & win32con.MOD_SHIFT:
        parts.append('Shift')
    if mod & win32con.MOD_WIN:
        parts.append('Win')
    return '+'.join(parts)


def format_hotkey(modifiers, key):
    """
    格式化热键字符串
    Args:
        modifiers: 修饰键码
        key: 虚拟键码
    Returns:
        str: 如 "Ctrl+Alt+F1"
    """
    mod_str = get_modifiers_name(modifiers)
    key_name = get_key_name(key)

    if mod_str and key_name:
        return f"{mod_str}+{key_name}"
    elif key_name:
        return key_name
    else:
        return ""


def register(hwnd, shortcut_id, modifiers_str, key_str):
    """
    注册全局热键
    Args:
        hwnd: 窗口句柄（接收热键消息）
        shortcut_id: 热键 ID
        modifiers_str: 修饰键字符串，如 "Ctrl+Alt"
        key_str: 键名字符串，如 "F1"
    Returns:
        bool: 是否注册成功
    """
    mod = parse_modifiers(modifiers_str)
    key = parse_key(key_str)

    if key == 0:
        print(f"Failed to register hotkey: key not found")
        return False

    if hwnd is None:
        print(f"Failed to register hotkey: hwnd is None")
        return False

    try:
        result = win32gui.RegisterHotKey(hwnd, shortcut_id, mod, key)
        if result:
            print(f"Registered hotkey: {modifiers_str}+{key_str}, id={shortcut_id}, hwnd={hwnd}")
        else:
            print(f"Failed to register hotkey: {modifiers_str}+{key_str} (already registered?)")
        return result
    except Exception as e:
        print(f"Failed to register hotkey: {e}")
        return False


def unregister(hwnd, shortcut_id):
    """
    注销全局热键
    Args:
        hwnd: 窗口句柄
        shortcut_id: 热键 ID
    """
    try:
        win32gui.UnregisterHotKey(hwnd, shortcut_id)
    except Exception:
        pass


def unregister_all(hwnd):
    """
    注销所有与指定窗口关联的热键
    注意：Win32 API 不支持一次性获取所有已注册的热键，
    所以通常在配置中记录所有 ID，然后逐个注销
    Args:
        hwnd: 窗口句柄
    """
    pass
