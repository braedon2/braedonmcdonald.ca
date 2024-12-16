import sys
import sqlite3 

import config
from photo_album.photo_album_db import (
    Album, Photo, PhotoAlbumDb
)

from PyQt6 import QtGui
from PyQt6.QtCore import (
    QAbstractListModel, 
    QAbstractTableModel,
    QItemSelection,
    QItemSelectionModel, 
    QModelIndex,
    QSize,
    Qt
)
from PyQt6.QtWidgets import (
    QApplication, 
    QHBoxLayout,
    QListView, 
    QMainWindow, 
    QPushButton,
    QSizePolicy,
    QSpacerItem, 
    QStackedLayout,
    QTableView,
    QVBoxLayout,
    QWidget
)

class PhotoAlbumsListModel(QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = PhotoAlbumDb(config.photo_album_db_path)
        self._data: list[Album] = self.db.get_albums()
        self._data.sort(reverse=True)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> str|QSize|None:
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()].dirname
        if role == Qt.ItemDataRole.SizeHintRole:
            return QSize(175, 50)
        
    def rowCount(self, index: QModelIndex) -> int:
        return len(self._data)

class PhotoAlbumsListView(QListView):
    pass

class PhotoAlbumTableModel(QAbstractTableModel):
    def __init__(self, *args, album_id, **kwargs):
        super().__init__(*args, **kwargs)
        self.album_id = album_id

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.album_id
        
    def rowCount(self, index: QModelIndex) -> int:
        return 1
    
    def columnCount(self, index):
        return 1

class PhotoAlbumTableView(QTableView):
    pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Photo Album Editor")
        self.setMinimumWidth(600)
        self.setMinimumHeight(300)

        page_layout = QHBoxLayout()
        main_vertical_layout = QVBoxLayout()
        self.stacked_layout = QStackedLayout()
        save_cancel_button_layout = QHBoxLayout()

        self.photoAlbumsListView = PhotoAlbumsListView()
        self.photoAlbumsListModel = PhotoAlbumsListModel()
        self.photoAlbumsListView.setModel(self.photoAlbumsListModel)
        self.photoAlbumsListView.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        page_layout.addWidget(self.photoAlbumsListView)
        ix = self.photoAlbumsListModel.index(0, 0)
        self.photoAlbumsListView.selectionModel().setCurrentIndex(ix, QItemSelectionModel.SelectionFlag.Select)
        self.photoAlbumsListView.selectionModel().currentChanged.connect(self.currentAlbumChanged)

        for album in self.photoAlbumsListModel._data:
            model = PhotoAlbumTableModel(album_id=album.rowid)
            view = PhotoAlbumTableView()
            view.setModel(model)
            view.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            )
            self.stacked_layout.addWidget(view)
        page_layout.addLayout(self.stacked_layout)

        spacer = QSpacerItem(0, 50, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.cancelButton = QPushButton('cancel')
        self.cancelButton.setDisabled(True)
        self.saveButton = QPushButton('save')
        self.saveButton.setDisabled(True)
        save_cancel_button_layout.addItem(spacer)
        save_cancel_button_layout.addWidget(self.cancelButton)
        save_cancel_button_layout.addWidget(self.saveButton)
        main_vertical_layout.addLayout(save_cancel_button_layout)

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)

    def currentAlbumChanged(self, current, previous):
        self.stacked_layout.setCurrentIndex(current.row())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()