import sys, os, shutil
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QTabWidget,
    QLabel, QPushButton, QMenuBar, QVBoxLayout, QHBoxLayout, QFileDialog,
    QTableView, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QAction
from models import CharacterModel, GameSave
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
        main_widget = QWidget()
        main_vbox = QVBoxLayout()
        tabs = QTabWidget()
        # loop through characters, create edit page with layout
        for character in self.game.characters:
            model = CharacterModel(character=character)
            table = QTableView()
            table.setModel(model)
            table.horizontalHeader().hide()
            #name = character.displayName.string if character.displayName else 'None'
            print(character)
            name = character.displayName
            character_page = QWidget()
            vbox = QVBoxLayout()
            vbox.addWidget(table)
            character_page.setLayout(vbox)
            tabs.addTab(character_page, name)
        main_vbox.addWidget(tabs)
        main_vbox.addWidget(QLabel('edit globals here'))
        main_widget.setLayout(main_vbox)
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
