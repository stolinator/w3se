import sys, os, shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QTabWidget,
    QLabel, QPushButton, QMenuBar, QVBoxLayout, QHBoxLayout,
    QFileDialog, QTableView, QMessageBox, QListView, QLineEdit,
    QListWidget)
from PyQt6.QtGui import QPixmap, QFont, QAction
from models.character import CharacterModel
from models.game import Game
from models.items import ItemModel
from models.perks import PerkModel


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.createActions()
        self.createMenu()
        self.show()

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
        vbox.addWidget(item_view)
        hbox = QHBoxLayout()
        btn_add = QPushButton('show all items')
        btn_add.clicked.connect(self.showItems)
        btn_remove = QPushButton('remove item')
        btn_remove.clicked.connect(
            lambda: [inventory_model.removeRow(i.row(), i) for i in inventory_items.selectedIndexes()]
        )
        hbox.addWidget(btn_add)
        hbox.addWidget(btn_remove)
        vbox.addLayout(hbox)
        return editor

    def createCharacterEditor(self):
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
            btn_show_perks = QPushButton('show all perks')
            btn_show_perks.clicked.connect(self.showPerks)
            perk_btns_box = QHBoxLayout()
            perk_btns_box.addWidget(btn_show_perks)
            hbox_vbox.addLayout(perk_btns_box)
            character_page.setLayout(vbox)
            tabs.addTab(character_page, name)
        editor_vbox.addWidget(tabs)
        editor.setLayout(editor_vbox)
        return editor

    def setUpWindow(self):
        main_widget = QTabWidget()
        tab_functions = {
            'Edit Characters': self.createCharacterEditor,
            'Edit Inventory': self.createInventoryEditor,
            'Edit Global Values': self.createGlobalEditor
        }
        for label, func in tab_functions.items():
            main_widget.addTab(func(), label)
        self.setCentralWidget(main_widget)

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

    def loadFile(self):
        filename, ok = QFileDialog.getOpenFileName(self, 'Open Save Game File',
            os.curdir, 'Game Save Files (*.xml)')
        if ok:
            self.game = Game(filename)
            self.save_changes_act.setDisabled(False)
            self.setUpWindow()

    def showPerks(self):
        if hasattr(self, 'itemWindow'):
            self.itemWindow.close()
        self.perkWindow = QWidget()
        self.perkWindow.setWindowTitle('all perks')
        self.perkWindow.setGeometry(200, 100, 600, 480)
        vbox = QVBoxLayout()
        self.perkWindow.setLayout(vbox)
        vbox.addWidget(QLabel('drag perks to your character to add'))
        perklist = QListWidget()
        perklist.setDragEnabled(True)
        with open('export_perks.txt') as f:
            data = [s.strip('\n') for s in f.readlines()]
            print(data)
            perklist.addItems(data)
        vbox.addWidget(perklist)
        self.perkWindow.show()

    def showItems(self):
        if hasattr(self, 'perkWindow'):
            self.perkWindow.close()
        self.itemWindow = QWidget()
        self.itemWindow.setWindowTitle('all items')
        self.itemWindow.setGeometry(200, 100, 600, 480)
        vbox = QVBoxLayout()
        self.itemWindow.setLayout(vbox)
        vbox.addWidget(QLabel('drag items to your inventory to add'))
        itemlist = QListWidget()
        itemlist.setDragEnabled(True)
        with open('export_items.txt') as f:
            data = [s.strip('\n') for s in f.readlines()]
            print(data)
            itemlist.addItems(data)
        vbox.addWidget(itemlist)
        self.itemWindow.show()

    def saveFile(self):
        backup = QMessageBox.information(self, 'Backing up original..',
            'Do you want to back up the original file (it\'s recommended!)',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if backup:
            shutil.copyfile(self.game.filename, f'{self.game.filename}.backup')
        save_filename, ok = QFileDialog.getSaveFileName(self, 'Save File',
            os.path.split(self.game.filename)[1], 'Save Game Files (*.xml)')
        if ok:
            print(save_filename)
            self.game.save(save_filename)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
