from PyQt6.QtCore import (Qt, QAbstractTableModel)
from bs4 import BeautifulSoup as soup
from models import PerkModel

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
            value = self.__xml(key)[0].string if len(self.__xml(key)) else 'undefined'
            if key == 'displayName' and value == 'undefined':
                perk_names = self.perks.currentPerks()
                return [i for i in filter(lambda s: s.startswith('BCK'), perk_names)][0].strip('BCK_')
            return value

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
