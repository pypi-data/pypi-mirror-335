"""
此脚本中的类用于启动一个子线程，实时获取当前 Wwise 工程选中的对象，并通过 Signal 信号将对象信息传递给主线程
"""


import time
from PySide6.QtCore import Signal, QRunnable, QObject
import threading
from dvatioff_audio.waapi.waapi_utils import get_selected_objects


class SignalSelectedObjects(QObject):
    signal = Signal(list)


class WwiseObjectSelectWorker(QRunnable):
    def __init__(self, client):
        super().__init__()

        self.client = client
        self.running = threading.Event()
        self.running.set()
        self.worker_thread = None

        self.signal_selected_objects = SignalSelectedObjects()

    def run(self):
        self.worker_thread = threading.Thread(target=self.run_in_thread)
        self.worker_thread.start()

    def run_in_thread(self):
        while self.running.is_set():
            if not self.client or not self.client.is_connected():
                self.stop()
                break
            self.get_selected_objects()
            time.sleep(0.5)

    def get_selected_objects(self):
        """
        获取当前 Wwise 工程选中的对象
        """
        if self.client and self.client.is_connected():
            result = get_selected_objects(self.client)
            if result:
                selected_objects = result['objects']
                self.signal_selected_objects.signal.emit(selected_objects)
            else:
                self.signal_selected_objects.signal.emit([])
        else:
            self.signal_selected_objects.signal.emit([])

    def stop(self):
        self.running.clear()
        if self.worker_thread:
            self.worker_thread.join()
            self.worker_thread = None
