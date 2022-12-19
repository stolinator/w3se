from PyQt6.QtCore import (Qt, QAbstractTableModel, QModelIndex, QAbstractListModel)
    #)#, QMimeData, QByteArray, QDataStream)
from bs4 import BeautifulSoup as soup
from uuid import uuid4
from utility import load, save, parse
from PyQt6.QtCore import (QDataStream, QIODevice, QVariant)

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
        self.load()

    def load(self):
        self.metadata, self.rawdata = load(self.filename)
        self.__xml = parse(self.rawdata)
        self.characters = [Character(pc, i) for i, pc in enumerate(self.__xml('pc'))]

    def save(self, save_filename):
        save(save_filename, self.metadata, self.save_data)

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

    def export_items_and_perks(self):
        perks = set([tag.string for tag in self.__xml('perkname')])
        items = set(sorted([tag.string for tag in self.__xml('templateName')]))
        perks = sorted(list(perks))
        items = sorted(list(items))
        with open('export_perks.txt', 'w') as f:
            f.write('\n'.join(perks))
        with open('export_items.txt', 'w') as f:
            f.write('\n'.join(items))


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

    """
    def mimeTypes(self):
        #mime_data = QMimeData()
        #encoded_data = QByteArray()
        #stream = QDataStream(encoded_data
        #return ['application/vnd.text.list']
        return super().mimeTypes()

    def canDropMimeData(self, data, action, row, column, parent):
        return True
    """
    def dropMimeData(self, data, action ,row, column, parent):
        """
        print(f'data: {data}, action: {action}, row:column: {row}:column{column}, parent: {parent}')
        print(f'\n\ndata:\t{data.text()}\n')
        print(f'vars: {vars(data)}\n\ndir: {dir(data)}')
        print(f'data html?: {data.html()}') 

        #print(f'data retrieve?: {data.retrieveData()}') 
        #print(f'data sender?: {data.sender()}') 

        #print(f'data mimeData?: {data.mimeData()}') # data is of type QMimeData
        print(f'formats: {data.formats()}')
        # >>> formats: ['application/x-qabstractitemmodeldatalist']
        """

        #stream = QDataStream(encoded_data, QIODevice.ReadOnly)
        #encoded_data = data.data('application/vnd.text.list')
        #encoded_data = data.data('application/x-qabstractitemmodeldatalist')
        #stream = QDataStream(encoded_data)
        #new_items = []
        #help(stream)
        # readString, readBytes
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
            """
            print(vars(text))
            print()
            print(dir(text))
            print(text)
            """
            print(text.value())
            self.insertRows(self.rowCount(), 1, None, text.value())
        return True

        """
        while not stream.atEnd():
            #new_items.append(stream.readQString())
            print(stream.readQString())
            #print(stream.readString())
            #print(stream.readBytes())
        #print(f'new items: {new_items}')
        return True
        """
        """
        if data.hasFormat('application/x-qabstractitemmodeldatalist'):
            ba = data.data('application/x-qabstractitemmodeldatalist')
            #data_items = self.decodeData(ba)
            #print(data_items)
            print(ba.size())
            #print(ba.fromBase64())
            #print(ba.toStdString())
            #print(ba.readAll())
        return True
        """

    """
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if (role == Qt.ItemDataRole.EditRole) and (value != ''):
            item = self.xml('item')[index.row()]
            field = self.fields[index.triolumn()]
            item(field)[0].string = str(value)
            return True
        return False
    """

    def flags(self, row):
        #result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        result = result | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
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

    def currentPerks(self):
        return [tag.string for tag in self.xml('perkname')]

    def insertRows(self, position, rows, parent, value):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            if value not in self.currentPerks():
                #self.xml('perks')[0].append(f'<perk><perkname>{value}</perkname></perk>')
                self.xml.append(soup(f'<perk><perkname>{value}</perkname></perk>', 'lxml-xml').perk)
        self.endInsertRows()
        self.layoutChanged.emit()



class ItemModel(QAbstractTableModel):

    fields = ['templateName', 'slot', 'ammoLoaded', 'uid', 'isLockedForMerchant',
        'merchantBarterLevelRequirement', 'quantity']

    def __init__(self, parent=None, xml=None):
        super().__init__(parent)
        self.xml = xml
        #self.rowsAboutToBeRemoved.connect

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if str(orientation) == 'Orientation.Horizontal':
                return self.fields[section]
            elif str(orientation) == 'Orientation.Vertical' and section < self.rowCount():
                return self.xml('item')[section].templateName.string
        return None

    def rowCount(self, parent=None):
        return len(self.xml('item'))

    def columnCount(self, parent=None):
        return len(self.fields)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):

        if role == Qt.ItemDataRole.DisplayRole:
            item = self.xml('item')[index.row()]
            field = self.fields[index.column()]
            try:
                return str(item(field)[0].string)
            except IndexError:
                return 'undefined'
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if (role == Qt.ItemDataRole.EditRole) and (value != ''):
            item = self.xml('item')[index.row()]
            field = self.fields[index.column()]
            item(field)[0].string = str(value)
            return True
        return False

    def flags(self, index):
        #result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        result = result | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        if index.column() == 6:
            result = result | Qt.ItemFlag.ItemIsEditable
        return result

    def removeRow(self, row, parent=None):
        return self.removeRows(row, 1, parent)

    def removeRows(self, row, count, parent):
        self.beginRemoveRows(parent, row, row + count)
        for i in range(row, row + count):
            item = self.xml('item')[row]
            item.decompose()
        self.endRemoveRows() # removing all items creates a bug
        self.layoutChanged.emit()
        return True

    def currentItems(self):
        return [tag.string for tag in self.xml('templateName')]

    def insertRows(self, position, rows, value):
        print(f'debug:\tpos: {position}, rows: {rows}, values: {value}')
        """
          <item>
		   <templateName>
			Ammo762mm
		   </templateName>
		   <slot>
			0
		   </slot>
		   <ammoLoaded>
			0
		   </ammoLoaded>
		   <quantity>
			67
		   </quantity>
		   <uid>
			4c00a43f-c0bd-4517-adaf-de986999721a
		   </uid>
		   <isLockedForMerchant>
			False
		   </isLockedForMerchant>
		   <merchantBarterLevelRequirement>
			0
		   </merchantBarterLevelRequirement>
		  </item>
        """
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            if value not in self.currentItems():
                #self.xml('perks')[0].append(f'<perk><perkname>{value}</perkname></perk>')
                tag = soup(f'<item><templateName>{value}</templateName><slot>0</slot><quantity>1</quantity><uid>{str(uuid4())}</uid></item>', 'lxml-xml')
                print(f'tag: {tag}')
                print(f'{tag.item}')
                self.xml.append(tag.item)
        self.endInsertRows()
        self.layoutChanged.emit()

    def dropMimeData(self, data, action ,row, column, parent):
        print('data drop!')
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
            print(data.formats())
            ba = data.data('application/x-qabstractitemmodeldatalist')
            data_items = decode_data(ba)
            text = data_items[0][Qt.ItemDataRole.DisplayRole]
            print(text.value())
            self.insertRows(self.rowCount(), 1, text.value())
        else:
            print(data.formats())
        return True
