import os
import ctypes

_dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "opencv_world4100.dll")

if os.path.exists(_dll_path):
    ctypes.windll.kernel32.LoadLibraryW(_dll_path)
