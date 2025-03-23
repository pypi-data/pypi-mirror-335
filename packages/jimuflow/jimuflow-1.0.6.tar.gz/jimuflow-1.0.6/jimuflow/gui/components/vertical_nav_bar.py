# This software is dual-licensed under the GNU General Public License (GPL)
# and a commercial license.
#
# You may use this software under the terms of the GNU GPL v3 (or, at your option,
# any later version) as published by the Free Software Foundation. See
# <https://www.gnu.org/licenses/> for details.
#
# If you require a proprietary/commercial license for this software, please
# contact us at jimuflow@gmail.com for more information.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Copyright (C) 2024-2025  Weng Jing

from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtWidgets import QWidget, QStylePainter, QPushButton, QFrame, QVBoxLayout, \
    QScrollArea


def is_ascii(char):
    return 0 <= ord(char) <= 127


class VerticalTextButton(QPushButton):

    def __init__(self, text, parent: QWidget = None):
        super().__init__(parent)
        self._text = text
        self._margin = 2

    def sizeHint(self):
        self.ensurePolished()
        fm = self.fontMetrics()
        width = 0
        height = 0
        for ch in self._text:
            if is_ascii(ch):
                width = max(width, fm.height())
                height += fm.horizontalAdvance(ch)
            else:
                width = max(width, fm.maxWidth())
                height += fm.height()
        return QSize(width + self._margin * 2, height + self._margin * 2)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QStylePainter(self)
        fm = self.fontMetrics()
        y = self._margin
        for ch in self._text:
            if is_ascii(ch):
                painter.translate(self.width() - self._margin, y)
                painter.rotate(90)
                painter.drawText(0, fm.ascent(), ch)
                painter.rotate(-90)
                painter.translate(-self.width() + self._margin, -y)
                y += fm.horizontalAdvance(ch)
            else:
                painter.drawText((self.width() - fm.horizontalAdvance(ch)) / 2, y + fm.ascent(), ch)
                y += fm.height()


class VerticalNavBar(QFrame):
    item_clicked = Signal(object)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area = QScrollArea()
        scroll_area.setFixedWidth(max(self.fontMetrics().maxWidth(), self.fontMetrics().height()) + 4)
        self._scroll_area = scroll_area
        content_widget = QWidget()
        self._content_widget = content_widget
        items_layout = QVBoxLayout(content_widget)
        items_layout.setContentsMargins(0, 0, 0, 0)
        self._items = []
        self._items_layout = items_layout
        scroll_area.setWidget(content_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll_area)

    def add_item(self, label, value):
        button = VerticalTextButton(label)
        button.clicked.connect(lambda: self.item_clicked.emit(value))
        self._items_layout.addWidget(button)
        self._items.append((label, value, button))
        QTimer.singleShot(0, self._resize_content_widget)

    def _resize_content_widget(self):
        content_size = self._content_widget.sizeHint()
        self._content_widget.resize(content_size)

    def clear(self):
        for _, _, button in self._items:
            button.deleteLater()
        self._items = []
