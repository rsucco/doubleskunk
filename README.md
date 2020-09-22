# doubleskunk

Terminal-based cribbage game

#### Setup:
Note: Other Linux distributions besides Arch and Ubuntu should work fine. Just replace the commands below with the correct equivalents from your distro's package manager. The minimum supported and tested version of Python is 3.4.

##### Arch Linux:
    sudo pacman -S python python-pip
    sudo pip install colorama pyfiglet typing
##### Ubuntu:
    sudo apt update && sudo apt install python3 python3-pip -y
    sudo pip3 install colorama pyfiglet typing
##### macOS:
Note: If you don't have [Homebrew](https://brew.sh/) installed already, you'll have to install it first.

    brew install python
    sudo -H pip3 install colorama pyfiglet typing
##### Windows 10:
Note: If you don't have [Chocolatey](https://chocolatey.org/) installed already, you'll have to install it first.
Python 3.4+ is required, but if you're using a different version than 3.8, replace 'Python38' with the correct directory
name below. Run these commands in an Administrator PowerShell terminal.

    choco install python pip
    C:\Python38\Scripts\pip3.exe install colorama pyfiglet typing

#### Play:
##### Linux/macOS

    chmod +x ./doubleskunk.py
    ./doubleskunk.py

##### Windows 10
Note: If you have a version of Python 3 installed other than Python 3.8, change the path here accordingly.
If you followed the setup instructions above, this should work.

    C:\Python38\python.exe doubleskunk.py

You can use the `-p` flag to set 1 or 2 players and the `-d` flag to set difficulty betwixt 1 and 3, or just launch the
game with no flags and select your difficulty and number of players from the game's menus.

#### Release Notes:
##### 0.1 (20SEP2020):
The game is playable enough at this point that I think a 0.1 release is justified. More work is needed to pretty it up,
I'm still squishing little bugs here and there, and I still need to implement building and packaging for Windows/macOS,
but I'm happy enough with the stability of the engine and the performance of the AI opponent to call it playable.
