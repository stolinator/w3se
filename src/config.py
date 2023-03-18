import os, sys

def resource_path(rel_path):
    """ Generates absolute path for PyInstaller bundling """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get('_MEIPASS2', os.path.abspath('.'))

    return os.path.join(base_path, rel_path)

asset_dirname = 'assets'
items_filename = os.path.join(asset_dirname, 'export_items.txt')
perks_filename = os.path.join(asset_dirname, 'export_perks.txt')

items_filename = resource_path(items_filename)
perks_filename = resource_path(perks_filename)
