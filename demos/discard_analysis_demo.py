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
        'Enter \'q\' to quit, \'c\' to analyze a custom hand, or press enter to analyze a random hand:')


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


def get_dealer():
    while True:
        try:
            dealer = input('Calculate as [d]ealer, [p]one, or [b]oth?')[
                0].lower()
            if dealer == 'd' or dealer == 'p' or dealer == 'b':
                return dealer
            else:
                raise Exception()
        except Exception:
            print('Invalid response. Enter a d, p, or b.')
            continue


def get_custom_hand():
    clear()
    cards = []
    for i in range(6):
        print('Enter card number', i + 1, 'for your hand:')
        rank = get_rank()
        suit = get_suit()
        cards.append(Card(rank, suit))
        print(Hand(cards))
    return Hand(cards)


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
            f'{Fore.BLUE}{f.renderText("Discard")}{Style.RESET_ALL}')
        print(f'{Fore.RED}{f.renderText("Analysis")}{Style.RESET_ALL}')
        print(f'{Fore.LIGHTGREEN_EX}{f.renderText("Demo")}{Style.RESET_ALL}')
        command = get_command()
    if command == 'c':
        hand = get_custom_hand()
        dealer = get_dealer()
    elif command == 'q':
        break
    else:
        # Create and shuffle a deck to get a random hand
        deck = Deck()
        deck.shuffle()
        # Deal six cards to the hand
        hand = Hand(deck.deal_card(6))
        # Show both dealer and pone analysis
        dealer = 'b'
    clear()

    if dealer == 'd' or dealer == 'b':
        print('Hand cards: \n')
        print(Score(hand.cards, 0), '\n')
        print('Best discards for dealer:\n*******************\n')
        hand.best_discard(True, True)
        if dealer == 'b':
            input('Press enter to see best discards for pone.')
            clear()
    if dealer == 'p' or dealer == 'b':
        print('Hand cards: \n')
        print(Score(hand.cards, 0), '\n')
        print('Best discards for pone:\n*******************\n')
        hand.best_discard(False, True)
    hand = Hand()
    command = get_command()
