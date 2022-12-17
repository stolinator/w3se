import pytest
# set up working directory for import statements
import os, sys
cwd = os.path.abspath(os.curdir)
sys.path.append(cwd)

from bs4 import BeautifulSoup as soup
from src.utility import load, save, parse
from src.models import Character, GameSave

filename = 'test_save.xml'

def test_load():

    # these test look implementation specific, should
    # create better player API and make tests more general

    meta_data, save_data = load(filename)
    assert type(meta_data) == str
    assert type(save_data) == str
    assert len(meta_data.split('\n')) == 14



@pytest.fixture
def metadata_and_savedata():
    return load(filename)

@pytest.fixture
def xml(metadata_and_savedata):
    return parse(metadata_and_savedata[1])

def test_parse(metadata_and_savedata):

    meta_data, save_data = metadata_and_savedata

    xml = parse(save_data)
    assert type(xml) == soup
    assert len(xml('pc')) == 2

