from PyQt6.QtCore import (Qt, QAbstractTableModel, QModelIndex, QAbstractListModel)
    #)#, QMimeData, QByteArray, QDataStream)
from bs4 import BeautifulSoup as soup
from uuid import uuid4
from utility import load, save, parse
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
        return len(self.xml('perk')) or 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if role == Qt.ItemDataRole.DisplayRole:
            return str(self.xml('perk')[index.row()].string)
        return None

    def dropMimeData(self, data, action ,row, column, parent):
        def decode_data(ba):
            data = []
            item = {}
            ds = QDataStream(ba)
            while not ds.atEnd():
                row = ds.readInt32()
                column = ds.readInt32()

                map_items = ds.readInt32()
                for i in range(map_items):
                    key = ds.readInt32()
                    value = QVariant()
                    ds >> value
                    item[Qt.ItemDataRole(key)] = value
                data.append(item)
            return data
        if data.hasFormat('application/x-qabstractitemmodeldatalist'):
            ba = data.data('application/x-qabstractitemmodeldatalist')
            data_items = decode_data(ba)
            text = data_items[0][Qt.ItemDataRole.DisplayRole]
            print(text.value())
            self.insertRows(self.rowCount(), 1, None, text.value())
        return True


    def flags(self, row):
        #result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
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

