from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget
import dvatioff_audio.gui.gui_css as css
from dvatioff_audio.globals import PATH_ICON_WARNING
from dvatioff_audio.gui.gui_utils import create_label, create_button, add_widgets_to_vhboxlayout, create_layout


class NotificationWindow(QWidget):
    signal_confirmed = Signal()

    def __init__(self, title, message, icon_path=PATH_ICON_WARNING):
        super().__init__()
        self.title = title
        self.message = message
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowModality(Qt.ApplicationModal)
        self.init_UI()
        self.show()

    def init_UI(self):
        self.setWindowTitle(self.title)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(400, 200)

        layout = create_layout('vbox', self)

        label_message = create_label(self.message, css.LABEL_STYLE_NORMAL, alignment=Qt.AlignCenter)
        button_ok = create_button('确认', css.BUTTON_STYLE_PINK)
        button_ok.clicked.connect(self.confirm)

        add_widgets_to_vhboxlayout(layout, [
            [label_message],
            [button_ok]
        ])

    def confirm(self):
        self.signal_confirmed.emit()
        self.close()

    def change_icon(self, icon_path):
        self.setWindowIcon(QIcon(icon_path))
