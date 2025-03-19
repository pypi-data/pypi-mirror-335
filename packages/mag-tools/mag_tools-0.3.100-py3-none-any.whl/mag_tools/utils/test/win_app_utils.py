import os

import psutil
import threading

class WinAppUtils:
    @staticmethod
    def check_port_used(port):
        # 注意：psutil.net_connections() 返回的是所有当前的网络连接信息
        # 我们需要遍历这些信息来找到指定端口的连接
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port:
                return True  # 端口已被占用
        return False  # 端口未被占用

    @staticmethod
    def run_bat_file_in_thread(bat_file_path):
        # 在新线程中执行 .bat 文件
        os.system(bat_file_path)

    @staticmethod
    def start_win_app_driver(root_dir: str, port: str):
        if WinAppUtils.check_port_used(port):
            print(f"WinAppDriver程序 {port} 已启动")
        else:
            print(f"WinAppDriver程序 {port} 未启动，启动WinAppDriver")
            app_win_driver_bat = os.path.join(os.path.join(root_dir, 'bin'), "WinAppDriver.bat")
            thread = threading.Thread(target=WinAppUtils.run_bat_file_in_thread, args=(app_win_driver_bat,))
            thread.start()
