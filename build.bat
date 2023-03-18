rem .\w3se\scripts\activate

 python -m PyInstaller -F --clean --add-data assets/export_items.txt;./assets --add-data assets/export_perks.txt;./assets --noconsole --name w3se src/main.py