import os, re, lzf
from bs4 import BeautifulSoup as soup

def load(filename: str) -> (str, soup):
    """Takes a filename as input. Seperates text metadata from compressed XML"""
    with open(filename, 'rb') as f:

        raw_data = f.readlines()

        # discover previous data size
        tgt = next(i for i,s in enumerate(raw_data) if s.decode().startswith('Data'))
        data_size = int(raw_data[tgt].strip().decode('utf-8').replace('DataSize:=', ''))

        meta_data = ''
        compressed_data = b''

        # discover beginning of compression and store meta data
        compression_start = 0
        for i, line in enumerate(raw_data):
            try:
                meta_data += line.decode('utf-8')
            except UnicodeDecodeError:
                compression_start = i
                break

        # extract compressed data
        for line in raw_data[compression_start:]:
            compressed_data += line

        # decompress
        save_data = lzf.decompress(compressed_data, data_size).decode('utf-8')

        return meta_data, save_data

def save(filename, meta_data, save_data):

    data_size = len(save_data)
    compressed_data = lzf.compress(save_data)
    save_data_size = len(compressed_data)
    meta_data = update_meta_data(meta_data, data_size, save_data_size)

    with open(filename, 'wb+') as f:
        f.write(meta_data.encode('utf-8'))
        f.write(compressed_data)
    print(f'Data Size: {data_size}, SaveDataSize: {save_data_size}')

def update_meta_data(meta_data, data_size, save_data_size):
    # find/update DataSize and SaveDataSize 
    meta_data = re.sub('\sDataSize:=\d+\s', f'\nDataSize:={data_size}\n', meta_data)
    meta_data = re.sub('\sSaveDataSize:=\d+\s', f'\nSaveDataSize:={save_data_size}\n', meta_data)
    return meta_data


def parse(data):
    """
    """
    xml = soup(data, 'lxml-xml')
    characters = xml('pc')
    return xml

class Character:

    def __init__(self, xml, i):
        self.xml = xml
        self.i = i

    def fetch(self, prop):
        if self.xml('pc')[self.i](prop):
            return self.xml('pc')[self.i](prop)[0].string
        else:
            return None

    def mod(self, prop, val):
        target = self.xml('pc')[self.i](prop)
        if target and str(val) != '':
            target[0].string = str(val)

    def fetch_skill(self, prop):
        target = self.xml('pc')[self.i]('skillId', text=skills[prop])
        #return target[0].next_sibling.string if target else None
        if target:
            target = target[0].parent('level')
            return target[0].string if target else None
        return None



    def mod_skill(self, prop, val):
        target = self.xml('pc')[self.i]('skillId', text=skills[prop])
        if target and str(val) != '':
            target.next_sibling.string = str(val)
        # non-custom PCs with zero in that skill will
        # need to have whole skill generated if it doesn't exist
        else:
            print('need to implement generation of new skills!')

    @property
    def perks(self):
        #print(self.xml('pc')[self.i])
        perks = self.xml('pc')[self.i]('perks')[0]
        return [perk('perkname')[0].string for perk in perks]



    fields = [
        'displayName', 'coordination',
        'luck', 'awareness', 'strength', 'speed', 'intelligence',
        'charisma', 'availableAttributePoints', 'availableSkillPoints',
        'automatic_weapons', 'big_guns', 'small_arms', 'sniper_rifles',
        'animal_whisperer', 'bartering', 'nerd_stuff', 'explosives',
        'first_aid', 'leadership', 'lockpicking', 'mechanics', 'survival',
        'toaster_repair', 'weapon_modding', 'hard_ass', 'kiss_ass',
        'sneaky_shit', 'armor_modding'
    ]


    displayName = property(
        fget = lambda self: self.fetch('displayName'),
        fset = lambda self, x: self.mod('displayName', x)
    )
    coordination = property(
        fget = lambda self: self.fetch('coordination'),
        fset = lambda self, x: self.mod('coordination', x)
    )
    luck = property(
        fget = lambda self: self.fetch('luck'),
        fset = lambda self, x: self.mod('luck', x)
    )
    awareness = property(
        fget = lambda self: self.fetch('awareness'),
        fset = lambda self, x: self.mod('awareness', x)
    )
    speed = property(
        fget = lambda self: self.fetch('speed'),
        fset = lambda self, x: self.mod('speed', x)
    )
    intelligence = property(
        fget = lambda self: self.fetch('intelligence'),
        fset = lambda self, x: self.mod('intelligence', x)
    )
    charisma = property(
        fget = lambda self: self.fetch('charisma'),
        fset = lambda self, x: self.mod('charisma', x)
    )
    availableAttributePoints = property(
        fget = lambda self: self.fetch('availableAttributePoints'),
        fset = lambda self, x: self.mod('availableAttributePoints', x)
    )
    availableSkillPoints = property(
        fget = lambda self: self.fetch('availableSkillPoints'),
        fset = lambda self, x: self.mod('availableSkillPoints', x)
    )
    automatic_weapons = property(
        fget = lambda self: self.fetch_skill('automatic_weapons'),
        fset = lambda self, x: self.mod_skill('automatic_weapons', x)
    )
    big_guns = property(
        fget = lambda self: self.fetch_skill('big_guns'),
        fset = lambda self, x: self.mod_skill('big_guns', x)
    )
    small_arms = property(
        fget = lambda self: self.fetch_skill('small_arms'),
        fset = lambda self, x: self.mod_skill('small_arms', x)
    )
    sniper_rifles = property(
        fget = lambda self: self.fetch_skill('sniper_rifles'),
        fset = lambda self, x: self.mod_skill('sniper_rifles', x)
    )
    animal_whisperer = property(
        fget = lambda self: self.fetch_skill('animal_whisperer'),
        fset = lambda self, x: self.mod_skill('animal_whisperer', x)
    )
    bartering = property(
        fget = lambda self: self.fetch_skill('bartering'),
        fset = lambda self, x: self.mod_skill('bartering', x)
    )
    nerd_stuff = property(
        fget = lambda self: self.fetch_skill('nerd_stuff'),
        fset = lambda self, x: self.mod_skill('nerd_stuff', x)
    )
    explosives = property(
        fget = lambda self: self.fetch_skill('explosives'),
        fset = lambda self, x: self.mod_skill('explosives', x)
    )
    first_aid = property(
        fget = lambda self: self.fetch_skill('first_aid'),
        fset = lambda self, x: self.mod_skill('first_aid', x)
    )
    leadership = property(
        fget = lambda self: self.fetch_skill('leadership'),
        fset = lambda self, x: self.mod_skill('leadership', x)
    )
    lockpicking = property(
        fget = lambda self: self.fetch_skill('lockpicking'),
        fset = lambda self, x: self.mod_skill('lockpicking', x)
    )
    mechanics = property(
        fget = lambda self: self.fetch_skill('mechanics'),
        fset = lambda self, x: self.mod_skill('mechanics', x)
    )
    survival = property(
        fget = lambda self: self.fetch_skill('survival'),
        fset = lambda self, x: self.mod_skill('survival', x)
    )
    toaster_repair = property(
        fget = lambda self: self.fetch_skill('toaster_repair'),
        fset = lambda self, x: self.mod_skill('toaster_repair', x)
    )
    weapon_modding = property(
        fget = lambda self: self.fetch_skill('weapon_modding'),
        fset = lambda self, x: self.mod_skill('weapon_modding', x)
    )
    hard_ass = property(
        fget = lambda self: self.fetch_skill('hard_ass'),
        fset = lambda self, x: self.mod_skill('hard_ass', x)
    )
    sneaky_shit = property(
        fget = lambda self: self.fetch_skill('sneaky_shit'),
        fset = lambda self, x: self.mod_skill('sneaky_shit', x)
    )
    kiss_ass = property(
        fget = lambda self: self.fetch_skill('kiss_ass'),
        fset = lambda self, x: self.mod_skill('kiss_ass', x)
    )
    armor_modding = property(
        fget = lambda self: self.fetch_skill('armor_modding'),
        fset = lambda self, x: self.mod_skill('armor_modding', x)
    )

def isSkill(prop):
    return prop in skills.keys()

skills = { 'automatic_weapons': '10', 'big_guns': '30',
    'small_arms': '60', 'sniper_rifles': '80', 'animal_whisperer': '210',
    'bartering': '220', 'nerd_stuff': '230', 'explosives': '240',
    'first_aid': '250', 'leadership': '260', 'lockpicking': '270',
    'mechanics': '280', 'survival': '290', 'toaster_repair': '310',
    'weapon_modding': '320', 'hard_ass': '400', 'kiss_ass': '410',
    'sneaky_shit': '550', 'armor_modding': '560'
}
"""
editable_traits = [
    'displayName', 'coordination', 'luck', 'awareness', 'strength', 'speed',
    'intelligence', 'charisma', 'availableAttributePoints', 'availableSkillPoints',
]
"""
