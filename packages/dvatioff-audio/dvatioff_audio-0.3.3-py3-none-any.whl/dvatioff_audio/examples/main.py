from dvatioff_audio.utils import minimize_console


def main():
    print("工具初始化中...", flush=True)

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from qt_material import apply_stylesheet
    from dvatioff_audio.examples.main_window_framework import MainWindow

    app = QApplication()
    QTimer.singleShot(100, minimize_console)
    window = MainWindow()
    apply_stylesheet(app, theme='theme_xxx.xml', invert_secondary=True)
    window.show()

    app.exec()


if __name__ == '__main__':
    main()
