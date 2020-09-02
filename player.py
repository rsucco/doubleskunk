from hand import Hand
from card import Card
import random


# Base Player class
class Player:
    def __init__(self):
        self.score = 0
        self.last_score = -1
        self.hand = Hand()

    def peg_at(self, num):
        if self.last_score == num or self.score == num:
            return True
        return False

    # Increase score and set last_score
    def add_points(self, points):
        self.last_score = self.score
        self.score += points


# Class for human player
class HumanPlayer(Player):
    def __init__(self):
        super().__init__()

    def cut_deck(self, set_message):
        set_message(
            'Enter number between 4 and 36 or press enter for random cut.', append_msg=True)
        while True:
            try:
                cut = input()
                cut = int(cut)
                if cut >= 4 and cut <= 36:
                    return cut
                else:
                    raise Exception
            except Exception:
                return random.randint(4, 36)

    # Parse input to determine discard choices.
    # Returns a list of the discards and removes them from its Hand object
    # Raises an exception if the input is invalid so the game can handle the UI for that
    def select_discards(self, set_message, dealer):
        # Filtering constants
        VALID_CHARS = ['2', '3', '4', '5', '6', '7',
                       '8', '9', 't', 'j', 'q', 'k', 'a', 'h', 's', 'd', 'c']
        SUIT_CHARS = ['s', 'h', 'c', 'd']

        # Update UI
        base_messages = ['You can use the numbers 2-10 as well as A, T, J, Q, and K',
                         '',
                         'If you want to specify, you can include the first letter of the suit:',
                         Card.SPADES + ', ' + Card.HEARTS + ', ' + Card.CLUBS + ', or ' + Card.DIAMONDS,
                         '',
                         'If you don\'t care which suit is discarded, you don\'t need to include it.']
        if dealer:
            set_message(
                'Your deal. Enter two cards for your crib. (Spacing between them is optional)')
        else:
            set_message(
                'Opponent\'s deal. Enter two cards for opponent\'s crib. (Spacing between them is optional)')
        set_message(*base_messages, append_msg=True)

        # Get numerical rank of text input so we can create a Card object

        def get_num_rank(rank):
            if rank == 'a':
                return 1
            elif rank == 't':
                return 10
            elif rank == 'j':
                return 11
            elif rank == 'q':
                return 12
            elif rank == 'k':
                return 13
            else:
                return int(rank)

        # If a char is a valid suit, return it. Otherwise, return the default suit value of '0'
        def get_suit(suit):
            if suit in SUIT_CHARS:
                return suit
            else:
                return '0'

        while True:
            try:
                # Convert 10's to t's and uppercase to lowercase. Anything valid will be matched to VALID_CHARS
                discard_input = [char for char in input().lower().replace('10', 't')
                                 if char in VALID_CHARS]
                discards = []
                # Get the first card
                num_rank = get_num_rank(discard_input[0])
                # The character after the rank is always the suit
                # Either the suit was specified, or its the next card's rank, which returns the default '0'
                suit = get_suit(discard_input[1])
                discards.append(self.hand.discard(num_rank, suit))
                # The first card wasn't passed with a suit. That means the number starts one position earlier
                if suit == '0':
                    num_rank = get_num_rank(discard_input[1])
                else:
                    num_rank = get_num_rank(discard_input[2])
                # Calling get_suit on the last character will return the correct suit if there is one
                # If the last character is the second card's rank instead, it'll be the default '0'
                suit = get_suit(discard_input[-1])
                discards.append(self.hand.discard(num_rank, suit))
                break
            except Exception:
                five_h = Card(5, 'h')
                ace_s = Card(1, 's')
                queen_d = Card(12, 'd')
                set_message(
                    'Invalid input. Enter two cards for your crib. (Spacing between them is optional)')
                set_message(*base_messages[:4], append_msg=True)
                set_message('', 'Example:  \'' + self.hand.cards[0].rank + self.hand.cards[0].suit + self.hand.cards[-1].rank + '\' for ' + str(
                    self.hand.cards[0]) + ' and a ' + self.hand.cards[-1].rank + ' of unspecified suit.', append_msg=True)
        return discards


# Class for AI player
class AIPlayer(Player):
    def __init__(self, difficulty, verbose=False):
        super().__init__()
        self.difficulty = difficulty
        self.verbose = verbose

    def cut_deck(self, *args):
        return random.randint(4, 36)

    def select_discards(self, *args):
        discards = [self.hand.cards[0], self.hand.cards[1]]
        self.hand.cards = self.hand.cards[2:]
        return discards
