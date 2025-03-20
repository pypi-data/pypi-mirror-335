"""
此脚本中的类用于启动一个子线程，实时获取工具与 Wwise 工程 waapi 通信接口的连接状态，并通过 Signal 信号将连接状态的信息传递给主线程
"""


import time
import asyncio
import waapi
from PySide6.QtCore import Signal, QRunnable, QObject
import threading
from dvatioff_audio.waapi.waapi_utils import get_connected_project_name_info


# 用于发送连接状态的信号
class SignalConnectionStatus(QObject):
    signal = Signal(bool)


# 用于发送 waapi 客户端的信号
class SignalClient(QObject):
    signal = Signal(object)


# 用于发送 Wwise 工程名称的信号
class SignalProjectName(QObject):
    signal = Signal(str, str)


class WaapiConnectWorker(QRunnable):
    signal_connection_status = SignalConnectionStatus()
    signal_waapi_client = SignalClient()
    signal_project_name = SignalProjectName()

    def __init__(self):
        super().__init__()
        self.client = None
        self.running = threading.Event()
        self.running.set()
        self.connect_status = False
        self.connect_changed = False
        self.worker_thread = None

    def run(self):
        self.worker_thread = threading.Thread(target=self.run_in_thread)
        self.worker_thread.start()

    def run_in_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while self.running.is_set():
            self.connect_to_waapi()
            time.sleep(0.5)

        loop.close()

    def connect_to_waapi(self):
        """
        尝试连接到 waapi 并更新UI信号。如果已连接，直接返回
        """
        if self.client and self.client.is_connected():
            return

        self.reset_client()

        try:
            self.client = waapi.WaapiClient()
            if self.client and self.client.is_connected():
                self.handle_successful_connection()
            else:
                self.handle_failed_connection()
        except waapi.CannotConnectToWaapiException as e:
            print(f"无法连接到 waapi: {e}")
            self.handle_failed_connection()

    def reset_client(self):
        """
        重置客户端状态，清除任何现有的客户端引用
        """
        if self.client:
            self.client = None
        self.signal_waapi_client.signal.emit(self.client)
        self.signal_connection_status.signal.emit(False)

    def handle_successful_connection(self):
        """
        处理成功连接的情况，获取项目名称并发送相关信号
        """
        try:
            project_name, wwise_version = get_connected_project_name_info(self.client)
            self.signal_project_name.signal.emit(project_name, wwise_version)
            self.signal_connection_status.signal.emit(True)
            self.signal_waapi_client.signal.emit(self.client)
        except Exception as e:
            print(f"获取项目名称失败: {e}")
            self.reset_client()

    def handle_failed_connection(self):
        """
        处理连接失败的情况，重置客户端并发送失败信号
        """
        self.reset_client()

    def stop(self):
        self.running.clear()
        if self.client:
            self.client.disconnect()
            self.client = None
        if self.worker_thread:
            self.worker_thread.join()
            self.worker_thread = None
