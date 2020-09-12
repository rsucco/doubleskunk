# doubleskunk

Terminal-based cribbage game

### Instructions:

The basic game is playable against an AI player, but is very much in a pre-release phase.  

#### Setup:
I plan to test and build this for Arch Linux, Ubuntu, macOS, and Windows 10 eventually, but for now I'm only testing it on Arch Linux. It may work on the others, but no guarantees at this point.

    pip3 install colorama pyfiglet

#### Play:
You can launch a basic game by making doubleskunk.py executable and running it.

    chmod +x ./src/doubleskunk/doubleskunk.py
    ./src/doubleskunk/doubleskunk.py

You can use the `-p` flag to set 1 or 2 players and the `-d` flag to set difficulty betwixt 1 and 3.
