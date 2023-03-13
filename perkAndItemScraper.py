#!/usr/bin/env python
import sys, os, subprocess
sys.path.append('src')
from src.models import Game

#filename = 'Autosave1.xml'



if len(sys.argv) > 1:

    cmd = subprocess.run(f"find {sys.argv[1]} | grep -P 'xml$'", shell=True, capture_output=True)
    files = cmd.stdout.decode().split('\n')

    with open('export_items.txt') as f:
        items = set([s.strip('\n') for s in f.readlines()])

    with open('export_perks.txt') as f:
        perks = set([s.strip('\n') for s in f.readlines()])

    for filename in files:
        if filename == '':
            continue

        game = Game(filename)

        new_items = set([i.string for i in game.inventory('templateName')])
        items = items.union(new_items)

        new_perks = set()
        for character in game.characters:
            new_perks = new_perks.union( [p.string for p in character.perks.xml('perkname')] )
        perks = perks.union(new_perks)

    with open('export_items.txt', 'w') as f:
        for i in items:
            f.write(f'{i}\n')

    with open('export_perks.txt', 'w') as f:
        for p in perks:
            f.write(f'{p}\n')

else:
    print()
    print("perkAndItemScraper.py")
    print("----- Description-----")
    print("This recursively parses a directory and looks for new perks")
    print("and items contained in existing game saves. You can use this")
    print("to expand editing options with the w3se editor")
    print()
    print("----- Options -----")
    print("Usage: perkAndItemScraper <directory>")
    print("Arguments:")
    print("<directory>\tthe directory containing your game saves")
    print()
