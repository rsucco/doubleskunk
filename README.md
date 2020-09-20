# doubleskunk

Terminal-based cribbage game

### Instructions:

The basic game is playable against an AI player, but is very much in a pre-release phase.  

#### Setup:
I plan to test and build this for Arch Linux, Ubuntu, macOS, and Windows 10 eventually, but for now I'm only testing it
on Arch Linux, Ubuntu, and macOS. You should also be able to install the relevant dependencies with your own distribution's
package manager and get it to run on any distribution of Linux that supports Python 3. It may work on Windows, but no
guarantees at this point.

##### Arch Linux:
    sudo pacman -S python-pip
    sudo pip install colorama pyfiglet
##### Ubuntu:
    sudo apt update && sudo apt install python3 python3-pip -y
    sudo pip3 install colorama pyfiglet
##### macOS:
Note: If you don't have [Homebrew](https://brew.sh/) installed already, you'll have to install it first.

    brew install python
    sudo -H pip3 install colorama pyfiglet


#### Play:
You can launch a basic game from a Linux or macOS terminal by making doubleskunk.py executable and running it.

    chmod +x ./src/doubleskunk/doubleskunk.py
    ./src/doubleskunk/doubleskunk.py

You can use the `-p` flag to set 1 or 2 players and the `-d` flag to set difficulty betwixt 1 and 3, or just launch the
game with no flags and select your difficulty and number of players from the game's menus.

#### Release Notes:
##### 0.1 (20SEP2020):
The game is playable enough at this point that I think a 0.1 release is justified. More work is needed to pretty it up,
I'm still squishing little bugs here and there, and I still need to implement building and packaging for Windows/macOS,
but I'm happy enough with the stability of the engine and the performance of the AI opponent to call it playable.
