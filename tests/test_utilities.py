import pytest
# set up working directory for import statements
import os, sys
cwd = os.path.abspath(os.curdir)
sys.path.append(cwd)

from bs4 import BeautifulSoup as soup
from src.utility import load, save, parse, Character

filename = 'test_save.xml'

def test_load():

    # these test look implementation specific, should
    # create better player API and make tests more general

    meta_data, save_data = load(filename)
    assert type(meta_data) == str
    assert type(save_data) == str
    assert len(meta_data.split('\n')) == 14



@pytest.fixture
def meta_data_and_save_data():
    return load(filename)

def test_parse(meta_data_and_save_data):

    meta_data, save_data = meta_data_and_save_data

    xml = parse(save_data)
    assert type(xml) == soup
    assert len(xml('pc')) == 2

@pytest.fixture
def xml(meta_and_save_data):
    return parse(meta_and_save_data[1])

def test_game_data(xml):
    game = GameData(xml)
    assert len(game.characters) == 2
    assert int(game.money) > 0
    assert game.characters[0].name == 'yuri'
