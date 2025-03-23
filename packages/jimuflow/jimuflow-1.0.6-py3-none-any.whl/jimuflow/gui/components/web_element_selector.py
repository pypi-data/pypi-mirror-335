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

from PySide6.QtCore import QSortFilterProxyModel, Slot, QModelIndex, Signal, QEvent, QPoint, QAbstractItemModel
from PySide6.QtGui import QStandardItemModel, Qt, QPixmap
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QTreeView, QPushButton, QFrame, QHBoxLayout, \
    QSizePolicy, QDialog, QVBoxLayout, QDialogButtonBox

from jimuflow.common.uri_utils import build_web_element_uri, is_variable_uri, parse_web_element_uri, \
    parse_variable_uri, build_variable_uri, rename_variable_in_element_uri, get_variable_reference_in_element_uri
from jimuflow.datatypes import DataTypeRegistry
from jimuflow.definition import VariableDef
from jimuflow.gui.app import AppContext
from jimuflow.gui.elements_widget import CaptureElementButton
from jimuflow.locales.i18n import gettext


class WebElementSelectorPopupModel(QAbstractItemModel):
    DYNAMIC_ELEMENTS_GROUP_ID = 1
    STATIC_ELEMENT_GROUP_ID = 2
    VARIABLE_ID_OFFSET = 1000000
    ELEMENT_ID_OFFSET = 2000000

    def __init__(self, variables: list[VariableDef], elements_model: QStandardItemModel, parent=None):
        super().__init__(parent)
        self._element_variables = [var_def for var_def in variables if var_def.type == 'WebElement']
        self._elements_model = elements_model
        self._elements_model.dataChanged.connect(self._on_elements_model_data_changed)
        self._elements_model.rowsInserted.connect(self._on_elements_model_rows_inserted)
        self._elements_model.rowsRemoved.connect(self._on_elements_model_rows_removed)

    def reset(self, variables: list[VariableDef], elements_model: QStandardItemModel):
        self.beginResetModel()
        self._element_variables = [var_def for var_def in variables if var_def.type == 'WebElement']
        self._elements_model = elements_model
        self._elements_model.dataChanged.connect(self._on_elements_model_data_changed)
        self._elements_model.rowsInserted.connect(self._on_elements_model_rows_inserted)
        self._elements_model.rowsRemoved.connect(self._on_elements_model_rows_removed)
        self.endResetModel()

    def _on_elements_model_data_changed(self, top_left, bottom_right, roles):
        self.dataChanged.emit(self._map_elements_model_index(top_left), self._map_elements_model_index(bottom_right),
                              roles)

    def _group_row_offset(self):
        return 1 if len(self._element_variables) > 0 else 0

    def _on_elements_model_rows_inserted(self, parent, first, last):
        if not parent.isValid():
            self.beginInsertRows(QModelIndex(), first + self._group_row_offset(), last + self._group_row_offset())
            self.endInsertRows()
        else:
            self.beginInsertRows(self._map_elements_model_index(parent), first, last)
            self.endInsertRows()

    def _on_elements_model_rows_removed(self, parent, first, last):
        if not parent.isValid():
            self.beginRemoveRows(QModelIndex(), first + self._group_row_offset(), last + self._group_row_offset())
            self.endRemoveRows()
        else:
            self.beginRemoveRows(self._map_elements_model_index(parent), first, last)
            self.endRemoveRows()

    def _map_elements_model_index(self, source_index: QModelIndex):
        if not source_index.isValid():
            return QModelIndex()
        elif not source_index.parent().isValid():
            return self.index(source_index.row() + self._group_row_offset(), 0)
        else:
            return self.index(source_index.row(), source_index.column(),
                              self._map_elements_model_index(source_index.parent()))

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            if len(self._element_variables) > 0:
                if row == 0:
                    return self.createIndex(row, column, WebElementSelectorPopupModel.DYNAMIC_ELEMENTS_GROUP_ID)
                else:
                    return self.createIndex(row, column, WebElementSelectorPopupModel.STATIC_ELEMENT_GROUP_ID)
            else:
                return self.createIndex(row, column, WebElementSelectorPopupModel.STATIC_ELEMENT_GROUP_ID)
        else:
            if parent.internalId() == WebElementSelectorPopupModel.DYNAMIC_ELEMENTS_GROUP_ID:
                return self.createIndex(row, column, WebElementSelectorPopupModel.VARIABLE_ID_OFFSET + parent.row())
            else:
                return self.createIndex(row, column, WebElementSelectorPopupModel.ELEMENT_ID_OFFSET + parent.row())

    def parent(self, index: QModelIndex):
        internal_id = index.internalId()
        if (internal_id == WebElementSelectorPopupModel.DYNAMIC_ELEMENTS_GROUP_ID
                or internal_id == WebElementSelectorPopupModel.STATIC_ELEMENT_GROUP_ID):
            return QModelIndex()
        elif internal_id >= WebElementSelectorPopupModel.ELEMENT_ID_OFFSET:
            return self.createIndex(internal_id - WebElementSelectorPopupModel.ELEMENT_ID_OFFSET, 0,
                                    WebElementSelectorPopupModel.STATIC_ELEMENT_GROUP_ID)
        else:
            return self.createIndex(internal_id - WebElementSelectorPopupModel.VARIABLE_ID_OFFSET, 0,
                                    WebElementSelectorPopupModel.DYNAMIC_ELEMENTS_GROUP_ID)

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return self._elements_model.rowCount() + self._group_row_offset()
        if parent.parent().isValid():
            return 0
        if parent.internalId() == WebElementSelectorPopupModel.DYNAMIC_ELEMENTS_GROUP_ID:
            return len(self._element_variables)
        else:
            source_parent = self._elements_model.index(parent.row() - self._group_row_offset(), 0)
            return self._elements_model.rowCount(source_parent)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        internal_id = index.internalId()
        if internal_id == WebElementSelectorPopupModel.STATIC_ELEMENT_GROUP_ID:
            source_index = self._elements_model.index(index.row() - self._group_row_offset(), 0)
            return source_index.data(role)
        if internal_id >= WebElementSelectorPopupModel.ELEMENT_ID_OFFSET:
            source_parent = self._elements_model.index(index.parent().row() - self._group_row_offset(), 0)
            source_index = self._elements_model.index(index.row(), 0, source_parent)
            return source_index.data(role)

        if role == Qt.ItemDataRole.DisplayRole:
            if internal_id == WebElementSelectorPopupModel.DYNAMIC_ELEMENTS_GROUP_ID:
                return gettext('Dynamic elements')
            elif internal_id >= WebElementSelectorPopupModel.VARIABLE_ID_OFFSET:
                return self._element_variables[index.row()].name
        elif role == Qt.ItemDataRole.UserRole + 1:
            if internal_id >= WebElementSelectorPopupModel.VARIABLE_ID_OFFSET:
                return build_variable_uri(self._element_variables[index.row()].name)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        internal_id = index.internalId()
        if (internal_id == WebElementSelectorPopupModel.DYNAMIC_ELEMENTS_GROUP_ID
                or internal_id == WebElementSelectorPopupModel.STATIC_ELEMENT_GROUP_ID):
            return Qt.ItemFlag.ItemIsEnabled
        else:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


class WebElementSelectWidget(QWidget):
    element_added = Signal(str)
    element_double_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        keyword_input = QLineEdit()
        keyword_input.setPlaceholderText(gettext('Search element'))
        keyword_input.textEdited.connect(self.on_keyword_edited)
        layout.addWidget(keyword_input, 0, 0, 1, 1)
        capture_button = CaptureElementButton()
        capture_button.element_added.connect(self._on_element_added)
        layout.addWidget(capture_button, 0, 1, 1, 2)
        tree_view = QTreeView()
        tree_model = WebElementSelectorPopupModel([], QStandardItemModel(), self)
        proxy_model = QSortFilterProxyModel(self)
        proxy_model.setRecursiveFilteringEnabled(True)
        proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        proxy_model.setSourceModel(tree_model)
        tree_view.setModel(proxy_model)
        tree_view.header().hide()
        tree_view.selectionModel().currentChanged.connect(self.on_current_changed)
        tree_view.doubleClicked.connect(self.on_double_clicked)
        layout.addWidget(tree_view, 1, 0, 1, 1)
        preview_label = QLabel()
        preview_label.setFixedWidth(200)
        preview_label.setFrameShape(QFrame.Shape.StyledPanel)
        layout.addWidget(preview_label, 1, 1, 1, 2)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        self.setFixedWidth(700)
        self.setFixedHeight(300)
        self._tree_model = tree_model
        self._proxy_model = proxy_model
        self._preview_label = preview_label
        self._variables = []
        self._tree_view = tree_view

    def set_variables(self, variables: list[VariableDef]):
        self._variables = variables
        self._tree_model.reset(variables, AppContext.app().web_elements_model)
        self._tree_view.expandAll()

    @Slot(str)
    def on_keyword_edited(self, text):
        self._proxy_model.setFilterFixedString(text)

    @Slot(QModelIndex, QModelIndex)
    def on_current_changed(self, current: QModelIndex, previous: QModelIndex):
        if not current.isValid() or not current.parent().isValid():
            return
        item_data = current.data(Qt.ItemDataRole.UserRole + 1)
        if is_variable_uri(item_data):
            self._preview_label.clear()
            return
        element_id = parse_web_element_uri(item_data)
        element_info = AppContext.app().app_package.get_web_element_by_id(element_id)
        snapshot = element_info.get('snapshot', None)
        if not snapshot:
            self._preview_label.clear()
            return
        pixmap = QPixmap(snapshot)
        if pixmap.isNull():
            self._preview_label.clear()
            return
        pixmap_size = pixmap.size()
        label_size = self._preview_label.contentsRect().size()
        if pixmap_size.width() > label_size.width() or pixmap_size.height() > label_size.height():
            pixmap = pixmap.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
        self._preview_label.setPixmap(pixmap)

    @Slot(QModelIndex)
    def on_double_clicked(self, index: QModelIndex):
        if index.isValid() and index.parent().isValid():
            item_data = index.data(Qt.ItemDataRole.UserRole + 1)
            self.element_double_clicked.emit(item_data)

    def get_current_element_uri(self):
        index = self._tree_view.currentIndex()
        if index.isValid() and index.parent().isValid():
            return index.data(Qt.ItemDataRole.UserRole + 1)

    @Slot(str)
    def _on_element_added(self, element_id):
        element_info = AppContext.app().app_package.get_web_element_by_id(element_id)
        self.element_added.emit(build_web_element_uri(element_info))

    def set_current_uri(self, uri: str):
        for group_row in range(self._tree_model.rowCount()):
            group_index = self._tree_model.index(group_row, 0)
            for element_row in range(self._tree_model.rowCount(group_index)):
                element_index = self._tree_model.index(element_row, 0, group_index)
                if element_index.data(Qt.ItemDataRole.UserRole + 1) == uri:
                    self._tree_view.setCurrentIndex(self._proxy_model.mapFromSource(element_index))
                    return


class WebElementSelectorPopup(QWidget):
    accepted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(gettext('Element library')))
        self._select_widget = WebElementSelectWidget()
        self._select_widget.element_added.connect(self._on_element_added)
        self._select_widget.element_double_clicked.connect(self.on_double_clicked)
        layout.addWidget(self._select_widget)
        grid_layout: QGridLayout = self._select_widget.layout()
        cancel_button = QPushButton(gettext('Cancel'))
        cancel_button.clicked.connect(self.close)
        ok_button = QPushButton(gettext('OK'))
        ok_button.clicked.connect(self.on_ok)
        grid_layout.addWidget(cancel_button, 2, 1, 1, 1)
        grid_layout.addWidget(ok_button, 2, 2, 1, 1)

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._select_widget.set_variables(variables)

    def on_double_clicked(self, uri):
        self.accepted.emit(uri)
        self.close()

    def _on_element_added(self, uri):
        self.accepted.emit(uri)
        self.close()

    @Slot()
    def on_ok(self):
        current_element_uri = self._select_widget.get_current_element_uri()
        if current_element_uri:
            self.accepted.emit(current_element_uri)
        self.close()

    def set_current_uri(self, uri: str):
        self._select_widget.set_current_uri(uri)


class WebElementSelector(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._button = QLabel("{e}", self)
        self._button.setStyleSheet("color:blue;")
        self._button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._button.installEventFilter(self)
        self._button_top_margin = 4
        self._button_size = self._button.sizeHint()
        self._right_margin = self._button_size.width()
        self._popup = WebElementSelectorPopup(self)
        self._popup.accepted.connect(self._on_accepted)
        self.setMinimumWidth(100)
        self.setReadOnly(True)
        self.setFixedHeight(self.fontMetrics().height() + 10)
        self._value = ''

    def resizeEvent(self, e):
        super().resizeEvent(e)
        x = self.rect().right() - self._button_size.width()
        self._button.setGeometry(x, self.rect().top() + self._button_top_margin,
                                 self._button_size.width(), self._button_size.height())

    def eventFilter(self, watched, event):
        if watched is self._button:
            if event.type() == QEvent.Type.MouseButtonPress:
                self._show_popup()
                return True
        return super().eventFilter(watched, event)

    def _show_popup(self):
        pos = self.mapToGlobal(QPoint(0, self.height() - 2))
        self._popup.move(pos)
        self._popup.set_current_uri(self.get_value())
        self._popup.show()

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._popup.set_variables(variables, type_registry)

    def get_value(self):
        return self._value

    def set_value(self, value: str):
        self._value = value
        if not value:
            return
        variable_name = parse_variable_uri(value)
        if variable_name:
            self.setText(variable_name)
            return
        element_id = parse_web_element_uri(value)
        if element_id:
            element_info = AppContext.app().app_package.get_web_element_by_id(element_id)
            if element_info:
                self.setText(element_info['name'])

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.button() == Qt.MouseButton.LeftButton:
            self._show_popup()

    def _on_accepted(self, uri):
        self.set_value(uri)


class WebElementEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        selector = WebElementSelector()
        layout.addWidget(selector, 1)
        capture_button = CaptureElementButton()
        capture_button.element_added.connect(self._on_element_added)
        layout.addWidget(capture_button)
        self._selector = selector
        self._capture_button = capture_button
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._selector.set_variables(variables, type_registry)

    def get_value(self):
        return self._selector.get_value()

    def set_value(self, value: str):
        self._selector.set_value(value)

    def setPlaceholderText(self, text):
        self._selector.setPlaceholderText(text)

    @Slot(str)
    def _on_element_added(self, element_id):
        element_info = AppContext.app().app_package.get_web_element_by_id(element_id)
        self.set_value(build_web_element_uri(element_info))

    def rename_variable_in_value(self, value, old_name, new_name):
        if not value:
            return value, False
        return rename_variable_in_element_uri(value, old_name, new_name)

    def get_variable_reference_in_value(self, value, var_name):
        if not value:
            return 0
        return get_variable_reference_in_element_uri(value, var_name)


class WebElementSelectDialog(QDialog):
    def __init__(self, variables: list[VariableDef], parent=None):
        super().__init__(parent)
        self.setWindowTitle(gettext('Select Web Element'))
        self.selected_element = ''
        self._select_widget = WebElementSelectWidget()
        self._select_widget.element_added.connect(self._on_element_added)
        self._select_widget.element_double_clicked.connect(self.on_double_clicked)
        layout = QVBoxLayout(self)
        layout.addWidget(self._select_widget)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accepted)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        layout.addWidget(button_box)
        self._select_widget.set_variables(variables)

    def _on_accepted(self):
        self.selected_element = self._select_widget.get_current_element_uri()
        self.accept()

    def on_double_clicked(self, uri):
        self.selected_element = uri
        self.accept()

    def _on_element_added(self, uri):
        self.selected_element = uri
        self.accept()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    popup = WebElementEdit()
    popup.show()
    app.exec()
