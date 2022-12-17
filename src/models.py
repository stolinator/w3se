from PyQt6.QtCore import Qt, QAbstractTableModel
from bs4 import BeautifulSoup as soup

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
            #print(f'accessing trait {trait}')
            print(f'field: {trait}, value: {self.character[trait]}')
            return str(self.character[trait])
            #trait = self.character.fields[index.row()]
            #return str(self.character.fetch_skill(trait) if isSkill(trait) else self.character.fetch(trait))
        return None

    def flags(self, index):
        result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        # disable edits on the name column
        if index.row() > 0:
            result = result | Qt.ItemFlag.ItemIsEditable
        return result

class GameSave:

    def __init__(self, meta_data, xml):
        self.meta_data = meta_data
        self.__xml = xml
        self.characters = [Character(pc, i) for i, pc in enumerate(xml('pc'))]

    @property
    def save_data(self):
        return str(self.__xml.save)

    @property
    def money(self):
        return self.__xml('money')[0].string

    @money.setter
    def money(self, value):
        self.__xml('money')[0].string = str(value)

    @property
    def inventory(self):
        return self.__xml('hostInventory')

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
        'automatic_weapons', 'big_guns', 'brawling', 'small_arms',
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
                    #print(f'showing dict for {key}: {self[key]}')
                    if len(adjacent):
                        adjacent[0].parent('level')[0].string = value
                    else:
                        print('generating new skill!')
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


"""
editable_traits = [
    'displayName', 'coordination', 'luck', 'awareness', 'strength', 'speed',
    'intelligence', 'charisma', 'availableAttributePoints', 'availableSkillPoints',
]
"""
