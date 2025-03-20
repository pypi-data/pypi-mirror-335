from PySide6.QtCore import Qt, QUrl, QTimer, QObject, QEvent, QPoint
from PySide6.QtGui import QDesktopServices, QIntValidator
from PySide6.QtWidgets import QLabel, QFrame, QPushButton, QLineEdit, QComboBox, QTextEdit, QTextBrowser, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QFormLayout, QCheckBox
import dvatioff_audio.gui.gui_css as sss



def change_text_to_html(text, font="Microsoft YaHei", color="black", bold=False, italic=False, underline=False, line_break=False):
    """
    将文本转换为 HTML
    """
    text = f'<font face="{font}" color="{sss.COLOR[color]}">{text}</font>'
    if bold:
        text = f"<b>{text}</b>"
    if italic:
        text = f"<i>{text}</i>"
    if underline:
        text = f"<u>{text}</u>"
    if line_break:
        text += "<br>"

    return text


class CustomTooltip(QFrame):
    def __init__(self, text, parent=None):
        super().__init__(parent, Qt.ToolTip)
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(1)
        self.setStyleSheet("""
            QFrame {
                background-color: #9998a7;
                color: white;
                border-radius: 2px;
                padding: 1px;
            }
            QLabel {
                font-family: "Microsoft YaHei";
                font-size: 9pt;
            }
        """)
        self.label = QLabel(text)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.adjustSize()


class TooltipManager(QObject):
    def __init__(self, widget, tooltip_text, hover_delay=100):
        super().__init__(widget)
        self.widget = widget
        self.tooltip_text = tooltip_text
        self.hover_delay = hover_delay  # 毫秒

        self.tooltip = CustomTooltip(self.tooltip_text, parent=widget)
        self.tooltip.hide()

        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.show_tooltip)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_tooltip)

        self.widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.widget:
            if event.type() == QEvent.Enter:
                self.hover_timer.start(self.hover_delay)
            elif event.type() == QEvent.Leave:
                self.hover_timer.stop()
                self.hide_timer.stop()
                self.hide_tooltip()
        return super().eventFilter(obj, event)

    def show_tooltip(self):
        if not self.tooltip.isVisible():
            # 获取全局位置，并调整 tooltip 位置
            global_pos = self.widget.mapToGlobal(QPoint(0, self.widget.height()))
            self.tooltip.move(global_pos)
            self.tooltip.show()

    def hide_tooltip(self):
        if self.tooltip.isVisible():
            self.tooltip.hide()


def clear_layout(layout):
    """
    清空布局及其中的所有控件
    """
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())
            layout.removeItem(item)


def enable_button(button):
    """
    启用按钮
    """
    button.setDisabled(False)


def enable_all_buttons(buttons):
    """
    启用所有按钮
    """
    for button in buttons:
        button.setDisabled(False)


def disable_button(button):
    """
    禁用按钮
    """
    button.setDisabled(True)


def disable_all_buttons(buttons):
    """
    禁用所有按钮
    """
    for button in buttons:
        button.setDisabled(True)


def create_layout(layout_type, parent=None, spacing=None, margin=None):
    """
    创建布局
    """
    if layout_type == "vbox":
        layout = QVBoxLayout(parent)
    elif layout_type == "hbox":
        layout = QHBoxLayout(parent)
    elif layout_type == "grid":
        layout = QGridLayout(parent)
    elif layout_type == "form":
        layout = QFormLayout(parent)
    else:
        return None
    if parent:
        parent.setLayout(layout)
    if spacing:
        layout.setSpacing(spacing)
    if margin:
        left, top, right, bottom = margin
        layout.setContentsMargins(left, top, right, bottom)

    return layout


def create_label(text, style=None, width=None, height=None, alignment=None, external_link=False, link_activate=False, invisible=False, tooltip=""):
    """
    创建标签
    """
    label = QLabel(text)
    if style:
        label.setStyleSheet(style)
    if width:
        label.setFixedWidth(width)
    if height:
        label.setFixedHeight(height)
    if alignment:
        label.setAlignment(alignment)
    if external_link:
        label.setOpenExternalLinks(True)
    if link_activate:
        label.linkActivated.connect(open_local_url)
    if invisible:
        label.setVisible(False)
    if tooltip:
        TooltipManager(label, tooltip)

    return label


def create_line(height=None):
    """
    创建分割线
    """
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    if height:
        line.setFixedHeight(height)

    return line


def create_button(text, style=None, width=None, height=None, enabled=True, clicked=None, invisible=False, tooltip=""):
    """
    创建按钮
    """
    button = QPushButton(text)
    if style:
        button.setStyleSheet(style)
    if width:
        button.setFixedWidth(width)
    if height:
        button.setFixedHeight(height)
    if clicked:
        button.clicked.connect(clicked)
    if invisible:
        button.setVisible(False)
    if tooltip:
        TooltipManager(button, tooltip)
    button.setEnabled(enabled)

    return button


def create_lineEdit(text="", width=None, style=None, text_changed=None, int_validator=False, read_only=False, invisible=False, tooltip=""):
    """
    创建文本框
    """
    lineEdit = QLineEdit(text)
    if read_only:
        lineEdit.setStyleSheet("background-color: #c8c8c8;")
        lineEdit.setReadOnly(True)
    if width:
        lineEdit.setFixedWidth(width)
    if style:
        lineEdit.setStyleSheet(style)
    if text_changed:
        lineEdit.textChanged.connect(text_changed)
    if int_validator:
        lineEdit.setValidator(QIntValidator())
    if invisible:
        lineEdit.setVisible(False)
    if tooltip:
        TooltipManager(lineEdit, tooltip)

    return lineEdit


def create_comboBox(width=None, style=None, items=None, current_changed=None, invisible=False, tooltip=""):
    """
    创建下拉框
    """
    comboBox = QComboBox()
    if width:
        comboBox.setFixedWidth(width)
    if style:
        comboBox.setStyleSheet(style)
    if items:
        for item in items:
            comboBox.addItem(item)
    if current_changed:
        comboBox.currentTextChanged.connect(current_changed)
    if invisible:
        comboBox.setVisible(False)
    if tooltip:
        TooltipManager(comboBox, tooltip)

    return comboBox


def create_checkBox(text=None, width=None, checked=False, state_changed=None, tooltip=""):
    """
    创建复选框
    """
    checkBox = QCheckBox(text)
    if width:
        checkBox.setFixedWidth(width)
    checkBox.setChecked(checked)
    if state_changed:
        checkBox.stateChanged.connect(state_changed)
    if tooltip:
        TooltipManager(checkBox, tooltip)

    return checkBox


def create_textEdit(default_text="", width=None, max_height=None, read_only=False, line_wrap_mode=None, tooltip=""):
    """
    创建文本编辑框
    """
    textEdit = QTextEdit(default_text)
    if width:
        textEdit.setFixedWidth(width)
    if max_height:
        textEdit.setMaximumHeight(max_height)
    if read_only:
        textEdit.setReadOnly(True)
    if line_wrap_mode:
        textEdit.setLineWrapMode(line_wrap_mode)
    if tooltip:
        TooltipManager(textEdit, tooltip)
    return textEdit


def create_textBrowser(width=None, height=None, tooltip=""):
    """
    创建文本浏览器
    """
    textBrowser = QTextBrowser()
    if width:
        textBrowser.setFixedWidth(width)
    if height:
        textBrowser.setFixedHeight(height)
    if tooltip:
        TooltipManager(textBrowser, tooltip)

    return textBrowser


def add_widgets_to_gridlayout(layout, widgets):
    """
    将控件添加至 GridLayout 布局
    """
    for widget_info in widgets:
        widget = widget_info[0]
        row = widget_info[1]
        col = widget_info[2]
        row_span = widget_info[3] if len(widget_info) > 3 else 1
        col_span = widget_info[4] if len(widget_info) > 4 else 1
        alignment = widget_info[5] if len(widget_info) > 5 else Qt.Alignment()

        layout.addWidget(widget, row, col, row_span, col_span, alignment)


def add_widgets_to_vhboxlayout(layout, widgets):
    """
    将控件添加至 H/VBoxLayout 布局
    """
    for widget_info in widgets:
        widget = widget_info[0]
        stretch = widget_info[1] if len(widget_info) > 1 else 0
        alignment = widget_info[2] if len(widget_info) > 2 else Qt.Alignment()
        layout.addWidget(widget, stretch, alignment)


def open_local_url(url):
    """
    打开本地链接
    """
    url = url.replace("\\", "/")
    url = QUrl.fromLocalFile(url)
    QDesktopServices.openUrl(url)
