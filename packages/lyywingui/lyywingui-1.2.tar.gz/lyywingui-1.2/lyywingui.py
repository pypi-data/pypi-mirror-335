import psutil
import win32gui
import win32process
from fuzzywuzzy import fuzz

def get_window_title_by_process_name(process_name, title_filter=None, threshold=80):
    """
    通过进程名获取所有关联窗口的标题，并可选地模糊匹配标题。

    :param process_name: 进程名（例如：notepad.exe）
    :param title_filter: 用于模糊匹配的标题字符串（可选）
    :param threshold: 模糊匹配的阈值（默认 80）
    :return: 窗口标题列表
    """
    # 获取所有匹配进程的 PID
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == process_name.lower():
            pids.append(proc.info['pid'])

    # 如果未找到进程，返回空列表
    if not pids:
        return []

    # 枚举所有窗口，查找与目标 PID 匹配的窗口
    window_titles = []

    def callback(hwnd, _):
        # 获取窗口的进程 ID
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid in pids:
            # 获取窗口标题
            title = win32gui.GetWindowText(hwnd)
            if title:  # 过滤掉无标题的窗口
                # 如果未提供 title_filter 或模糊匹配成功，则添加到结果列表
                if title_filter is None or fuzz.partial_ratio(title.lower(), title_filter.lower()) >= threshold:
                    window_titles.append(title)
        return True

    # 枚举所有窗口
    win32gui.EnumWindows(callback, None)
    if len(window_titles) > 0:
        window_title = window_titles[0]
    return window_title



def get_hwnd_by_title(title):
    """
    根据窗口标题查找所有匹配的窗口句柄。

    :param title: 窗口标题（可以是部分标题）
    :return: 匹配的窗口句柄列表
    """
    def callback(hwnd, hwnds):
        if title.lower() in win32gui.GetWindowText(hwnd).lower():
            hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

if __name__ == '__main__':
    # 示例：获取进程名为 'TdxW.exe' 的窗口标题，并模糊匹配 "通达信金融终端"
    process_name = 'TdxW.exe'
    title_filter = "通达信金融终端"
    titles = get_window_title_by_process_name(process_name, title_filter)
    print(titles)