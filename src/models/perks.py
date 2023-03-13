from PyQt6.QtCore import Qt, QModelIndex, QAbstractListModel
from bs4 import BeautifulSoup as soup
from PyQt6.QtCore import (QDataStream, QIODevice, QVariant)


class PerkModel(QAbstractListModel):

    def __init__(self, parent=None, xml=None):
        super().__init__(parent)
        self.xml = xml

    def headerData(self, section, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return 'perkname'
        return None

    def rowCount(self, parent=None):
        print(f"row count: {len(self.xml('perk'))}")
        return len(self.xml('perk')) or 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if role == Qt.ItemDataRole.DisplayRole and index.row() < self.rowCount():
            print(f"looking for {index.row()}")
            return str(self.xml('perk')[index.row()].string)
        return None

    def dropMimeData(self, data, action ,row, column, parent):
        def decode_data(ba):
            data = []
            ds = QDataStream(ba)
            while not ds.atEnd():
                row = ds.readInt32()
                column = ds.readInt32()

                map_items = ds.readInt32()
                for i in range(map_items):
                    item = {}
                    key = ds.readInt32()
                    value = QVariant()
                    ds >> value
                    item[Qt.ItemDataRole(key)] = value
                data.append(item)
            return data
        if data.hasFormat('application/x-qabstractitemmodeldatalist'):
            ba = data.data('application/x-qabstractitemmodeldatalist')
            d = decode_data(ba)
            for data_items in d:
                text = data_items[Qt.ItemDataRole.DisplayRole]
                self.insertRows(self.rowCount(), 1, None, text.value())
        return True


    def flags(self, row):
        result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        result = result | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        return result

    def currentPerks(self):
        return [tag.string for tag in self.xml('perkname')]

    def insertRows(self, position, rows, parent, value):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            if value not in self.currentPerks():
                self.xml.append(soup(f'<perk><perkname>{value}</perkname></perk>', 'lxml-xml').perk)
        self.endInsertRows()
        self.layoutChanged.emit()

    def removeRow(self, row, parent=None):
        return self.removeRows(row, 1, parent)

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count)
        print(f"all there is: {self.xml('perk')}")
        for i in range(count):
            print(f"removing! {self.xml('perk')[row]} at {row}")
            item = self.xml('perk')[row]
            item.decompose()
        self.endRemoveRows()
        self.layoutChanged.emit()
        return True



