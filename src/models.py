from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QAbstractListModel
from bs4 import BeautifulSoup as soup
from uuid import uuid4

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
            trait = Character.fields[index.row()]
            self.character[trait] = value
            #trait = self.character.fields[index.row()]
            #self.character.mod_skill(trait, value) if isSkill(trait) else self.character.mod(trait, value)
        return True

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if role == Qt.ItemDataRole.DisplayRole:
            trait = Character.fields[index.row()]
            return str(self.character[trait])
        return None

    def flags(self, index):
        result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        # disable edits on the name column
        if index.row() > 0:
            result = result | Qt.ItemFlag.ItemIsEditable
        return result

class Game:

    def __init__(self, filename):
        self.filename = filename
        self.load(filename)
        self.characters = [Character(pc, i) for i, pc in enumerate(xml('pc'))]

    def load(self):
        self.metadata, self.rawdata = load(self.filename)
        self.__xml = parse(self.rawdata)

    def save(self):
        save(save_filename, self.meta_data, self.save_data)

    @property
    def save_data(self):
        return str(self.__xml.save)

    @property
    def money(self):
        return self.__xml('money')[0].string

    @money.setter
    def money(self, value):
        self.__xml('money')[0].string = str(value)

    def set_money(self, value):
        self.__xml('money')[0].string = str(value)

    @property
    def inventory(self):
        return self.__xml.save.hostInventory

    """
    @property
    def characters(self):
        return [Character(pc) for pc in xml('pc')]
    """

class Character:

    fields = [
        'displayName', 'coordination',
        'luck', 'awareness', 'strength', 'speed', 'intelligence',
        'charisma', 'availableAttributePoints', 'availableSkillPoints',
        'perkPoints', 'automatic_weapons', 'big_guns', 'brawling', 'small_arms',
        'sniper_rifles', 'animal_whisperer', 'bartering', 'nerd_stuff',
        'explosives', 'first_aid', 'leadership', 'lockpicking', 'mechanics',
        'survival', 'toaster_repair', 'weapon_modding', 'hard_ass', 'kiss_ass',
        'sneaky_shit', 'armor_modding'
    ]

    skills = { 'automatic_weapons': '10', 'big_guns': '30',
        'small_arms': '60', 'sniper_rifles': '80', 'animal_whisperer': '210',
        'bartering': '220', 'nerd_stuff': '230', 'explosives': '240',
        'first_aid': '250', 'leadership': '260', 'lockpicking': '270',
        'mechanics': '280', 'survival': '290', 'toaster_repair': '310',
        'weapon_modding': '320', 'hard_ass': '400', 'kiss_ass': '410',
        'sneaky_shit': '550', 'armor_modding': '560', 'brawling': '40'
    }

    # add perks here

    def __init__(self, xml, i):
        self.__xml = xml # selects <pc> subtree from overall <save>
        self.i = i

    @property
    def perks(self):
        return PerkModel(xml=self.__xml('perks')[0])

    def __getattr__(self, key):
        """
        if self.isSkill(key):
            adjacent = self.__xml('skillId', string=self.skills[key])
            return adjacent[0].parent('level')[0].string if len(adjacent) else None
        else:
            return self.__xml(key)[0].string if len(self.__xml(key)) else None
        """
        return self[key]

    def __getitem__(self, key):
        if self.isSkill(key):
            adjacent = self.__xml('skillId', string=self.skills[key])
            return adjacent[0].parent('level')[0].string if len(adjacent) else 'undefined'
        else:
            return self.__xml(key)[0].string if len(self.__xml(key)) else 'undefined'
            #return self.__xml(key)[0].string

    def __setattr__(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        if value:
            if key in self.fields:
                if self.isSkill(key):
                    adjacent = self.__xml('skillId', string=self.skills[key])
                    if len(adjacent):
                        adjacent[0].parent('level')[0].string = value
                    else:
                        self.new_skill(key, value)

                else:
                    self.__xml(key)[0].string = value
            else:
                self.__dict__[key] = value

    def isSkill(self, prop):
        return prop in self.skills.keys()

    def new_skill(self, skillName, level=0):
        """generates xml for a non-existing skill for this character"""
        skillId = self.skills[skillName]
        skill_xml = soup(f'<skill><skillId>{skillId}</skillId><level>{level}</level></skill>', 'lxml-xml')
        self.__xml('skills')[0].append(skill_xml('skill')[0])
        #return xml('skill')[0]


class PerkModel(QAbstractListModel):

    #fields = ['templateName', 'slot', 'ammoLoaded', 'uid', 'isLockedForMerchant',
        #'merchantBarterLevelRequirement', 'quantity']

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

        #print(f'row: {index.row()}')
        #print(self.xml)
        if role == Qt.ItemDataRole.DisplayRole:
            #[print(f"perkname: {p.perkname.string}") for p in self.xml('perk')]
            return str(self.xml('perk')[index.row()].string)
        return None

    """
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if (role == Qt.ItemDataRole.EditRole) and (value != ''):
            item = self.xml('item')[index.row()]
            field = self.fields[index.column()]
            item(field)[0].string = str(value)
            return True
        return False
    """

    def flags(self, row):
        result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        return result

    """
    def removeRow(self, row, parent=None):
        return self.removeRows(row, 1, parent)

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count)
        for i in range(row, row + count):
            item = self.xml('item')[row]
            item.decompose()
        self.endRemoveRows() # removing all items creates a bug
        return True
    """


"""
editable_traits = [
    'displayName', 'coordination', 'luck', 'awareness', 'strength', 'speed', perkPoints
    'intelligence', 'charisma', 'availableAttributePoints', 'availableSkillPoints',
]
"""

def new_item(templateName, quantity=1):
    pass

class ItemModel(QAbstractTableModel):

    fields = ['templateName', 'slot', 'ammoLoaded', 'uid', 'isLockedForMerchant',
        'merchantBarterLevelRequirement', 'quantity']

    def __init__(self, parent=None, xml=None):
        super().__init__(parent)
        self.xml = xml

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if str(orientation) == 'Orientation.Horizontal':
                return self.fields[section]
            elif str(orientation) == 'Orientation.Vertical':
                return self.xml('item')[section].templateName.string
        return None

    def rowCount(self, parent=None):
        return len(self.xml('item')) or 0

    def columnCount(self, parent=None):
        return len(self.fields)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if role == Qt.ItemDataRole.DisplayRole:
            item = self.xml('item')[index.row()]
            field = self.fields[index.column()]
            return str(item(field)[0].string)
            return 'unimplemented'
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if (role == Qt.ItemDataRole.EditRole) and (value != ''):
            item = self.xml('item')[index.row()]
            field = self.fields[index.column()]
            item(field)[0].string = str(value)
            return True
        return False

    def flags(self, index):
        result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        return result

    def removeRow(self, row, parent=None):
        return self.removeRows(row, 1, parent)

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count)
        for i in range(row, row + count):
            item = self.xml('item')[row]
            item.decompose()
        self.endRemoveRows() # removing all items creates a bug
        return True
