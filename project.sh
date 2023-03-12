#!/bin/bash

source w3se/bin/activate

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
else
  show_help
fi
