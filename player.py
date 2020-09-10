from hand import Hand
from card import Card
from colorama import Fore, Back, Style
import traceback
import random


# Base Player class
class Player:
    def __init__(self, victory_callback, player_num):
        self.victory = victory_callback
        self.player_num = player_num
        self.score = 0
        self.last_score = -1
        self.hand = Hand()

    def peg_at(self, num):
        if self.last_score == num or self.score == num:
            return True
        return False

    # Increase score and set last_score
    def add_points(self, points):
        if points > 0:
            self.last_score = self.score
            self.score += points
        # Call the victory callback to notify the game that we won
        if self.score >= 121:
            self.score = 121
            self.victory(self.player_num)


# Class for human player
class HumanPlayer(Player):
    def __init__(self, victory_callback, player_num):
        super().__init__(victory_callback, player_num)

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

    # Get card input from player
    def get_card_input(self, num_cards):
        # Filtering constants
        VALID_CHARS = ['2', '3', '4', '5', '6', '7',
                       '8', '9', 't', 'j', 'q', 'k', 'a', 'h', 's', 'd', 'c']
        SUIT_CHARS = ['s', 'h', 'c', 'd']

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

        # Convert 10's to t's, 1's to a's, and uppercase to lowercase. Anything valid will be matched to VALID_CHARS
        discard_input = [char for char in input().lower().replace('10', 't').replace('1', 'a')
                         if char in VALID_CHARS]
        discards = []
        # Get the first card
        num_rank = get_num_rank(discard_input[0])

        # Getting just one card requires special handling
        if num_cards == 1:
            suit = get_suit(discard_input[-1])
            return (num_rank, suit)

        # The character after the rank is always the suit
        # Either the suit was specified, or its the next card's rank, which returns the default '0'
        suit = get_suit(discard_input[1])
        discards.append((num_rank, suit))

        # The first card wasn't passed with a suit. That means the number starts one position earlier
        if suit == '0':
            num_rank = get_num_rank(discard_input[1])
        else:
            num_rank = get_num_rank(discard_input[2])
        # Calling get_suit on the last character will return the correct suit if there is one
        # If the last character is the second card's rank instead, it'll be the default '0'
        suit = get_suit(discard_input[-1])
        discards.append((num_rank, suit))
        return discards

    # Parse input to determine discard choices.
    # Returns a list of the discards and removes them from its Hand object
    def select_discards(self, set_message, dealer):
        # Update UI
        base_messages = ['You can use the numbers 2-10 as well as A, T, J, Q, and K.',
                         '',
                         'If you want to specify, you can include the first letter of the suit:',
                         Card.SPADES + ', ' + Card.HEARTS + ', ' + Card.CLUBS + ', or ' + Card.DIAMONDS,
                         '',
                         'If you don\'t care which suit is discarded, you don\'t need to include it.']
        if dealer:
            set_message(
                Style.BRIGHT + 'Your deal.' + Style.RESET_ALL, 'Enter two cards for your crib. (Spacing between them is optional)')
        else:
            set_message(
                Style.BRIGHT + 'Opponent\'s deal.' + Style.RESET_ALL, 'Enter two cards for opponent\'s crib. (Spacing between them is optional)')
        set_message(*base_messages, append_msg=True)
        discards = []
        while True:
            try:
                discard_input = self.get_card_input(2)
                for card in discard_input:
                    discards.append(self.hand.discard(card[0], card[1]))
                break
            except Exception:
                traceback.print_exc()
                # Put discards back in hand
                for discard in discards:
                    self.hand.cards.append(discard)
                discards = []
                if dealer:
                    msgs = [Style.BRIGHT + 'Your deal.' + Style.RESET_ALL,
                            'Invalid input. Enter two cards for your crib. (Spacing between them is optional)']
                else:
                    msgs = [Style.BRIGHT + 'Opponent\'s deal.' + Style.RESET_ALL,
                            Style.BRIGHT + 'Invalid input.' + Style.RESET_ALL + ' Enter two cards for opponent\'s crib. (Spacing between them is optional)']
                msgs.extend(base_messages[:4])
                msgs.extend(['', 'Example:  \'' + self.hand.cards[0].rank + self.hand.cards[0].suit + self.hand.cards[-1].rank + '\' for ' + str(
                    self.hand.cards[0]) + ' and a ' + self.hand.cards[-1].rank + ' of unspecified suit.'])
                set_message(*msgs)
        return discards

    # Get user input to make a pegging play
    def get_peg_play(self, set_message, available_cards, pegging_count, opponent_go, *args):
        # Return a go automatically if there aren't any cards
        if len(available_cards.cards) == 0:
            return -1
        # Update UI
        base_messages = [Style.BRIGHT + 'Your turn.' + Style.RESET_ALL + ' Enter a card to play and press enter.',
                         'You can use the numbers 2-10 as well as the letters A, T, J, Q, and K.', '', 'Available cards: ' + str(available_cards)]
        # Make sure the player has a valid card to play
        if any([card.value + pegging_count <= 31 for card in available_cards.cards]):
            # Make it easy for them if they only have one card
            if len(available_cards.cards) == 1:
                set_message(Style.BRIGHT + 'Your turn.' + Style.RESET_ALL +
                            ' Press enter to play your last card.', '', base_messages[-1])
                return available_cards.cards[0].num_rank
            else:
                set_message(*base_messages)
                # Keep trying until we get valid input from the player
                while True:
                    try:
                        discard_input = self.get_card_input(1)
                        if discard_input[0] in [card.num_rank for card in available_cards.cards] and Card(discard_input[0]).value + pegging_count <= 31:
                            return discard_input[0]
                        else:
                            raise Exception
                    except Exception:
                        traceback.print_exc()
                        set_message(Style.BRIGHT + 'Invalid input. Your turn.' + Style.RESET_ALL +
                                    ' Enter a card to play and press enter.')
                        set_message(*base_messages[1:], append_msg=True)
                        continue
        # Return a go if nothing plays
        else:
            # If the opponent hasn't given a go, that means we'll be saying go. Tell the player as much.
            if not opponent_go:
                set_message(Style.BRIGHT + 'Your turn. Press enter to say \'go\'!' +
                            Style.RESET_ALL, base_messages[-1])
                input()
            # If the opponent has already said go, then we'll be scoring a point, so don't print the sad message
            return -1


# Class for AI player
class AIPlayer(Player):
    def __init__(self, victory_callback, player_num, **kwargs):
        super().__init__(victory_callback, player_num)
        self.difficulty = kwargs['difficulty']
        self.verbose = kwargs['verbose']

    def cut_deck(self, *args):
        return random.randint(4, 36)

    def select_discards(self, *args):
        discards = [self.hand.cards[0], self.hand.cards[1]]
        self.hand.cards = self.hand.cards[2:]
        return discards

    def get_peg_play(self, set_cards, available_cards, pegging_count, opponent_go, played_cards):
        play_card = [
            card.num_rank for card in available_cards.cards if card.num_rank + pegging_count <= 31]
        if len(play_card) > 0:
            return play_card[0]
        else:
            return -1
