#!/bin/bash

if [ -d w3se ]
then
  source w3se/bin/activate
else
  echo "w3se not found, unable to activate virtual environment"
fi

show_help() {
  echo Usage: project [COMMAND]
  echo ----- HELP -----
  echo Options:
  printf "\tlint: runs pylama src on project"
  printf "\n\ttest: runs pytest"
  printf "\n\trun: executes the main GUI\n"
  exit
}

if [ $# -eq 0 ]
then
  show_help
fi


if [ "$1" == "lint" ]
then
  pylama src
elif [ "$1" == "test" ]
then
  clear && pytest
elif [ "$1" == "run" ]
then
  python src/main.py
elif [ "$1" == "build" ]
then
  python -m PyInstaller -F --clean --add-data 'assets/export_items.txt:./assets' --add-data 'assets/export_perks.txt:./assets' --name w3se src/main.py
else
  show_help
fi
