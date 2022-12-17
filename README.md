# w3se

A save game editor for inXile Entertainment's Wasteland 3

*This was tested against save files from the Linux Steam version (1.6.9.420.309496) without any DLC.*

## Usage

Use the `File- > Load Save Game` dialog. Browse to your save game file, and edit away!

## Features

- View party members and edit their stats
- Attributes and Attribute points
- Add items to your party's inventory


## Installation

1. Clone the repository to your local system
  - `git clone https://github.com/stolinaotr/w3se.git`
2. [Optional] set up a virtual environment
  - `cd` into the repository folder
  - `python3 -m venv w3se`
3. Use `pip` to install dependencies
  - `pip install -r requirements.txt`
4. Run `main.py`
  - `python src/main.py`

## Development Notes

### Running Tests

After installing dependencies, just run the `pytest` command.

### Running the Linter

Run `pylama src` to view any linter conflicts.

#### Planned Functionality

Currently rewriting the model/view between PyQt and BeautifulSoup, which should
enable the following actions:

- Edit money
- Edit perks
- Add/Edit items in party inventory
- Improve usability (refactor layout), write better logic for File Dialog
