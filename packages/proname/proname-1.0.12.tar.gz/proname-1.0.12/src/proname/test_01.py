import os
import sys
import ctypes

# 加载DLL
# HdConfigLib = ctypes.CDLL(r'C:\Users\Xpeng\source\repos\Dll1\x64\Debug\Dll1.dll')

def test_01():
    print("test_01")
    print(os.getcwd())
    print(sys.path)

def test_02():
    # 获取当前py文件路径
    current_path = os.path.dirname(os.path.abspath(__file__))
    print(current_path, "3")
    # 切换到当前路径
    dll_path = os.path.join(current_path, r'.\include\VnHardwareConf.dll')

    HdConfigLib = ctypes.CDLL(dll_path)
    HdConfigLib.getVersion.restype = ctypes.c_char_p
    result = HdConfigLib.getVersion()
    print(f"Result: {result.decode('utf-8')}")


if __name__ == '__main__':
    test_01()
    test_02()
