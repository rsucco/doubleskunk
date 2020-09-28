#!/usr/bin/env python3
import sys
import argparse
from game import Game
from pyfiglet import Figlet
from colorama import Style, Fore
from os import name, system


def print_welcome():
    if name == 'nt':
        system('cls')
    else:
        system('clear')
    f = Figlet(font='slant', width=80)
    print(Style.BRIGHT + Fore.LIGHTRED_EX + '\n' + '-' * 80 + '\n' + Style.RESET_ALL)
    print(f'{Style.BRIGHT}{Fore.GREEN}{f.renderText("   DOUBLE")}{Style.RESET_ALL}')
    print(f'{Style.BRIGHT}{Fore.LIGHTRED_EX}{f.renderText("                 SKUNK")}{Style.RESET_ALL}')
    print(Style.BRIGHT + Fore.LIGHTGREEN_EX + '\n' + '-' * 80 + '\n' + Style.RESET_ALL)
    print(Style.BRIGHT + 'Please maximize your terminal window for the best experience.\n' + Style.RESET_ALL)


# noinspection PyBroadException
def main():
    # Check for command-line arguments
    parser = argparse.ArgumentParser(description='Play a game of cribbage.')
    parser.add_argument('-d', '--difficulty', nargs='?', default=-1, type=int,
                        choices=range(1, 4), metavar='1-3', help='Set difficulty')
    parser.add_argument('-p', '--players', nargs='?', default=-1, type=int,
                        choices=range(3), metavar='0-2', help='Set number of players')
    parser.add_argument('-D', '--debug', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('--test', action='store_true',
                        help='Jump straight to current test')
    args = parser.parse_args(sys.argv[1:])

    print_welcome()

    # Set number of players
    try:
        # Check if the user passed a valid number of players via command line, and use it if so
        if args.players in range(3):
            num_players = args.players
        else:
            num_players = input(
                'Enter 1 or 2 for number of players (default 1):')
            num_players = int(num_players[0])
            # If the user gave invalid input or no input, use the default
            if num_players not in range(3):
                num_players = 1
    # Either the user pressed enter for the default, or they can't even be trusted to type in an integer
    except Exception:
        num_players = 1

    # Set difficulty
    try:
        # Check if the user passed a valid difficulty via command line, and use it if so
        if args.difficulty in range(1, 4):
            difficulty = args.difficulty
        else:
            difficulty = input(
                'Enter 1 for easy difficulty, 2 for medium, 3 for hard (default 2):')
            difficulty = int(difficulty[0])
            # If the user gave invalid input or no input, use the default
            if difficulty not in range(1, 4):
                difficulty = 2
    except Exception:
        difficulty = 2

    game = Game(num_players, difficulty, args.debug)
    game.play()


if __name__ == '__main__':
    main()
