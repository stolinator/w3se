import sys, os, shutil
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QTabWidget,
    QLabel, QPushButton, QMenuBar, QVBoxLayout, QHBoxLayout,
    QFileDialog, QTableView, QMessageBox, QListView, QLineEdit,
    QListWidget, QButtonGroup, QRadioButton, QHeaderView,
    QAbstractItemView, QMessageBox, QLineEdit)
from PyQt6.QtGui import QPixmap, QFont, QAction
from models import CharacterModel, Game, ItemModel, PerkModel
from config import items_filename, perks_filename


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.createActions()
        self.createMenu()
        self.setAcceptDrops(True)
        self.waiting_label = QLabel('Drag and drop a save file or use the file menu to get started...')
        self.waiting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.waiting_label)
        self.show()
        with open(items_filename) as f:
            self.all_items = [s.strip('\n') for s in f.readlines()]

    def initUI(self):
        self.setGeometry(200, 100, 720, 480)
        self.setWindowTitle('Wasteland 3 Save Editor')


    def createGlobalEditor(self):
        editor = QWidget()
        vbox = QVBoxLayout()
        editor.setLayout(vbox)
        vbox.addWidget(QLabel('Edit global values'))
        value_table = QTableView()
        value_table.horizontalHeader().hide()
        value_table.setModel(self.game.globals)
        vbox.addWidget(value_table)
        return editor

    def createInventoryEditor(self):
        editor = QWidget()
        vbox = QVBoxLayout()
        editor.setLayout(vbox)
        item_view = QTableView()
        item_view.setAcceptDrops(True)
        item_view.showDropIndicator()
        model = ItemModel(xml = self.game.inventory)
        item_view.setModel(model)
        header = item_view.horizontalHeader()
        """
        for i,f in enumerate(model.fields):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch if i == 0 else QHeaderView.ResizeMode.ResizeToContents)
        """
        for i, f in enumerate(model.fields):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        # filters
        itemfilters_hbox = QHBoxLayout()
        itemfilters_hbox.addWidget(QLabel('Filters:'))
        itemfilters_group = QButtonGroup()
        filter_types = {'Consumables': 'ITM_Consumable', 'Armor Mods': 'ITM_ArmorMod',
                        'Armor': 'ITM_Equip_Armor', 'Weapon Mods': 'ITM_WeaponMod',
                        'Weapons': 'ITM_Equip_Weapon', 'Ammo': 'Ammo',
                        'Crafting': 'ITM_Crafting', 'Trinkets': 'ITM_Equip_Trinket',
                        'Cyborg': 'ITM_Equip_Cyborg', 'Clear Filters': ''
                        }
        vbox.addLayout(itemfilters_hbox)
        # search box
        def search_items(substr):
            substr = substr.lower()
            for i in range(model.rowCount()):
                if model.data(model.index(i, 0)).lower().find(substr) != -1:
                    item_view.setRowHidden(i, False)
                else:
                    item_view.setRowHidden(i, True)
        itemsearch_hbox = QHBoxLayout()
        itemsearch_label = QLabel('Search')
        itemsearch = QLineEdit()
        #itemsearch.changeEvent.connect(lambda ev: print('textbox change'))
        itemsearch.textChanged.connect(lambda: search_items(itemsearch.text()))
        itemsearch_hbox.addWidget(itemsearch_label)
        itemsearch_hbox.addWidget(itemsearch)
        vbox.addLayout(itemsearch_hbox)

        def filter_items(text):
            #help(model)
            [item_view.setRowHidden(i, not (model.data(model.index(i, 0)).startswith(filter_types[text]) or (text == 'Clear Filters'))) for i in range(model.rowCount())]
            """
            for i in range(model.rowCount()):

                if model.data(model.index(i, 0)).startswith(filter_types[text]) or text == 'Clear Filters':
                    item_view.setRowHidden(i, False)
                else:
                    item_view.setRowHidden(i, True)
            """

        for i in filter_types.keys():
            rbtn = QRadioButton(i)
            # shouldn't use IIFE here, it's messy
            (lambda text: rbtn.clicked.connect(lambda: filter_items(text)))(i)
            itemfilters_group.addButton(rbtn)
            itemfilters_hbox.addWidget(rbtn)

        vbox.addWidget(item_view)
        hbox = QHBoxLayout()
        btn_add = QPushButton('Show all in-game items')
        btn_add.clicked.connect(self.showItems)
        btn_remove = QPushButton('Remove selected items')
        btn_remove.clicked.connect(
            #lambda: [model.removeRow(i.row(), i) for i in sorted(item_view.selectedIndexes(), reverse=True)]
            #lambda: [model.(i.row(), i) for i in sorted(item_view.selectedIndexes(), reverse=True)]
            lambda: model.removeRowsFromList(sorted([i.row() for i in item_view.selectedIndexes()], reverse=True))
        )
        hbox.addWidget(btn_add)
        hbox.addWidget(btn_remove)
        vbox.addLayout(hbox)
        return editor

    def createCharacterEditor(self):
        filter_types = {'Quirks': 'QRK', 'Perks': 'PRK', 'Backgrounds': 'BCK', 'Clear': 'Clear' }
        def search_perks(text, view):
            print(text)
            text = text.lower()
            model = view.model()
            rows = model.rowCount()
            for i in range(rows):
                if model.data(model.index(i, 0)).lower().find(text) != -1:
                    view.setRowHidden(i, False)
                else:
                    view.setRowHidden(i, True)
        def filter_perks(text, view):
            model = view.model()
            for i in range(model.rowCount()):
                if model.data(model.index(i, 0)).startswith(filter_types[text]) or text == 'Clear Filter':
                    view.setRowHidden(i, False)
                else:
                    view.setRowHidden(i, True)
        editor = QWidget()
        editor_vbox = QVBoxLayout()
        tabs = QTabWidget()
        for character in self.game.characters:
            model = CharacterModel(character=character)
            skilltable = QTableView()
            skilltable.setModel(model)
            skilltable.horizontalHeader().hide()
            perklist = QListView()
            perklist.setAcceptDrops(True)
            perklist.showDropIndicator()
            perklist.setModel(character.perks)
            perklist.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
            perkfilters_hbox = QHBoxLayout()
            perkfilters_group = QButtonGroup()


            perk_search_hbox = QHBoxLayout()
            perk_search = QLineEdit()
            perk_search_label = QLabel('Search')
            (lambda ps, view: ps.textChanged.connect(lambda: search_perks(ps.text(), view)))(perk_search, perklist)
            perk_search_hbox.addWidget(perk_search_label)
            perk_search_hbox.addWidget(perk_search)

            name = character.displayName
            character_page = QWidget()
            vbox = QVBoxLayout()
            hbox = QHBoxLayout()
            hbox_vbox = QVBoxLayout()
            vbox.addLayout(hbox)
            hbox.addWidget(skilltable)
            hbox.addLayout(hbox_vbox)
            hbox_vbox.addWidget(QLabel(f"Edit {name}'s Perks"))
            hbox_vbox.addWidget(perklist)

            hbox_vbox.addLayout(perkfilters_hbox)
            hbox_vbox.addLayout(perk_search_hbox)

            btn_show_perks = QPushButton('Show all perks')
            btn_show_perks.clicked.connect(self.showPerks)
            btn_remove_perks = QPushButton('Remove selected perks')

            for i in filter_types.keys():
                rbtn = QRadioButton(i)
                # shouldn't use IIFE here, it's messy
                (lambda text, view: rbtn.clicked.connect(lambda: filter_perks(text, view)))(i, perklist)
                perkfilters_group.addButton(rbtn)
                perkfilters_hbox.addWidget(rbtn)

            def remove_selected(current_perklist, model):
                get_rid = {}
                [get_rid.setdefault(i.row(), i) for i in current_perklist.selectedIndexes()]
                [model.removeRow(i, get_rid[i]) for i in sorted(get_rid.keys(), reverse=True)]

            btn_remove_perks.clicked.connect((lambda pl, model: lambda: remove_selected(pl, model))(perklist, character.perks))
            perk_btns_box = QHBoxLayout()
            perk_btns_box.addWidget(btn_show_perks)
            perk_btns_box.addWidget(btn_remove_perks)
            hbox_vbox.addLayout(perk_btns_box)
            character_page.setLayout(vbox)
            tabs.addTab(character_page, name)
        editor_vbox.addWidget(tabs)
        editor.setLayout(editor_vbox)
        return editor

    def setUpWindow(self):
        assert self.game is not None
        assert self.game.metadata is not None
        #assert self.game.bug is True
        main_widget = QTabWidget()
        tab_functions = {
            'Edit Characters': self.createCharacterEditor,
            'Edit Inventory': self.createInventoryEditor,
            'Edit Global Values': self.createGlobalEditor
        }
        for label, func in tab_functions.items():
            main_widget.addTab(func(), label)
        self.setCentralWidget(main_widget)
        self.waiting_label = None

    def createActions(self):

        self.load_file_act = QAction('Load Save Game')
        self.load_file_act.triggered.connect(self.loadFile)

        self.save_changes_act = QAction('&Save Changes')
        self.save_changes_act.setShortcut('Ctrl+S')
        self.save_changes_act.setDisabled(True)
        self.save_changes_act.triggered.connect(self.saveFile)

        self.quit_act = QAction('&Quit')
        self.quit_act.setShortcut('Ctrl+Q')
        self.quit_act.triggered.connect(self.close)

    def createMenu(self):
        self.menuBar().setNativeMenuBar(False)
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction(self.load_file_act)
        file_menu.addAction(self.save_changes_act)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_act)

    def loadFile(self, filename=None):

        def parseFile(filename):
            self.game = Game(filename)
            if (self.game.metadata is None):
                file_warning = QMessageBox.warning(self, 'Error Parsing File',
                            "The selected file isn't compatible with this editor",
                            buttons=QMessageBox.StandardButton.Ok
                            )
            else:
                self.save_changes_act.setDisabled(False)
                self.setUpWindow()

        if not filename:
            filename, ok = QFileDialog.getOpenFileName(self, 'Open Save Game File',
                os.curdir, 'Game Save Files (*.xml)')
            if ok:
                parseFile(filename)
        else:
            parseFile(filename)

    def showPerks(self):
        if hasattr(self, 'itemWindow'):
            self.itemWindow.close()
        self.perkWindow = QWidget()
        self.perkWindow.setWindowTitle('all perks')
        self.perkWindow.setGeometry(0, 0, 600, 480)
        vbox = QVBoxLayout()
        self.perkWindow.setLayout(vbox)
        vbox.addWidget(QLabel('drag perks to your character to add'))

        perkfilters_hbox = QHBoxLayout()
        perkfilters_hbox.addWidget(QLabel('Filters:'))
        perkfilters_group = QButtonGroup()
        vbox.addLayout(perkfilters_hbox)

        filter_types = {'Quirks': 'QRK', 'Perks': 'PRK', 'Backgrounds': 'BCK' }
        def search_perks(text):
            show = perklist.findItems(text, Qt.MatchFlag.MatchContains)
            [(perklist.item(i).setHidden(False) if perklist.item(i) in show else perklist.item(i).setHidden(True)) for i in range(perklist.count())]
        def filter_perks(text):
            show = perklist.findItems(filter_types[text], Qt.MatchFlag.MatchStartsWith)
            [(perklist.item(i).setHidden(False) if perklist.item(i) in show else perklist.item(i).setHidden(True)) for i in range(perklist.count())]
        perk_search_hbox = QHBoxLayout()
        perk_search = QLineEdit()
        perk_search_label = QLabel('Search')
        perk_search.textChanged.connect(lambda: search_perks(perk_search.text()))
        perk_search_hbox.addWidget(perk_search_label)
        perk_search_hbox.addWidget(perk_search)
        vbox.addLayout(perk_search_hbox)

        perklist = QListWidget()
        perklist.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        perklist.setDragEnabled(True)
        with open(perks_filename) as f:
            data = [s.strip('\n') for s in f.readlines()]
            perklist.addItems(data)
        vbox.addWidget(perklist)
        self.perkWindow.show()
        self.perkWindow.move(self.geometry().center())


        for i in filter_types.keys():
            rbtn = QRadioButton(i)
            # shouldn't use IIFE here, it's messy
            (lambda text: rbtn.clicked.connect(lambda: filter_perks(text)))(i)
            perkfilters_group.addButton(rbtn)
            perkfilters_hbox.addWidget(rbtn)


    def showItems(self):
        if hasattr(self, 'perkWindow'):
            self.perkWindow.close()
        self.itemWindow = QWidget()
        self.itemWindow.setWindowTitle('All In-Game Items')
        self.itemWindow.setGeometry(0, 0, 600, 480)
        vbox = QVBoxLayout()
        self.itemWindow.setLayout(vbox)
        vbox.addWidget(QLabel('You can drag and drop items into your inventory from here'))
        itemfilters_hbox = QHBoxLayout()
        itemfilters_hbox.addWidget(QLabel('Filters:'))
        itemfilters_group = QButtonGroup()
        # possibly missing types, I don't haven't scraped enough saves to know?
        filter_types = {'Consumables': 'ITM_Consumable', 'Armor Mods': 'ITM_ArmorMod',
                        'Armor': 'ITM_Equip_Armor', 'Weapon Mods': 'ITM_WeaponMod',
                        'Weapons': 'ITM_Equip_Weapon', 'Ammo': 'Ammo',
                        'Crafting': 'ITM_Crafting', 'Trinkets': 'ITM_Equip_Trinket',
                        'Cyborg': 'ITM_Equip_Cyborg'
                        }
        vbox.addLayout(itemfilters_hbox)

        itemlist = QListWidget()
        itemlist.setDragEnabled(True)
        itemlist.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        itemlist.addItems(self.all_items)

        def search_items(substr):
            substr = substr.lower()
            show = itemlist.findItems(substr, Qt.MatchFlag.MatchContains)
            [(itemlist.item(i).setHidden(False) if itemlist.item(i) in show else itemlist.item(i).setHidden(True)) for i in range(itemlist.count())]
        itemsearch_hbox = QHBoxLayout()
        itemsearch_label = QLabel('Search')
        itemsearch = QLineEdit()
        #itemsearch.changeEvent.connect(lambda ev: print('textbox change'))
        itemsearch.textChanged.connect(lambda: search_items(itemsearch.text()))
        itemsearch_hbox.addWidget(itemsearch_label)
        itemsearch_hbox.addWidget(itemsearch)
        vbox.addLayout(itemsearch_hbox)

        vbox.addWidget(itemlist)
        #vbox.addWidget(QPushButton('Add all selected items to inventory'))
        self.itemWindow.show()
        self.itemWindow.move(self.geometry().center())

        def filter_items(text):
            #for i in range(itemlist.count()):
                #itemlist.item(i).setHidden(True)
            #show = itemlist.findItems(filter_types[text], Qt.MatchFlag.MatchStartsWith)
            #for item in show:
                #item.setHidden(False)
            show = itemlist.findItems(filter_types[text], Qt.MatchFlag.MatchStartsWith)
            [(itemlist.item(i).setHidden(False) if itemlist.item(i) in show else itemlist.item(i).setHidden(True)) for i in range(itemlist.count())]
        for i in filter_types.keys():
            rbtn = QRadioButton(i)
            # shouldn't use IIFE here, it's messy
            (lambda text: rbtn.clicked.connect(lambda: filter_items(text)))(i)
            itemfilters_group.addButton(rbtn)
            itemfilters_hbox.addWidget(rbtn)

    def saveFile(self):
        save_filename, ok = QFileDialog.getSaveFileName(self, 'Save File',
            os.path.split(self.game.filename)[1], 'Save Game Files (*.xml)')
        if save_filename == self.game.filename:
            backup = QMessageBox.information(self, 'Backing up original..',
                'Do you want to back up the original file (it\'s recommended!)',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if backup:
                shutil.copyfile(self.game.filename, f'{self.game.filename}.backup')

        if ok:
            self.game.save(save_filename) # causes "Windows fatal exception: access violation" (windows 10)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files[0].endswith('xml'):
            self.loadFile(files[0])

    def closeEvent(self, event):
        self.perkWindow.close() if hasattr(self, 'perkWindow') else None
        self.itemWindow.close() if hasattr(self, 'itemWindow') else None


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
