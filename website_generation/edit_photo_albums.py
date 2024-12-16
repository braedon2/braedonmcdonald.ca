from PyQt6.QtWidgets import QApplication, QTableView
from PyQt6.QtCore import Qt, QMimeData, QAbstractTableModel, QByteArray, QBuffer, QIODevice, QFile
from PyQt6.QtGui import QPixmap, QImage, QDrag

class ImageTableModel(QAbstractTableModel):
    def __init__(self, images):
        super().__init__()
        self._images = images  # 2D list of QPixmap objects

    def rowCount(self, parent=None):
        return len(self._images)

    def columnCount(self, parent=None):
        return len(self._images[0]) if self._images else 0

    def data(self, index, role):
        if role == Qt.ItemDataRole.DecorationRole:
            row, col = index.row(), index.column()
            return self._images[row][col]
        return None

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled
        )

    def mimeData(self, indexes):
        mime_data = super().mimeData(indexes)
        if indexes:
            index = indexes[0]
            row, col = index.row(), index.column()
            pixmap: QPixmap = self._images[row][col]
            # Serialize QPixmap as QByteArray
            ba = QByteArray()
            buff = QBuffer(ba)
            pixmap.save(buff, "JPG")
            byte_array = ba.data()
            mime_data.setData("application/x-pixmap", byte_array)
            mime_data.setText(f"{row},{col}")
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        if not data.hasFormat("application/x-pixmap"):
            return False
        source_row, source_col = map(int, data.text().split(","))
        pixmap = QPixmap()
        pixmap.loadFromData(data.data("application/x-pixmap"))

        # Swap images
        self._images[source_row][source_col], self._images[parent.row()][parent.column()] = \
            self._images[parent.row()][parent.column()], self._images[source_row][source_col]

        # Notify view of data changes
        self.dataChanged.emit(self.index(row, column), self.index(source_row, source_col))
        return True

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

class ImageTableView(QTableView):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

if __name__ == '__main__':
    app = QApplication([])

    # Create example images
    pixmap1 = QPixmap(100, 100)
    pixmap1.fill(Qt.GlobalColor.red)
    pixmap2 = QPixmap(100, 100)
    pixmap2.fill(Qt.GlobalColor.green)
    pixmap3 = QPixmap(100, 100)
    pixmap3.fill(Qt.GlobalColor.blue)
    pixmap4 = QPixmap(100, 100)
    pixmap4.fill(Qt.GlobalColor.yellow)

    images = [
        [pixmap1, pixmap2],
        [pixmap3, pixmap4],
    ]

    # Create model and view
    model = ImageTableModel(images)
    table = ImageTableView()
    table.setModel(model)

    # Adjust row and column sizes
    table.horizontalHeader().setDefaultSectionSize(100)
    table.verticalHeader().setDefaultSectionSize(100)

    table.show()
    app.exec()