# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtSvgWidgets import *
from PySide6.QtWidgets import *

from mangoui.models.models import TitleBarMenusModel
from mangoui.settings.settings import THEME
from .mango_div import MangoDiv
from .mango_title_button import MangoTitleButton

_is_maximized = False
_old_size = QSize()


class MangoTitleBar(QWidget):
    clicked = Signal(object)
    released = Signal(object)

    def __init__(
            self,
            parent,
            app_parent,
            logo_image=":/icons/app_icon.svg",
    ):
        super().__init__()
        self.parent = parent
        self.app_parent = app_parent
        self._logo_image = logo_image

        self._is_custom_title_bar = True

        self.title_bar_layout = QVBoxLayout(self)
        self.title_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.bg = QFrame()

        self.bg_layout = QHBoxLayout(self.bg)
        self.bg_layout.setContentsMargins(10, 0, 5, 0)
        self.bg_layout.setSpacing(0)

        self.div_1 = MangoDiv(THEME.bg_300)
        self.div_2 = MangoDiv(THEME.bg_300)
        self.div_3 = MangoDiv(THEME.bg_300)

        # 带移动应用程序的左框
        self.top_logo = QLabel()
        self.top_logo_layout = QVBoxLayout(self.top_logo)
        self.top_logo_layout.setContentsMargins(0, 0, 0, 0)

        self.logo_svg = QSvgWidget()
        self.logo_svg.load(self._logo_image)
        self.top_logo_layout.addWidget(self.logo_svg, Qt.AlignCenter, Qt.AlignCenter)  # type: ignore

        # 标题标签
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignVCenter)  # type: ignore
        self.title_label.setStyleSheet(f'font: {THEME.font.title_size}pt {THEME.font.family}')

        # 自定义按钮布局
        self.custom_buttons_layout = QHBoxLayout()
        self.custom_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_buttons_layout.setSpacing(3)

        # 最小化按钮
        self.minimize_button = MangoTitleButton(
            self.parent,
            self.app_parent,
            tooltip_text="收起",
            icon_path=":/icons/icon_minimize.svg"
        )

        # 最大化/恢复按钮
        self.maximize_restore_button = MangoTitleButton(
            self.parent,
            self.app_parent,
            tooltip_text="最大化",
            icon_path=":/icons/icon_maximize.svg"
        )

        # 关闭按钮
        self.close_button = MangoTitleButton(
            self.parent,
            self.app_parent,
            tooltip_text="关闭",
            icon_path=":/icons/icon_close.svg"
        )

        self.title_bar_layout.addWidget(self.bg)

        self.bg.setStyleSheet(f"background-color: {THEME.bg_300}; border-radius: {THEME.border_radius};")

        self.top_logo.setMinimumWidth(40)
        self.top_logo.setMaximumWidth(40)

        def moveWindow(event):
            # 如果最大化改变为正常
            if parent.isMaximized():
                self.maximize_restore()
                # self.resize(_old_size)
                curso_x = parent.pos().x()
                curso_y = event.globalPos().y() - QCursor.pos().y()
                parent.move(curso_x, curso_y)
            # 移动窗口
            if event.buttons() == Qt.LeftButton:  # type: ignore
                parent.move(parent.pos() + event.globalPos() - parent.drag_pos)
                parent.drag_pos = event.globalPos()
                event.accept()

        # 移动应用程序小部件
        if self._is_custom_title_bar:
            self.top_logo.mouseMoveEvent = moveWindow
            self.div_1.mouseMoveEvent = moveWindow
            self.title_label.mouseMoveEvent = moveWindow
            self.div_2.mouseMoveEvent = moveWindow
            self.div_3.mouseMoveEvent = moveWindow

        # 最大化/恢复
        if self._is_custom_title_bar:
            self.top_logo.mouseDoubleClickEvent = self.maximize_restore
            self.div_1.mouseDoubleClickEvent = self.maximize_restore
            self.title_label.mouseDoubleClickEvent = self.maximize_restore
            self.div_2.mouseDoubleClickEvent = self.maximize_restore

        # 添加按钮按钮

        # 功能
        self.minimize_button.released.connect(lambda: parent.showMinimized())
        self.maximize_restore_button.released.connect(lambda: self.maximize_restore())
        self.close_button.released.connect(lambda: parent.close())

        # 添加控件到布局
        self.bg_layout.addWidget(self.top_logo)

        # 添加占位符 div_1
        self.bg_layout.addWidget(self.div_1)
        self.bg_layout.setStretch(self.bg_layout.indexOf(self.div_1), -1)  # 设置 div_1 的伸缩因子

        # 添加 title_label，靠近 top_logo
        self.bg_layout.addWidget(self.title_label)

        # 添加占位符 div_2
        self.bg_layout.addWidget(self.div_2)
        self.bg_layout.setStretch(self.bg_layout.indexOf(self.div_2), 1)  # 设置 div_2 的伸缩因子

        # 添加自定义按钮布局
        self.bg_layout.addLayout(self.custom_buttons_layout)

        # ADD Buttons
        if self._is_custom_title_bar:
            self.bg_layout.addWidget(self.minimize_button)
            self.bg_layout.addWidget(self.maximize_restore_button)
            self.bg_layout.addWidget(self.close_button)

    def add_menus(self, parameters: list[TitleBarMenusModel]):
        if parameters is None:
            return
        for parameter in parameters:
            self.menu = MangoTitleButton(
                self.parent,
                self.app_parent,
                btn_id=parameter.btn_id,
                tooltip_text=parameter.btn_tooltip,
                icon_path=parameter.btn_icon,
                is_active=parameter.is_active
            )
            self.menu.clicked.connect(self.btn_clicked)
            self.menu.released.connect(self.btn_released)

            self.custom_buttons_layout.addWidget(self.menu)

        if self._is_custom_title_bar:
            self.custom_buttons_layout.addWidget(self.div_3)

    # 标题栏菜单发出信号
    def btn_clicked(self):
        self.clicked.emit(self.menu)

    def btn_released(self):
        self.released.emit(self.menu)

    # 设置标题栏文本
    def set_title(self, title):
        self.title_label.setText(title)

    # 最大化并恢复父窗口
    def maximize_restore(self, e=None):
        global _is_maximized
        global _old_size

        # 更改UI并调整夹点大小
        def change_ui():
            if _is_maximized:
                self.parent.central_widget_layout.setContentsMargins(0, 0, 0, 0)  # type: ignore
                self.parent.window.set_stylesheet(border_radius=0, border_size=0)  # type: ignore
                self.maximize_restore_button.set_icon(":/icons/icon_restore.svg")
            else:
                self.parent.central_widget_layout.setContentsMargins(10, 10, 10, 10)  # type: ignore
                self.parent.window.set_stylesheet(border_radius=10, border_size=2)  # type: ignore
                self.maximize_restore_button.set_icon(":/icons/icon_maximize.svg")

        # 检查事件
        if self.parent.isMaximized():
            _is_maximized = False
            self.parent.showNormal()
            change_ui()
        else:
            _is_maximized = True
            _old_size = QSize(self.parent.width(), self.parent.height())
            self.parent.showMaximized()
            change_ui()
