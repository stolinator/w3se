#!/usr/bin/env python

import click
from src.utility import load, parse

#filename = 'new_test_save.xml'
filename = 'Autosave1.xml'

md, sd = load(filename)
xml = parse(sd)

with open('output1.xml', 'w') as f:
    f.write(xml.prettify())
