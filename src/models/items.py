from PyQt6.QtCore import (Qt, QAbstractTableModel, QModelIndex)
from bs4 import BeautifulSoup as soup
from uuid import uuid4
from PyQt6.QtCore import (QDataStream, QVariant)


class ItemModel(QAbstractTableModel):

    fields = ['templateName', 'quantity']#, 'uid']

    def __init__(self, parent=None, xml=None):
        super().__init__(parent)
        self.xml = xml
        self.items = xml('item')

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if str(orientation) == 'Orientation.Horizontal':
                return self.fields[section]
            elif str(orientation) == 'Orientation.Vertical' and section < self.rowCount():
                return self.items[section].templateName.string
        return None

    def rowCount(self, parent=None):
        return len(self.items)

    def columnCount(self, parent=None):
        return len(self.fields)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            item = self.items[index.row()]
            field = self.fields[index.column()]
            try:
                return str(item(field)[0].string)
            except IndexError:
                return 'undefined'

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if (role == Qt.ItemDataRole.EditRole) and (value != ''):
            item = self.items[index.row()]
            field = self.fields[index.column()]
            item(field)[0].string = str(value)
            return True
        return False

    def flags(self, index):
        result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | \
            Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        if index.column() == self.fields.index('quantity'):
            result = result | Qt.ItemFlag.ItemIsEditable
        return result

    def removeRow(self, row, parent=None):
        return self.removeRows(row, 1, parent)

    def removeRowsFromList(self, rows):
        [self.items[row].decompose() for row in rows]
        self.layoutChanged.emit()
        self.items = self.xml('item')

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count)
        for i in range(count):
            item = self.items[row]
            item.decompose()
        self.endRemoveRows()
        self.layoutChanged.emit()
        self.items = self.xml('item')
        return True

    def currentItems(self):
        #return [tag.string for tag in self.xml('templateName')]
        return [tag.templateName.string for tag in self.items]

    def insertRows(self, position, rows, value):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            if value not in self.currentItems():
                tag = soup(f'<item><templateName>{value}</templateName><slot>0</slot><quantity>1</quantity><uid>{str(uuid4())}</uid></item>', 'lxml-xml')
                self.xml.append(tag.item)
        self.endInsertRows()
        self.items = self.xml('item')
        self.layoutChanged.emit()

    def decode_data(self, ba):
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

    def dropMimeData(self, data, action ,row, column, parent):
        if data.hasFormat('application/x-qabstractitemmodeldatalist'):
            ba = data.data('application/x-qabstractitemmodeldatalist')
            data_items = self.decode_data(ba) # list of objects containing Qt objects
            inventory = self.currentItems()
            for data_item in data_items:
                value = data_item[Qt.ItemDataRole.DisplayRole].value()
                if value not in inventory:
                    tag = soup(f'<item><templateName>{value}</templateName><slot>0</slot><quantity>1</quantity><uid>{str(uuid4())}</uid></item>', 'lxml-xml')
                    self.xml.append(tag.item)
            self.items = self.xml('item')
            self.layoutChanged.emit()
        return True
