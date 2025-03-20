from PySide6.QtCore import QSettings, QThreadPool, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QFileDialog, QStatusBar
from dvatioff_audio.gui.gui_utils import disable_button, create_label, create_button, create_textBrowser, add_widgets_to_gridlayout, create_layout, enable_button
import dvatioff_audio.gui.gui_css as css
from dvatioff_audio.waapi.waapi_connector import WaapiConnectWorker
from functools import partial
from dvatioff_audio.waapi.waapi_object_selector import WwiseObjectSelectWorker
from dvatioff_audio.utils import open_url
import dvatioff_audio.globals as g


class MainWindow(QMainWindow):
    def __init__(self, ):
        super().__init__()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.setting = QSettings("dvatiOFF", "导入选择")
        self.setWindowIcon(QIcon(""))

        self.threadpool = QThreadPool()  # 线程池
        self.thread_waapi_connect = None
        self.worker_waapi_connect = None
        self.worker_get_wwise_selected_objects = None

        self.waapi_client = None  # WAAPI 客户端
        self.connect_status = False  # WAAPI 的连接状态
        self.connected = g.UNCONNECTED  # WAAPI 详细的连接状态，分为 未连接/已连接/连接至错误的 Wwise 工程或版本 三种状态
        self.wwise_project_name = None  # Wwise 工程名称
        self.wwise_version = None  # Wwise 版本
        self.statusBar = None  # 状态栏
        self.status_message = None  # 状态栏信息
        self.status_color = None  # 状态栏颜色（表示连接状态）

        self.confirm_window = None  # 各类操作执行后弹出的确认窗口

        self.wwise_selected_objects = []  # Wwise 中选中的对象
        self.wwise_selected_objects_legal = []  # Wwise 中选中的合法对象
        self.buttons_all = []  # 所有 GUI 按钮
        self.buttons_connect_activate = []  # 连接至 Wwise 后激活的按钮

        self.page_sfx_import = None  # 音效导入页面

        self.init_UI()

    def init_UI(self):
        """
        初始化UI
        """
        self.setWindowTitle("dvatiOFF-音频工具集")
        self.setFixedSize(1000, 600)
        self.init_status_bar()
        self.create_page_sfx_import()
        self.setup_menu()
        self.execute_waapi_connect_worker()

    def setup_menu(self):
        """
        设置菜单栏
        """
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet(css.FONT_PURE)

        menu_vo = menu_bar.addMenu("语音")
        action_vo_import = menu_vo.addAction("语音占位导入")
        action_vo_import.triggered.connect(partial(self.switch_page, 0))

        menu_audio = menu_bar.addMenu("音效")
        action_audio_3p = menu_audio.addAction("音效导入")
        action_audio_3p.triggered.connect(partial(self.switch_page, 0))
        menu_audio.addAction(action_audio_3p)

        menu_help = menu_bar.addMenu("帮助")
        action_help = menu_help.addAction("音效命名规则")
        action_help.triggered.connect(partial(open_url, ""))
        menu_help.addAction(action_help)

    def remove_widgets(self):
        """
        移除所有的页面
        """
        self.stacked_widget.removeWidget(self.page_sfx_import)
        self.page_sfx_import.deleteLater()

    def refresh_UI(self):
        """
        刷新页面显示
        """
        self.buttons_all = []
        self.buttons_connect_activate = []
        self.remove_widgets()
        self.create_page_sfx_import()
        if not self.connect_status:
            self.disable_buttons()

    def switch_page(self, index):
        """
        切换页面
        :param index: 页面索引(见全局变量定义)
        """
        if index == g.INDEX_PAGE_SFX_IMPORT:
            self.setFixedSize(1000, 400)

        self.refresh_UI()
        self.stacked_widget.setCurrentIndex(index)

    # START ------------------ 状态栏相关 ------------------

    def init_status_bar(self):
        """
        初始化状态栏
        """
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.status_message = create_label("未连接至 Wwise Authoring", css.LABEL_STYLE_STATUS)
        self.statusBar.addPermanentWidget(self.status_message)
        self.status_color = create_label("  ", css.LABEL_STATUS_RED, 16, 16)
        self.status_color.setStyleSheet(css.LABEL_STATUS_RED)
        self.statusBar.addPermanentWidget(self.status_color)

    def execute_waapi_connect_worker(self):
        self.worker_waapi_connect = WaapiConnectWorker()
        self.worker_waapi_connect.signal_connection_status.signal.connect(self.status_changed)
        self.worker_waapi_connect.signal_waapi_client.signal.connect(self.get_waapi_client)
        self.worker_waapi_connect.signal_project_name.signal.connect(self.get_wwise_project_name_info)

        self.threadpool.start(self.worker_waapi_connect)

    @Slot(bool)
    def status_changed(self, status):
        """
        连接状态改变时更新状态栏显示
        """
        self.connect_status = status
        if status:
            if self.wwise_project_name == g.WWISE_PROJECT_NAME and self.wwise_version == g.WWISE_VERSION:
                self.status_color.setStyleSheet(css.LABEL_STATUS_GREEN)
                self.status_message.setText(f"{self.wwise_project_name} - {self.wwise_version} 已连接")
                self.enable_buttons()
                self.connected = g.CONNECTED
            elif self.wwise_project_name == g.WWISE_PROJECT_NAME and self.wwise_version != g.WWISE_VERSION:
                self.status_color.setStyleSheet(css.LABEL_STATUS_YELLOW)
                self.status_message.setText(f"{self.wwise_project_name} - {self.wwise_version} 已连接 (Wwise 版本不匹配)")
                self.disable_buttons()
                self.connected = g.WRONG_CONNECTED
            elif self.wwise_project_name != g.WWISE_PROJECT_NAME and self.wwise_version == g.WWISE_VERSION:
                self.status_color.setStyleSheet(css.LABEL_STATUS_YELLOW)
                self.status_message.setText(f"{self.wwise_project_name} - {self.wwise_version} 已连接 (Wwise 工程不匹配)")
                self.disable_buttons()
                self.connected = g.WRONG_CONNECTED
            else:
                self.status_color.setStyleSheet(css.LABEL_STATUS_YELLOW)
                self.status_message.setText(f"{self.wwise_project_name} - {self.wwise_version} 已连接 (Wwise 工程和版本不匹配)")
                self.disable_buttons()
                self.connected = g.WRONG_CONNECTED
        else:
            self.status_color.setStyleSheet(css.LABEL_STATUS_RED)
            self.status_message.setText("未连接至 Wwise Authoring")
            self.disable_buttons()
            self.connected = g.UNCONNECTED

        if self.connected != g.CONNECTED and self.worker_get_wwise_selected_objects:
            self.worker_get_wwise_selected_objects.stop()
            self.worker_get_wwise_selected_objects = None

    @Slot(object)
    def get_waapi_client(self, client):
        self.waapi_client = client

    def execute_get_wwise_objects_worker(self):
        self.worker_get_wwise_selected_objects = WwiseObjectSelectWorker(self.waapi_client)
        self.worker_get_wwise_selected_objects.signal_selected_objects.signal.connect(self.get_selected_objects)
        self.threadpool.start(self.worker_get_wwise_selected_objects)

    @Slot(list)
    def get_selected_objects(self, selected_objects):
        if len(selected_objects) != len(self.wwise_selected_objects) or any(a != b for a, b in zip(selected_objects, self.wwise_selected_objects)):
            self.wwise_selected_objects = selected_objects
            # self.add_scroll_content(self.layout_scroll_event_soundbank)

    @Slot(str, str)
    def get_wwise_project_name_info(self, project_name, wwise_version):
        self.wwise_project_name = project_name
        self.wwise_version = wwise_version

    # END ------------------ 状态栏相关 ------------------

    # START ------------------ 页面相关 ------------------

    # ================== 音效占位导入 ==================
    def create_page_sfx_import(self):
        """
        创建音效导入页面
        """
        self.page_sfx_import = QWidget()
        self.stacked_widget.addWidget(self.page_sfx_import)

        layout = create_layout("grid", self.page_sfx_import, margin=(50, 50, 50, 50))

        # ================== 元素添加 ==================
        title = create_label("音效占位导入", css.LABEL_STYLE_TITLE, height=80)

        label_select_excel = create_label("选择 Excel 文件: ", css.LABEL_STYLE, width=100)
        textBrowser_select_execl = create_textBrowser(width=700, height=36)
        button_select_excel = create_button("选择", css.BUTTON_STYLE_PINK, tooltip="选择导入音效所需的 Excel 文件")
        button_name_vfy = create_button("音频文件名校验", css.BUTTON_STYLE_PINK, enabled=False)
        button_import = create_button("导入", css.BUTTON_STYLE_PINK, enabled=False)

        # ================== 事件绑定 ==================
        button_select_excel.clicked.connect(partial(self.open_file_dialog, textBrowser_select_execl, button_name_vfy, button_import))

        # ================== 页面布局 ==================
        add_widgets_to_gridlayout(layout, [
            [title, 0, 0, 1, 3],
            [label_select_excel, 1, 0], [textBrowser_select_execl, 1, 1], [button_select_excel, 1, 2],
            [button_name_vfy, 2, 0, 1, 3],
            [button_import, 3, 0, 1, 3]
        ])

    # END ------------------ 页面相关 ------------------

    def disable_buttons(self):
        """
        禁用所有按钮
        """
        for button in self.buttons_all:
            button.setDisabled(True)

    def enable_buttons(self):
        """
        启用所有按钮
        """
        for button in self.buttons_connect_activate:
            button.setDisabled(False)

    def open_file_dialog(self, textBrowser, button_name_vfy, button_import):
        last_file_path = self.setting.value("last_file_path", "")
        file_path, _ = QFileDialog.getOpenFileName(self, '选择文件', last_file_path, "Excel 文件 (*.xlsx)")

        if file_path:
            enable_button(button_name_vfy)
            if file_path != textBrowser.toPlainText():
                disable_button(button_import)
                textBrowser.setText(file_path)
                self.setting.setValue("last_folder_path", file_path)

    def open_confirm_window(self, **kwargs):
        """
        打开确认窗口
        """
        task = kwargs.get("task")
        if task == g.INDEX_PAGE_VO_IMPORT:
            title = "确认"
            message = "是否将正式资源导入 Wwise?"

    def execute_task(self, **kwargs):
        """
        关闭确认窗口
        """
        task = kwargs.get("task")

