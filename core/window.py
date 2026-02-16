"""
窗口管理模块
负责窗口枚举、toggle 功能
"""
import win32gui
import win32con
import win32process


def get_all_windows():
    """
    获取所有可见顶层窗口
    Returns:
        list: 窗口信息列表，每个元素为 (hwnd, title, class_name)
    """
    windows = []

    def enum_callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return True

        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True

        class_name = win32gui.GetClassName(hwnd)
        windows.append({
            'hwnd': hwnd,
            'title': title,
            'class_name': class_name
        })
        return True

    win32gui.EnumWindows(enum_callback, None)
    return windows


def get_window_info(hwnd):
    """
    获取窗口详细信息
    Args:
        hwnd: 窗口句柄
    Returns:
        dict: 窗口信息
    """
    if not win32gui.IsWindow(hwnd):
        return None

    return {
        'hwnd': hwnd,
        'title': win32gui.GetWindowText(hwnd),
        'class_name': win32gui.GetClassName(hwnd)
    }


def group_by_class(windows):
    """
    按窗口类名分组
    Args:
        windows: 窗口信息列表
    Returns:
        dict: {class_name: [window_info, ...]}
    """
    groups = {}
    for w in windows:
        class_name = w['class_name']
        if class_name not in groups:
            groups[class_name] = []
        groups[class_name].append(w)
    return groups


def is_window_minimized(hwnd):
    """
    检查窗口是否最小化
    Args:
        hwnd: 窗口句柄
    Returns:
        bool: 是否最小化
    """
    return win32gui.IsIconic(hwnd)


def is_window_visible(hwnd):
    """
    检查窗口是否可见（未最小化且未隐藏）
    Args:
        hwnd: 窗口句柄
    Returns:
        bool: 是否可见
    """
    return win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd)


def toggle_window(hwnd):
    """
    切换窗口显示/隐藏
    如果窗口最小化，则恢复并激活
    如果窗口正常显示，则最小化
    Args:
        hwnd: 窗口句柄
    Returns:
        bool: 操作是否成功
    """
    if not win32gui.IsWindow(hwnd):
        return False

    if is_window_minimized(hwnd):
        # 最小化 → 恢复并激活
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    else:
        # 正常/最大化 → 最小化
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

    return True


def find_window_by_class(window_class):
    """
    通过窗口类名查找窗口（返回第一个匹配的窗口）
    Args:
        window_class: 窗口类名
    Returns:
        int or None: 窗口句柄
    """
    windows = get_all_windows()
    for w in windows:
        if w['class_name'] == window_class:
            return w['hwnd']
    return None


def find_window_by_title(title):
    """
    通过窗口标题查找窗口（模糊匹配）
    Args:
        title: 窗口标题
    Returns:
        int or None: 窗口句柄
    """
    windows = get_all_windows()
    for w in windows:
        if title.lower() in w['title'].lower():
            return w['hwnd']
    return None


def activate_window(hwnd):
    """
    激活窗口（恢复到前台）
    Args:
        hwnd: 窗口句柄
    """
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
