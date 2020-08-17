from deck import Deck
from hand import Hand
from card import Card
from score import Score
from os import system, name
from sys import exit
from colorama import Fore, Back, Style
from pyfiglet import Figlet


def get_command():
    return input(
        'Enter \'q\' to quit, \'c\' to count a custom hand, or press enter to count a random hand:')


# Get a custom hand from the user in a (hopefully) idiot-proof way
def get_rank():
    while True:
        try:
            rank = input(
                'Input numerical rank from 1-13, or use the letters A, J, Q, or K:')
            if rank[0].lower() == 'a':
                rank = 1
            elif rank[0].lower() == 'j':
                rank = 11
            elif rank[0].lower() == 'q':
                rank = 12
            elif rank[0].lower() == 'k':
                rank = 13
            else:
                rank = int(rank)
            if rank > 0 and rank < 14:
                return rank
            else:
                raise Exception()
        except Exception:
            print('Invalid rank.')
            continue


def get_suit():
    # Stylish ways to write the suits
    SPADES = str(f'{Fore.LIGHTYELLOW_EX}[s]pades ♠{Style.RESET_ALL}')
    HEARTS = str(f'{Fore.RED}[h]earts ♥{Style.RESET_ALL}')
    CLUBS = str(f'{Fore.GREEN}[c]lubs ♣{Style.RESET_ALL}')
    DIAMONDS = str(f'{Fore.BLUE}[d]iamonds ♦{Style.RESET_ALL}')
    while True:
        try:
            suit = input(
                'Input first letter of suit: ' + SPADES + ', ' + HEARTS + ', ' + CLUBS + ', or ' + DIAMONDS + ':')[0].lower()
            if suit == 's' or suit == 'h' or suit == 'c' or suit == 'd':
                return suit
            else:
                raise Exception()
        except Exception:
            print('Invalid suit.')
            continue


def get_custom_hand():
    clear()
    cards = []
    for i in range(4):
        print('Enter card number ', i + 1, ' for your hand:')
        rank = get_rank()
        suit = get_suit()
        cards.append(Card(rank, suit))
        print(Hand(cards))
    print('Enter cut card:')
    rank = get_rank()
    suit = get_suit()
    upcard = Card(rank, suit)
    is_crib = input('Crib y/n? [default n]')
    if is_crib.lower() == 'y':
        is_crib = True
    else:
        is_crib = False
    hand = Hand(cards, is_crib, upcard)
    clear()
    return hand


def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')


command = 'first_run'
while command != 'q':
    clear()
    # Show some niceties the first time
    if command == 'first_run':
        f = Figlet(font='big', width=100)
        print(
            f'{Fore.BLUE}{f.renderText("Cribbage")}{Style.RESET_ALL}')
        print(f'{Fore.RED}{f.renderText("Counting")}{Style.RESET_ALL}')
        print(f'{Fore.LIGHTGREEN_EX}{f.renderText("Demo")}{Style.RESET_ALL}')
        command = get_command()
    if command == 'c':
        hand = get_custom_hand()
    else:
        # Create and shuffle a deck to get a random hand
        deck = Deck()
        deck.shuffle()
        # Deal four cards to the hand and one to the upcard
        hand = Hand(deck.deal_card(4))
        hand.upcard = deck.deal_card(1)[0]
    clear()
    print('Hand cards: ')
    print(Score(hand.cards, 0))
    print('Cut card: ')
    print(hand.upcard)
    print('All cards:')
    print(hand, '\n***************\n')
    hand.count(True)
    hand = Hand()
    command = get_command()
