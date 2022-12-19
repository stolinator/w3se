#!/bin/bash

source w3se/bin/activate

if [ $# -eq 0 ]
then
  echo project --help
  echo project [COMMAND]
  echo Options:
  printf "\tlint: runs pylama src on project"
  printf "\n\ttest: runs pytest"
  printf "\n\trun: executes the main GUI\n"
  exit
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
  echo "unknown command supplied. use --help to see options"
fi
