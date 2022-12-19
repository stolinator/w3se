import pytest
# set up working directory for import statements
import os, sys
cwd = os.path.abspath(os.curdir)
sys.path.append(cwd)

from bs4 import BeautifulSoup as soup
from src.utility import load, save, parse
from src.models import Character, GameSave, CharacterModel, ItemModel, PerkModel
from collections import namedtuple

filename = 'test_save.xml'

@pytest.fixture
def gamesave():
    md, sd = load(filename)
    xml = parse(sd)
    return GameSave(md, xml)

def test_game_data():
    md, sd = load(filename)
    xml = parse(sd)
    game = GameSave(md, xml)
    assert len(game.characters) == 2
    assert int(game.money) >= 0
    assert game.characters[0].displayName == 'Yuri'
    assert len(game.meta_data.split('\n')) == 14
    assert len(game.characters) == 2

def test_game_data_manipulation(gamesave):
    money = gamesave.money
    new_value = str(int(money) + 10)
    assert int(money) >= 0
    gamesave.money = new_value
    assert gamesave.money != money
    assert gamesave.money == new_value

# test for Character class
def test_character_load(gamesave):
    yuri, spence = gamesave.characters
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

def test_character_manipulation(gamesave):
    yuri, spence = gamesave.characters
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

def test_manipulation_persists(gamesave):
    new_savefile = f'new_{filename}'

    # make an edit and save to new file
    yuri, spence = gamesave.characters
    yuri.bartering = '10'
    save(new_savefile, gamesave.meta_data, gamesave.save_data)

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
    #yuri = gamesave.characters[0]
    #assert 'BCK_Yuri' in [p.string for p in yuri.perks('perkname')]
    assert 'BCK_Yuri' in [p.string for p in yuri('perkname')]
    assert 'BCK_Spence' in [p.string for p in spence('perkname')]


def test_perks_removal(gamesave):
    yuri = gamesave.characters[0]

# test adding new perks and saving

# test inventory
# test removing from inventory
# test adding new items and saving (check qty after re-load)
