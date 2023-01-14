import pytest
# set up working directory for import statements
import os, sys
cwd = os.path.abspath(os.curdir)
sys.path.append(cwd)
sys.path.append(os.path.join(cwd, 'src'))

from bs4 import BeautifulSoup as soup
from src.utility import load, save, parse
from src.models import Character, Game, CharacterModel, ItemModel, PerkModel
from collections import namedtuple

filename = 'test_save.xml'

@pytest.fixture
def game():
    return Game(filename)

def test_game_data(game):
    assert len(game.characters) == 2
    #assert int(game.money) >= 0
    assert int(game.globals.money) >= 0
    assert game.characters[0].displayName == 'Yuri'
    assert len(game.metadata.split('\n')) == 14
    assert len(game.characters) == 2

def test_game_data_manipulation(game):
    money = game.globals.money
    new_value = str(int(money) + 10)
    assert int(money) >= 0
    assert int(new_value) > int(money)
    assert int(new_value) == int(money) + 10
    game.globals.money = new_value
    assert game.globals.money != money
    assert game.globals.money == new_value

# test for Character class
def test_character_load(game):
    yuri, spence = game.characters
    assert yuri.displayName == 'Yuri'
    assert spence.displayName == 'Spence'
    # test for specific skill values
    assert yuri.automatic_weapons == '3'
    assert yuri.weapon_modding == '2'
    assert yuri.hard_ass == '1'

    assert spence.small_arms == '1'
    assert spence.first_aid == '2'
    assert spence.brawling == '2'

    # check undefined values
    assert yuri.nerd_stuff == 'undefined'

def test_character_manipulation(game):
    yuri, spence = game.characters
    yuri.automatic_weapons = '7'
    yuri.weapon_modding = '8'
    yuri.hard_ass = '9'

    assert yuri.automatic_weapons == '7'
    assert yuri.weapon_modding == '8'
    assert yuri.hard_ass == '9'

    # writing to undefined values
    assert yuri.nerd_stuff == 'undefined'
    """
    with pytest.raises(IndexError):
        yuri.nerdstuff
    """
    yuri.nerd_stuff = '1'
    assert yuri.nerd_stuff == '1'

def test_manipulation_persists(game):
    new_savefile = f'new_{filename}'

    # make an edit and save to new file
    yuri, spence = game.characters
    yuri.bartering = '10'
    game.save(new_savefile)

    # load new file and check for changes
    metadata, savedata = load(new_savefile)
    xml = parse(savedata)
    new_yuri = Character(xml, 0)
    assert new_yuri.bartering == '10'
    yuri_xml = xml('pc')[0]
    new_yuri_skill_count = len(yuri_xml('skills')[0])
    assert new_yuri_skill_count == 4
    for skillId in '10', '220', '400', '320':
        assert skillId in [skill.skillId.string for skill in yuri_xml('skills')[0]('skill')]

def test_perks():
    yuri, spence = parse(load('test_save.xml')[1])('pc')
    assert 'BCK_Yuri' in [p.string for p in yuri('perkname')]
    assert 'BCK_Spence' in [p.string for p in spence('perkname')]


def test_perks_removal(game):
    yuri = game.characters[0]

# test adding new perks and saving

# test inventory
# test removing from inventory
# test adding new items and saving (check qty after re-load)
