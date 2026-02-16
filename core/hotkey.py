"""
热键管理模块
使用 keyboard 库实现全局热键
"""
import keyboard


# 存储已注册的热键回调
_hotkey_callbacks = {}
# 防止快速连续触发的标志
_last_trigger_time = {}
_TRIGGER_COOLDOWN = 0.5  # 0.5秒内不重复触发


def register(hwnd, shortcut_id, modifiers_str, key_str):
    """
    注册全局热键
    Args:
        hwnd: 窗口句柄（忽略，仅为兼容）
        shortcut_id: 热键 ID
        modifiers_str: 修饰键字符串，如 "Ctrl+Alt"
        key_str: 键名字符串，如 "F1"
    Returns:
        bool: 是否注册成功
    """
    try:
        # 构建热键字符串
        hotkey_str = f"{modifiers_str}+{key_str}" if modifiers_str else key_str

        print(f"Registering hotkey: {hotkey_str}")

        # 注册热键，使用 suppress=True 防止重复触发
        keyboard.add_hotkey(hotkey_str, _trigger_callback, args=(shortcut_id,), suppress=True)

        print(f"Registered hotkey: {hotkey_str}, id={shortcut_id}")
        return True
    except Exception as e:
        print(f"Failed to register hotkey: {e}")
        return False


def unregister(hwnd, shortcut_id):
    """
    注销全局热键
    注意：keyboard 库无法直接注销特定热键，需要记录所有热键
    """
    pass


def set_callback(shortcut_id, callback):
    """
    设置热键触发时的回调
    Args:
        shortcut_id: 热键 ID
        callback: 回调函数
    """
    _hotkey_callbacks[shortcut_id] = callback


def _trigger_callback(shortcut_id):
    """
    热键触发时的内部回调
    """
    import time

    current_time = time.time()

    # 检查是否在冷却时间内
    if shortcut_id in _last_trigger_time:
        if current_time - _last_trigger_time[shortcut_id] < _TRIGGER_COOLDOWN:
            print(f"Hotkey ignored (cooldown): {shortcut_id}")
            return

    _last_trigger_time[shortcut_id] = current_time

    print(f">>> Hotkey triggered: {shortcut_id}")
    if shortcut_id in _hotkey_callbacks:
        _hotkey_callbacks[shortcut_id]()


def unregister_all():
    """注销所有热键"""
    keyboard.unhook_all()
    _hotkey_callbacks.clear()
    _last_trigger_time.clear()
