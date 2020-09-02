from hand import Hand
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

    def cut_deck(self):
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
    def select_discards(self):
        VALID_CHARS = ['0', '1', '2', '3', '4', '5', '6', '7',
                       '8', '9', 't', 'j', 'q', 'k', 'a', 'h', 's', 'd', 'c']
        SUIT_CHARS = ['s', 'h', 'c', 'd']
        # Only retain valid input, stripping all whitespace and junk
        # Convert any 10's to t's and so on to make handling them easier
        # Even though we have to convert them back later, this makes it easier to allow fuzzy input
        discard_input = [char for char in input().lower().replace('10', 't')
                         if char in VALID_CHARS]

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

        def get_suit(suit):
            if suit in SUIT_CHARS:
                return suit
            else:
                return '0'

        discards = []
        # Get the first card
        num_rank = get_num_rank(discard_input[0])
        # If this is a suit, it'll be the right one, and if it's the next card's rank, it'll be the default 0
        suit = get_suit(discard_input[1])
        discards.append(self.hand.discard(num_rank, suit))

        # The first card wasn't passed with a suit. That means the number starts one position earlier
        if suit == '0':
            num_rank = get_num_rank(discard_input[1])
        else:
            num_rank = get_num_rank(discard_input[2])
        # Calling get_suit on the last character will return the correct suit if there is one
        # If the last character is the rank instead, it'll be the default 0
        suit = get_suit(discard_input[-1])
        discards.append(self.hand.discard(num_rank, suit))
        return discards


# Class for AI player
class AIPlayer(Player):
    def __init__(self, difficulty, verbose=False):
        super().__init__()
        self.difficulty = difficulty
        self.verbose = verbose

    def cut_deck(self):
        return random.randint(4, 36)

    def select_discards(self):
        discards = [self.hand.cards[0], self.hand.cards[1]]
        self.hand.cards = self.hand.cards[2:]
        return discards
