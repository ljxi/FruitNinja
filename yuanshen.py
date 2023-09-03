import ctypes
u32 = ctypes.windll.user32
hwnd = u32.FindWindowW('UnityWndClass', '原神')
u32.ShowWindow(hwnd, 9)