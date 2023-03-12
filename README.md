# w3se

A save game editor for inXile Entertainment's Wasteland 3

*This was tested against save files from the Linux Steam version (1.6.9.420.309496) without any DLC.*

## Usage

After **Installing** (see below), run `python src/main.py` to launch.

Use the `File- > Load Save Game` dialog. Browse to your save game file, and edit away!

## Features

- View party members and edit their stats
- Attributes and Attribute points
- Add/Edit/Remove items in the party inventory
- Add perks to each character
- Edit money quantity


## Installation

1. Clone the repository to your local system
  - `git clone https://github.com/stolinator/w3se.git`
2. [Optional] set up a virtual environment
  - `cd` into the repository folder
  - `python3 -m venv w3se`
  - `source w3se/bin/activate`
3. Use `pip` to install dependencies
  - `pip install -r requirements.txt`
4. Run `main.py`
  - `python src/main.py`

## Development Notes

If your shell is `bash` compatible, `project.sh` will automate
to automate development functions. Currently, you can `run`, `test`, or`lint`
files.

### Running Tests

After installing dependencies, just run the `pytest` command.

### Running the Linter

Run `pylama src` to view any linter conflicts.

## Planned Updates

- Improve usability
    - The list views for adding/removing items and perks are cool, but need work.
- A more efficient way to find the Wasteland 3 save files on a given system
    - Should put common locations in the README
- Sort, searching, and filtering for the perk and item menus
- Removing perks
- A more efficient inventory browser (large inventories cause a noticeable app slow-down)
- Include pre-built releases for anyone looking to test out the project!
