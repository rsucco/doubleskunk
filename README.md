# doubleskunk

Terminal-based cribbage game

#### Setup:
Note: Other Linux distributions besides Arch and Ubuntu should work fine. Just replace the commands below with the
correct equivalents from your distro's package manager. The minimum supported and tested version of Python is 3.6.

##### Arch Linux:
    sudo pacman -S python python-colorama python-pyfiglet
##### Ubuntu:
    sudo apt update && sudo apt install python3 python3-pip -y
    sudo pip3 install colorama pyfiglet typing
##### Gentoo:
    sudo emerge dev-lang/python dev-python/pip
    sudo pip3 install --user colorama pyfiglet typing
##### FreeBSD:
    sudo pkg install python3 py38-pip
    pip install colorama pyfiglet typing
##### macOS:
Note: If you don't have [Homebrew](https://brew.sh/) installed already, you'll have to install it first.

    brew install python
    sudo -H pip3 install colorama pyfiglet typing
##### Windows 10:
Note: If you don't have [Chocolatey](https://chocolatey.org/) installed already, you'll have to install it first.
Python 3.6+ is required, but if you're using a different version than 3.8, replace 'Python38' with the correct directory
name below. Run these commands in an Administrator PowerShell terminal.

    choco install python pip
    C:\Python38\Scripts\pip3.exe install colorama pyfiglet typing

#### Play:
##### Linux/macOS

    ./terminal_client/doubleskunk.py

##### Windows 10
Note: If you have a version of Python 3 installed other than Python 3.8, change the path here accordingly.
If you followed the setup instructions above, this should work.

    C:\Python38\python.exe .\terminal_client\doubleskunk.py

You can use the `-p` flag to set 1 or 2 players and the `-d` flag to set difficulty betwixt 1 and 3, or just launch the
game with no flags and select your difficulty and number of players from the game's menus.

#### Release Notes:
##### 0.1.1 (23SEP2020):
I added Windows running instructions and some minor bug fixes and performance improvements. Going forward, the network
multiplayer is going to be the main focus, and when that branch is stable and merged I'll call it 0.2. Until then, I'll
periodically update 0.1.* with minor bug fixes, but the human vs. AI terminal cribbage game can be considered to be,
for all practical purposes, complete.

##### 0.1 (20SEP2020):
The game is playable enough at this point that I think a 0.1 release is justified. More work is needed to pretty it up,
I'm still squishing little bugs here and there, and I still need to implement building and packaging for Windows/macOS,
but I'm happy enough with the stability of the engine and the performance of the AI opponent to call it playable.
