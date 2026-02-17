"""
热键管理模块
使用 pynput 库实现全局热键
"""
from pynput import keyboard
import time


# 存储已注册的热键回调
_hotkey_callbacks = {}
_callbacks = {}
# 防止快速连续触发的标志
_last_trigger_time = {}
_TRIGGER_COOLDOWN = 0  # 移除 cooldown，依赖窗口状态判断来防止闪烁
_listener = None
# 记录当前按下的修饰键
_pressed_modifiers = set()


def register(hwnd, shortcut_id, modifiers_str, key_str):
    """
    注册全局热键
    """
    try:
        hotkey_str = f"{modifiers_str}+{key_str}" if modifiers_str else key_str
        print(f"Registering hotkey: {hotkey_str}")

        _hotkey_callbacks[shortcut_id] = {
            'modifiers': modifiers_str,
            'key': key_str
        }

        global _listener
        if _listener is None:
            _listener = keyboard.Listener(on_press=_on_press, on_release=_on_release)
            _listener.start()

        print(f"Registered hotkey: {hotkey_str}, id={shortcut_id}")
        return True
    except Exception as e:
        print(f"Failed to register hotkey: {e}")
        return False


def _on_press(key):
    """全局按键按下回调"""
    global _pressed_modifiers

    try:
        key_name = key.char
    except AttributeError:
        key_name = str(key).replace('Key.', '')

    # 记录修饰键
    if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        _pressed_modifiers.add('Ctrl')
    elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
        _pressed_modifiers.add('Alt')
    elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
        _pressed_modifiers.add('Shift')
    elif key == keyboard.Key.cmd or key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
        _pressed_modifiers.add('Win')

    # 检查是否匹配已注册的热键
    current_mod = '+'.join(sorted(_pressed_modifiers))

    for shortcut_id, info in _hotkey_callbacks.items():
        expected_mod = info['modifiers']
        if expected_mod:
            expected_mod_sorted = '+'.join(sorted(expected_mod.split('+')))
        else:
            expected_mod_sorted = ''

        if current_mod == expected_mod_sorted and key_name == info['key']:
            _trigger_callback(shortcut_id)
            break


def _on_release(key):
    """全局按键释放回调"""
    global _pressed_modifiers

    try:
        key_name = key.char
    except AttributeError:
        key_name = str(key).replace('Key.', '')

    # 移除修饰键
    if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        _pressed_modifiers.discard('Ctrl')
    elif key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
        _pressed_modifiers.discard('Alt')
    elif key == keyboard.Key.shift or key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
        _pressed_modifiers.discard('Shift')
    elif key == keyboard.Key.cmd or key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
        _pressed_modifiers.discard('Win')


def _trigger_callback(shortcut_id):
    """热键触发时的内部回调"""
    current_time = time.time()

    if shortcut_id in _last_trigger_time:
        if current_time - _last_trigger_time[shortcut_id] < _TRIGGER_COOLDOWN:
            print(f"Hotkey ignored (cooldown): {shortcut_id}")
            return

    _last_trigger_time[shortcut_id] = current_time
    print(f">>> Hotkey triggered: {shortcut_id}")

    # 调用注册的回调
    if shortcut_id in _callbacks:
        _callbacks[shortcut_id]()


def unregister(hwnd, shortcut_id):
    """注销热键"""
    if shortcut_id in _hotkey_callbacks:
        del _hotkey_callbacks[shortcut_id]


def set_callback(shortcut_id, callback):
    """设置热键触发时的回调"""
    _callbacks[shortcut_id] = callback


def unregister_all():
    """注销所有热键"""
    global _listener, _pressed_modifiers
    if _listener:
        _listener.stop()
        _listener = None
    _hotkey_callbacks.clear()
    _callbacks.clear()
    _last_trigger_time.clear()
    _pressed_modifiers.clear()
