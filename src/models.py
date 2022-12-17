from PyQt6.QtCore import Qt, QAbstractTableModel
from utility import isSkill


class CharacterModel(QAbstractTableModel):

    def __init__(self, parent=None, character=None):
        super().__init__(parent)
        self.character = character

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.character.fields[section]
        return None

    def rowCount(self, parent=None):
        return len(self.character.fields)

    def columnCount(self, parent=None):
        return 1

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            trait = self.character.fields[index.row()]
            self.character.mod_skill(trait, value) if isSkill(trait) else self.character.mod(trait, value)
        return True

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if role == Qt.ItemDataRole.DisplayRole:
            trait = self.character.fields[index.row()]
            return str(self.character.fetch_skill(trait) if isSkill(trait) else self.character.fetch(trait))
        return None

    def flags(self, index):
        result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        # disable edits on the name column
        if index.row() == 1:
            result = result | Qt.ItemFlag.ItemIsEditable
        return result
