from utility import load, save, parse
from models import Character, Globals


class Game:
    """Class representing a save game file. It manages interactions with the
    file system and maninpulating character, inventory, and save data.
    `filename` is a string containing the absolute path to a save file.

    >>> filename = '/path/to/my/save.xml'
    >>> game = Game(filename)
    >>> print(game)
    <Game savefile: /path/to/my/save>
    
    select a character
    >>> pc = game.characters[0]

    save any changes made to characters, inventory, or globals
    >>> filename = '/path/to/my/new_save.xml'
    >>> game.save(filename)
    
    """

    def __str__(self):
        return f"<Game savefile: '{self.filename}'>"

    def __repr__(self):
        return f"Game({self.filename})"

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
    def globals(self):
        return Globals(self.__xml)

    """
    @property
    def money(self):
        return self.__xml('money')[0].string

    @money.setter
    def money(self, value):
        self.__xml('money')[0].string = str(value)

    def set_money(self, value):
        self.__xml('money')[0].string = str(value)
    """

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

