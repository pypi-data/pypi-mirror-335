"""
文本-语音对齐检测窗口框架
"""


import os
import queue
import threading
import time
from PySide6.QtCore import  QRunnable, QObject, Signal, QThreadPool
from PySide6.QtGui import QTextCursor, QIcon
from PySide6.QtWidgets import QWidget
import dvatioff_audio.gui.gui_css as css
from notification_window_framework import NotificationWindow
from dvatioff_audio.voice.voice_utils import text_speech_verify_worker, output_text_speech_verify_result
from dvatioff_audio.gui.gui_utils import create_label, create_button, add_widgets_to_vhboxlayout, create_layout, create_textEdit
from dvatioff_audio.globals import PATH_ICON_VFY


class TextSpeechVerificationWorkerSignals(QObject):
    finished = Signal(dict)


class TextSpeechVerificationWorker(QRunnable):
    def __init__(self, folder_path, text_dict, language):
        super().__init__()
        self.folder_path = folder_path
        self.text_dict = text_dict
        self.language = language
        self.signals = TextSpeechVerificationWorkerSignals()
        self.stop_requested = False

    def run(self):
        update_queue = queue.Queue()
        worker_thread = threading.Thread(target=text_speech_verify_worker,
                                         args=(self.folder_path, self.text_dict, self.language, update_queue))
        worker_thread.start()
        vfy_complete = False

        while True:
            if self.stop_requested:
                break
            try:
                stt_result = update_queue.get_nowait()
                self.signals.finished.emit(stt_result)

                total_index = stt_result.get('total_index', 0)
                total_file_num = stt_result.get('total_file_num', 0)
                if total_index == total_file_num:
                    vfy_complete = True
            except queue.Empty:
                pass
            if vfy_complete:
                break
            time.sleep(0.4)

    def stop(self):
        self.stop_requested = True


class TextSpeechVFYWindow(QWidget):
    def __init__(self, text_dict, folder_path, language, icon_path=PATH_ICON_VFY):
        super().__init__()

        self.threadpool = QThreadPool()
        self.worker = None
        self.notification_window = None
        self.setWindowIcon(QIcon(icon_path))

        self.folder_path = folder_path
        self.text_dict = text_dict
        self.language = language

        self.error_log = ''
        self.error_file_paths = []

        self.layout = create_layout('vbox', self)

        self.label_all_log = create_label('全部日志', style=css.LABEL_STYLE_SIZE15)
        self.label_error_log = create_label('错误日志', style=css.LABEL_STYLE_SIZE15)
        self.label_cur_folder = create_label('<b>当前文件夹:</b> ')
        self.label_cur_detection_progress = create_label('<b>当前文件夹检测进度:</b> ')
        self.label_total_detection_progress = create_label('<b>总检测进度:</b> ')
        self.text_all_log = create_textEdit(read_only=True, max_height=600)
        self.text_error_log = create_textEdit(read_only=True, max_height=400)

        self.output_button = create_button('输出错误文件和日志', style=css.BUTTON_STYLE_PINK, enabled=False)
        self.output_button.clicked.connect(self.output_log_and_files)

        add_widgets_to_vhboxlayout(self.layout, [
            [self.label_all_log],
            [self.label_cur_folder],
            [self.label_cur_detection_progress],
            [self.label_total_detection_progress],
            [self.text_all_log],
            [self.label_error_log],
            [self.text_error_log],
            [self.output_button]
        ])

        self.setWindowTitle("文本-语音对齐检测")
        self.setFixedSize(1400, 1200)
        self.show()

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        event.accept()

    def execute_text_speech_vfy_task(self):
        self.worker = TextSpeechVerificationWorker(self.folder_path, self.text_dict, self.language)
        self.worker.signals.finished.connect(self.text_speech_vfy_ui_update)
        self.threadpool.start(self.worker)

    def text_speech_vfy_ui_update(self, stt_result):
        parent_directory_name = stt_result.get('parent_directory_name', '')
        file_name = stt_result.get('file_name', '')
        file_path = stt_result.get('file_path', '')
        cur_index = stt_result.get('cur_index', 0)
        cur_folder_file_num = stt_result.get('cur_folder_file_num', 0)
        total_index = stt_result.get('total_index', 0)
        total_file_num = stt_result.get('total_file_num', 0)
        true_text = stt_result.get('true_text', '')
        speech_text = stt_result.get('speech_text', '')
        true_pinyin = stt_result.get('true_pinyin', '')
        speech_pinyin = stt_result.get('speech_pinyin', '')
        true_kata = stt_result.get('true_kata', '')
        speech_kata = stt_result.get('speech_kata', '')
        true_kata_romaji = stt_result.get('true_kata_romaji', '')
        speech_kata_romaji = stt_result.get('speech_kata_romaji', '')
        wer = stt_result.get('wer', 0)

        self.label_cur_folder.setText(f'<b>当前文件夹:</b> {parent_directory_name}')
        self.label_cur_detection_progress.setText(f'<b>当前文件夹检测进度:</b> {cur_index}/{cur_folder_file_num}')
        self.label_total_detection_progress.setText(f'<b>总检测进度:</b> {total_index}/{total_file_num}')

        # 保持文本窗口的焦点跟随
        cursor_all_log = self.text_all_log.textCursor()
        cursor_all_log.movePosition(QTextCursor.End)
        self.text_all_log.setTextCursor(cursor_all_log)
        self.text_all_log.ensureCursorVisible()
        cursor_error_log = self.text_error_log.textCursor()
        cursor_error_log.movePosition(QTextCursor.End)
        self.text_error_log.setTextCursor(cursor_error_log)
        self.text_error_log.ensureCursorVisible()

        if true_text == "本句为呼喝声，跳过检测":
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>当前检测文件:</b> {file_name}</font><br>")
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['blue']}>{true_text}，跳过检测</font><br><br>")
            return
        elif true_text == "Azure 接口调用失败":
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>当前检测文件:</b> {file_name}<br>")
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['pink']}>{true_text}，跳过检测</font><br><br>")
            return

        self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>正确文本:</b> {true_text}</font><br>")
        self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>识别文本:</b> {speech_text}</font><br>")

        if self.language == "Chinese":
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>正确拼音:</b> {true_pinyin}</font><br>")
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>识别拼音:</b> {speech_pinyin}</font><br>")
        elif self.language == "Japanese":
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>正确假名:</b> {true_kata}</font><br>")
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>识别假名:</b> {speech_kata}</font><br>")
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>正确罗马音:</b> {true_kata_romaji}</font><br>")
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>识别罗马音:</b> {speech_kata_romaji}</font><br>")

        if wer < 0.2:
            self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['green']}><b>匹配度:</b> {(1 - wer) * 100:.2f}%</font><br><br>")
        else:
            self.error_file_paths.append(file_path)
            self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>错误文件:</b> {file_name}</font><br>")
            self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>正确文本:</b> {true_text}</font><br>")
            self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>识别文本:</b> {speech_text}</font><br>")
            if self.language == "Chinese":
                self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>正确拼音:</b> {true_pinyin}</font><br>")
                self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>识别拼音:</b> {speech_pinyin}</font><br>")
            elif self.language == "Japanese":
                self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>正确假名:</b> {true_kata}</font><br>")
                self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>识别假名:</b> {speech_kata}</font><br>")
                self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>正确罗马音:</b> {true_kata_romaji}</font><br>")
                self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['black']}><b>识别罗马音:</b> {speech_kata_romaji}</font><br>")
            if wer >= 0.5:
                self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['red']}><b>匹配度:</b> {(1 - wer) * 100:.2f}%</font><br><br>")
                self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['red']}><b>匹配度:</b> {(1 - wer) * 100:.2f}%</font><br><br>")

            elif 0.2 <= wer < 0.5:
                self.text_all_log.textCursor().insertHtml(f"<font color={css.COLOR['orange']}><b>匹配度:</b> {(1 - wer) * 100:.2f}</font><br><br>")
                self.text_error_log.textCursor().insertHtml(f"<font color={css.COLOR['orange']}><b>匹配度:</b> {(1 - wer) * 100:.2f}</font><br><br>")

        # 保持文本窗口的焦点跟随
        cursor_all_log = self.text_all_log.textCursor()
        cursor_all_log.movePosition(QTextCursor.End)
        self.text_all_log.setTextCursor(cursor_all_log)
        self.text_all_log.ensureCursorVisible()
        cursor_error_log = self.text_error_log.textCursor()
        cursor_error_log.movePosition(QTextCursor.End)
        self.text_error_log.setTextCursor(cursor_error_log)
        self.text_error_log.ensureCursorVisible()

        if total_index == total_file_num:
            self.error_log = self.text_error_log.toPlainText()
            if self.error_log:
                self.output_button.setEnabled(True)
            return

    def output_log_and_files(self):
        folder_name = os.path.basename(self.folder_path)
        output_text_speech_verify_result(folder_name, self.error_file_paths, self.error_log, self.language)
        self.output_button.setEnabled(False)
        self.notification_window = NotificationWindow('语音文本校验完毕', '输出成功, 错误文件和日志已保存至桌面')
        self.notification_window.show()
