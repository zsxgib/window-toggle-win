"""
热键管理模块
使用 pynput 库实现全局热键
"""
from pynput import keyboard
import time


# 存储已注册的热键回调
_hotkey_callbacks = {}
# 防止快速连续触发的标志
_last_trigger_time = {}
_TRIGGER_COOLDOWN = 0.5  # 0.5秒内不重复触发
_listener = None


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

        # 使用 pynput 监听
        def make_callback(sid):
            def callback():
                _trigger_callback(sid)
            return callback

        # pynput 需要特殊处理
        # 这里我们记录热键信息，在监听器中处理
        _hotkey_callbacks[shortcut_id] = {
            'modifiers': modifiers_str,
            'key': key_str,
            'callback': make_callback(shortcut_id)
        }

        # 确保监听器正在运行
        global _listener
        if _listener is None:
            _listener = keyboard.Listener(on_press=_on_press)
            _listener.start()

        print(f"Registered hotkey: {hotkey_str}, id={shortcut_id}")
        return True
    except Exception as e:
        print(f"Failed to register hotkey: {e}")
        return False


def _on_press(key):
    """全局按键监听回调"""
    try:
        key_name = key.char
    except AttributeError:
        key_name = str(key).replace('Key.', '')

    # 获取当前按下的修饰键
    current_modifiers = []
    pressed = keyboard._current_keys
    if keyboard.Key.ctrl in pressed:
        current_modifiers.append('Ctrl')
    if keyboard.Key.alt in pressed:
        current_modifiers.append('Alt')
    if keyboard.Key.shift in pressed:
        current_modifiers.append('Shift')
    if keyboard.Key.cmd in pressed:
        current_modifiers.append('Win')

    current_modifiers.sort()
    current_mod_str = '+'.join(current_modifiers)

    # 检查是否匹配已注册的热键
    for shortcut_id, info in _hotkey_callbacks.items():
        expected_mod = info['modifiers'].split('+') if info['modifiers'] else []
        expected_mod.sort()
        expected_mod_str = '+'.join(expected_mod)

        if current_mod_str == expected_mod_str and key_name == info['key']:
            # 触发回调
            info['callback']()
            break


def unregister(hwnd, shortcut_id):
    """
    注销全局热键
    """
    if shortcut_id in _hotkey_callbacks:
        del _hotkey_callbacks[shortcut_id]


def set_callback(shortcut_id, callback):
    """
    设置热键触发时的回调（用于 toggle 窗口）
    """
    if shortcut_id in _hotkey_callbacks:
        _hotkey_callbacks[shortcut_id]['toggle_callback'] = callback


def _trigger_callback(shortcut_id):
    """
    热键触发时的内部回调
    """
    current_time = time.time()

    # 检查是否在冷却时间内
    if shortcut_id in _last_trigger_time:
        if current_time - _last_trigger_time[shortcut_id] < _TRIGGER_COOLDOWN:
            print(f"Hotkey ignored (cooldown): {shortcut_id}")
            return

    _last_trigger_time[shortcut_id] = current_time

    print(f">>> Hotkey triggered: {shortcut_id}")
    if shortcut_id in _hotkey_callbacks:
        cb = _hotkey_callbacks[shortcut_id].get('toggle_callback')
        if cb:
            cb()


def unregister_all():
    """注销所有热键"""
    global _listener
    if _listener:
        _listener.stop()
        _listener = None
    _hotkey_callbacks.clear()
    _last_trigger_time.clear()
