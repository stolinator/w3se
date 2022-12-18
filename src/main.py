import sys, os, shutil
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QTabWidget,
    QLabel, QPushButton, QMenuBar, QVBoxLayout, QHBoxLayout, QFileDialog,
    QTableView, QMessageBox, QListView, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QAction
from models import CharacterModel, GameSave, ItemModel, PerkModel
from utility import load, save, parse


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        #self.setUpWindow()
        self.createActions()
        self.createMenu()
        self.show()

    def initUI(self):
        self.setGeometry(200, 100, 600, 480)
        self.setWindowTitle('Wasteland 3 Save Editor')

    def setUpWindow(self):
        main_widget = QTabWidget()
        character_edit = QWidget()
        globals_edit = QWidget()
        globals_vlayout = QVBoxLayout()
        globals_hlayout1 = QHBoxLayout()
        globals_edit.setLayout(globals_vlayout)
        globals_vlayout.addWidget(QLabel('Edit global values'))
        globals_vlayout.addLayout(globals_hlayout1)
        globals_hlayout1.addWidget(QLabel('Money'))
        money_edit = QLineEdit()
        money_edit.textEdited.connect(lambda: self.game.set_money(money_edit.text()))
        globals_hlayout1.addWidget(QLabel('Money'))
        globals_hlayout1.addWidget(money_edit)
        inventory_edit = QWidget()
        inventory_edit_vbox = QVBoxLayout()
        inventory_edit.setLayout(inventory_edit_vbox)
        inventory_items = QTableView()
        inventory_model = ItemModel(xml = self.game.inventory)
        inventory_items.setModel(inventory_model)
        inventory_edit_vbox.addWidget(inventory_items)
        inv_hbox_btns = QHBoxLayout()
        add_item_btn = QPushButton('add item')
        remove_item_btn = QPushButton('remove item')
        remove_item_btn.clicked.connect(lambda: [inventory_model.removeRow(i.row(), i) for i in inventory_items.selectedIndexes()])
        inv_hbox_btns.addWidget(add_item_btn)
        inv_hbox_btns.addWidget(remove_item_btn)
        inventory_edit_vbox.addLayout(inv_hbox_btns)
        character_edit_vbox = QVBoxLayout()
        tabs = QTabWidget()
        # loop through characters, create edit page with layout
        for character in self.game.characters:
            model = CharacterModel(character=character)
            skilltable = QTableView()
            skilltable.setModel(model)
            skilltable.horizontalHeader().hide()
            #name = character.displayName.string if character.displayName else 'None'
            #print(character)
            perklist = QListView()
            perklist.setModel(character.perks)
            name = character.displayName
            character_page = QWidget()
            vbox = QVBoxLayout()
            hbox = QHBoxLayout()
            hbox_vbox = QVBoxLayout()
            #vbox.addWidget(table)
            vbox.addLayout(hbox)
            hbox.addWidget(skilltable)
            hbox.addLayout(hbox_vbox)
            hbox_vbox.addWidget(QLabel(f"Edit {name}'s Perks"))
            hbox_vbox.addWidget(perklist)
            character_page.setLayout(vbox)
            tabs.addTab(character_page, name)
        character_edit_vbox.addWidget(tabs)
        character_edit.setLayout(character_edit_vbox)
        main_widget.addTab(tabs, 'Edit Characters')
        main_widget.addTab(inventory_edit, 'Edit Inventory')
        main_widget.addTab(globals_edit, 'Edit Global Values')
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
            meta, save = load(filename)
            self.game = GameSave(meta, parse(save))
            self.filename = filename
            self.save_changes_act.setDisabled(False)
            self.setUpWindow()

    def saveFile(self):
        backup = QMessageBox.information(self, 'Backing up original..',
            'Do you want to back up the original file (it\'s recommended!)',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if backup:
            shutil.copyfile(self.filename, f'{self.filename}.backup')
        save_filename, ok = QFileDialog.getSaveFileName(self, 'Save File',
            os.path.split(self.filename)[1], 'Save Game Files (*.xml)')
        if ok:
            print(save_filename)
            save(save_filename, self.game.meta_data, self.game.save_data)
            #save(save_filename, self.meta_data, str(self.xml.save))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
