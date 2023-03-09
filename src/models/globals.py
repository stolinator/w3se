from bs4 import BeautifulSoup as soup
from PyQt6.QtCore import Qt, QAbstractTableModel

class Globals(QAbstractTableModel):

    def __init__(self, xml):
        super().__init__()
        # add xml tags that you want to edit to this list
        self.fields = ['money']
        self.table = {}
        for field in self.fields:
            self.table[field] = xml(field)[0]

    def __getitem__(self, key):
        return self.table[key].string

    def __setitem__(self, key, value):
        self.table[key].string = value

    """
    @property
    def money(self):
        return self.table['money'].string

    @money.setter
    def money(self, value):
        self.table['money'].string = str(value)
    """



    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if (str(orientation) == 'Orientation.Vertical'):
                return self.fields[section]
        #return self.fields

    def rowCount(self, parent=None):
        return len(self.table.values())

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            key = self.fields[index.row()]
            return str(self.table[key].string)

    def setData(self, index, value, role):
        if (role == Qt.ItemDataRole.EditRole) and (value != ''):
            key = self.fields[index.row()]
            self.table[key].string = str(value)
            return True
        return False

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

