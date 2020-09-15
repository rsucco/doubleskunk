#!/usr/bin/env python3
import sys
import argparse
from game import Game
from card import Card
from hand import Hand


# Jump right into the part I'm currently testing
def jump_to_test():
    game = Game(1, 3, True)
    game.dealer = 0
    game.pone = 1
    cards = [Card(2, 's'),
             Card(3, 's'),
             Card(5, 's'),
             Card(7, 's'),
             Card(8, 's'),
             Card(6, 'd')]
    game.players[0].hand = Hand(cards)
    cards = [Card(4, 'c'),
             Card(5, 'c'),
             Card(6, 's'),
             Card(4, 'h'),
             Card(9, 'd'),
             Card(13, 'h')]
    game.players[1].hand = Hand(cards)
    # cards = [Card(7, 'h'),
    #          Card(8, 'h'),
    #          Card(9, 'h'),
    #          Card(10, 'h')]
    # game.crib = Hand(cards)
    game.get_discards()
    game.get_upcard()
    game.show_hands()
    #game.pegging()
    exit()


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
    print(args)
    if args.test:
        jump_to_test()
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
