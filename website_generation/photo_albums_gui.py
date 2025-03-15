import argparse
import math
import sys
from typing import Iterable

from config import AbstractConfig, Config, TestConfig
from photo_album.photo_album_db import (
    Album, Photo, PhotoAlbumDb
)

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import (
    QAbstractListModel, 
    QAbstractTableModel,
    QBuffer,
    QByteArray,
    QIODevice,
    QItemSelectionModel, 
    QModelIndex,
    QRect,
    QSize,
    Qt
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QListView, 
    QMainWindow, 
    QPushButton,
    QSizePolicy,
    QSpacerItem, 
    QStackedLayout,
    QStyledItemDelegate,
    QTableView,
    QVBoxLayout,
    QWidget
)

def make_parser():
    parser = argparse.ArgumentParser(
        description='Graphical interface for editing photo albums',
    )
    parser.add_argument(
        '-t', '--test', action='store_true',
        help='Use the test database')
    return parser

def pixmap_to_byte_array(pixmap: QPixmap) -> QByteArray:
    ba = QByteArray()
    buff = QBuffer(ba)
    buff.open(QIODevice.OpenModeFlag.WriteOnly)
    pixmap.save(buff, 'JPG')
    byte_array = ba.data()
    return byte_array

class PhotoAlbumsListModel(QAbstractListModel):
    def __init__(self, config: AbstractConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = PhotoAlbumDb(config)
        self.data = self.db.get_albums()
        self.data.sort(reverse=True)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> str|QSize|None:
        if role == Qt.ItemDataRole.DisplayRole:
            return self.data[index.row()].dirname
        if role == Qt.ItemDataRole.SizeHintRole:
            return QSize(175, 50)
        
    def rowCount(self, index: QModelIndex) -> int:
        return len(self.data)

class PhotoAlbumsListView(QListView):
    pass

class PhotoAlbumImagesTableModel(QAbstractTableModel):
    COL_COUNT = 4

    def __init__(self, album: Album, config: AbstractConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.album = album
        self.db = PhotoAlbumDb(config)
        self.data: list[tuple[Photo, QPixmap]] = []
        self.unsaved_data = None

    def init_data(self):
        db_photos = self.db.get_resized_album_photos(self.album.rowid)
        rows = math.ceil(len(db_photos) / self.COL_COUNT)

        self.beginInsertRows(QModelIndex(), 0, rows-1)
        for p in db_photos:
            pixmap = QPixmap(
                f'{config.photo_albums_root}/{self.album.dirname}/{p.filename}')
            pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
            self.data.append((p, pixmap))
        self.data.sort(key=lambda x: x[0].position)
        self.endInsertRows()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> QPixmap:
        if role == Qt.ItemDataRole.DecorationRole:
            i = index.row() * self.COL_COUNT + index.column()
            if i < len(self.data):
                if self.unsaved_data:
                    return self.unsaved_data[i][1]
                else:
                    return self.data[i][1]
        
    def rowCount(self, index: QModelIndex) -> int:
        return math.ceil(len(self.data) / self.COL_COUNT)
    
    def columnCount(self, index: QModelIndex):
        return self.COL_COUNT
    
    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled
        )
    
    def mimeData(self, indexes: Iterable[QModelIndex]):
        mime_data = super().mimeData(indexes)
        if indexes:
            row, col = indexes[0].row(), indexes[0].column()
            i = row * self.COL_COUNT + col
            data = self.unsaved_data if self.unsaved_data else self.data
            if i < len(data):
                pixmap = self.data[i][1]
                byte_array = pixmap_to_byte_array(pixmap)
                mime_data.setData('application/x-pixmap', byte_array)
                mime_data.setText(f'{row},{col}')
                return mime_data
                
    def dropMimeData(self, mime_data, action, row, column, parent) -> bool:
        if not mime_data.hasFormat("application/x-pixmap"):
            return False
        source_row, source_col = map(int, mime_data.text().split(","))
        source_i = source_row * self.COL_COUNT + source_col
        dest_i = parent.row() * self.COL_COUNT + parent.column()

        if source_i < len(self.data) and dest_i < len(self.data):
            self.insert_source_before_dest(source_i, dest_i)
            self.dataChanged.emit(
                self.index(0, 0), 
                self.index(self.rowCount(0)-1, self.columnCount(0)-1))
            return True
        return False
    
    def insert_source_before_dest(self, source_i, dest_i) -> None:
        if not self.unsaved_data:
            self.unsaved_data = self.data.copy()
        item = self.unsaved_data.pop(source_i)
        self.unsaved_data.insert(dest_i, item)

    def cancel_unsaved_data(self):
        self.unsaved_data = None 
        self.dataChanged.emit(
            self.index(0, 0), 
            self.index(self.rowCount(0)-1, self.columnCount(0)-1))

    def save_unsaved_data(self):
        self.db.update_photos_with_new_order(
            [item[0] for item in self.unsaved_data])
        self.data = self.unsaved_data
        self.unsaved_data = None

class PhotoDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        pixmap = index.data(Qt.ItemDataRole.DecorationRole)
        if isinstance(pixmap, QPixmap):
            rect = option.rect
            pixmap_size = pixmap.size()
            x = rect.x() + (rect.width() - pixmap_size.width()) // 2
            y = rect.y() + (rect.height() - pixmap_size.height()) // 2
            target_rect = QRect(x, y, pixmap_size.width(), pixmap_size.height())
            painter.drawPixmap(target_rect, pixmap)
        else:
            super().paint(painter, option, index)

class PhotoAlbumImagesTableView(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(10)

        self.setShowGrid(False)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        

class MainWindow(QMainWindow):
    def __init__(self, config: AbstractConfig):
        super().__init__()
        self.models: list[PhotoAlbumImagesTableModel] = []

        self.setWindowTitle("Photo Album Editor")
        self.setFixedSize(940, 600)

        page_layout = QHBoxLayout()
        self.main_vertical_layout = QVBoxLayout()
        self.stacked_layout = QStackedLayout()
        self.save_cancel_button_layout = QHBoxLayout()

        # left pane selection list
        self.photoAlbumsListView = PhotoAlbumsListView()
        self.photoAlbumsListModel = PhotoAlbumsListModel(config)
        self.photoAlbumsListView.setModel(self.photoAlbumsListModel)
        self.photoAlbumsListView.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        page_layout.addWidget(self.photoAlbumsListView)
        ix = self.photoAlbumsListModel.index(0, 0)
        self.photoAlbumsListView.selectionModel().setCurrentIndex(ix, QItemSelectionModel.SelectionFlag.Select)
        self.photoAlbumsListView.selectionModel().currentChanged.connect(self.currentAlbumChanged)

        # stacked layout of photo album images
        for album in self.photoAlbumsListModel.data:
            model = PhotoAlbumImagesTableModel(album, config)
            view = PhotoAlbumImagesTableView()
            view.setModel(model)
            view.resizeRowsToContents()
            view.resizeColumnsToContents()
            delegate = PhotoDelegate(view)
            view.setItemDelegate(delegate)
            model.dataChanged.connect(view.resizeRowsToContents)
            model.rowsInserted.connect(view.resizeColumnsToContents)
            model.rowsInserted.connect(view.resizeRowsToContents)
            model.dataChanged.connect(self.modelDataChanged)
            self.models.append(model)
            self.stacked_layout.addWidget(view)
        self.main_vertical_layout.addLayout(self.stacked_layout)

        self.cancelButton = QPushButton('cancel')
        self.cancelButton.setDisabled(True)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        self.saveButton = QPushButton('save')
        self.saveButton.setDisabled(True)
        self.saveButton.clicked.connect(self.saveButtonClicked)

        spacer = QSpacerItem(0, 50, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.save_cancel_button_layout.addItem(spacer)
        self.save_cancel_button_layout.addWidget(self.cancelButton)
        self.save_cancel_button_layout.addWidget(self.saveButton)
        self.main_vertical_layout.addLayout(self.save_cancel_button_layout)

        page_layout.addLayout(self.main_vertical_layout)

        self.models[0].init_data()

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)

    def currentAlbumChanged(self, current, previous):
        model = self.models[current.row()]
        if not model.data:
            model.init_data()

        self.stacked_layout.setCurrentIndex(current.row())
        if self.models[current.row()].unsaved_data:
            self.saveButton.setEnabled(True)
            self.cancelButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)
            self.cancelButton.setEnabled(False)

    def modelDataChanged(self):
        self.saveButton.setEnabled(True)
        self.cancelButton.setEnabled(True)

    def cancelButtonClicked(self):
        index = self.stacked_layout.currentIndex()
        model = self.models[index]
        model.cancel_unsaved_data()
        self.saveButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

    def saveButtonClicked(self):
        index = self.stacked_layout.currentIndex()
        model = self.models[index]
        model.save_unsaved_data()
        self.saveButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    config = TestConfig if args.test else Config

    app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    app.exec()