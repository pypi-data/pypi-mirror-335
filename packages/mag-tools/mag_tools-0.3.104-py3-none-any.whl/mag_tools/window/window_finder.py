import ctypes
from ctypes import wintypes

# 定义回调函数类型
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

# 定义 Windows API 函数
EnumWindows = ctypes.windll.user32.EnumWindows
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
GetWindowText = ctypes.windll.user32.GetWindowTextW
SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow

class WindowFinder:
    @staticmethod
    def find_window_by_title(title: str):
        hwnd_list = []

        def enum_windows_proc(hwnd: wintypes.HWND):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                window_title = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, window_title, length + 1)
                if title in window_title.value:
                    hwnd_list.append(hwnd)
            return True

        EnumWindows(EnumWindowsProc(enum_windows_proc), 0)
        return hwnd_list