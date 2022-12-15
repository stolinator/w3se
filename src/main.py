import sys, os, shutil
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QTabWidget,
    QLabel, QPushButton, QMenuBar, QVBoxLayout, QHBoxLayout, QFileDialog,
    QTableView, QMessageBox)
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtGui import QPixmap, QFont, QAction
from utility import load, save, parse, Character, isSkill


class MainWindow(QMainWindow):

    def __init__(self):
        self.characters = []
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
        for character in self.characters:
            model = CharacterModel(character=character)
            table = QTableView()
            table.setModel(model)
            table.horizontalHeader().hide()
            name = character.displayName.string if character.displayName else 'None'
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
            self.meta_data, save_data = load(filename)
            self.filename = filename
            self.xml = parse(save_data)
            self.characters = [Character(self.xml,i) for i in range(len(self.xml('pc')))]
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
            save(save_filename, self.meta_data, str(self.xml.save))

class CharacterModel(QAbstractTableModel):

    def __init__(self, parent=None, character=None):
        super().__init__(parent)
        self.character = character

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.character.fields[section]
        return None

    def rowCount(self, parent=None):
        return len(self.character.fields)

    def columnCount(self, parent=None):
        return 1

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            trait = self.character.fields[index.row()]
            self.character.mod_skill(trait, value) if isSkill(trait) else self.character.mod(trait, value)
        return True

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        row = index.row()
        column = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            trait = self.character.fields[index.row()]
            return str(self.character.fetch_skill(trait) if isSkill(trait) else self.character.fetch(trait))
        return None

    def flags(self, index):
        result = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        # disable edits on the name column
        if index.row() == 1:
            result = result | Qt.ItemFlag.ItemIsEditable
        return result


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
