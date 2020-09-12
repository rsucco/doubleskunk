from src.doubleskunk.hand import Hand
from src.doubleskunk.card import Card
from src.doubleskunk.deck import Deck
from itertools import combinations
from statistics import pstdev, mean
from colorama import Style
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

    @staticmethod
    def cut_deck(set_message):
        set_message(
            'Enter number between 4 and 36 or press enter for random cut.', append_msg=True)
        while True:
            try:
                cut = input()
                cut = int(cut)
                if 4 <= cut <= 36:
                    return cut
                else:
                    raise Exception
            except Exception:
                return random.randint(4, 36)

    # Get card input from player
    @staticmethod
    def get_card_input(num_cards):
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
    def select_discards(self, set_message, dealer, opponent_score):
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

    @staticmethod
    def cut_deck(*args):
        return random.randint(4, 36)

    # Selects and returns a list of the discards and removes them from its Hand object
    def select_discards(self, set_message, dealer, opponent_score):
        # Get best discards, sorted by highest expected net points
        best_discards = self.get_best_discards(dealer)
        # Play more recklessly if justified by the score
        # The dealer scores 16 points on average between pegging, hand, and crib
        # If they're likely to get to 121 by their next count, it's better to optimize for hand score instead of net
        if opponent_score > 104 and not dealer:
            best_discards = sorted(best_discards, key=lambda x: x['avg'], reverse=True)
        # Take a moonshot if defeat seems likely anyways
        elif opponent_score > 110 and ((self.score < 100 and not dealer) or self.score < 90):
            best_discards = sorted(best_discards, key=lambda x: x['max'], reverse=True)
        # At the highest difficulty, always make the best play
        if self.difficulty == 3:
            discard_index = 0
        # At medium difficulty, choose randomly between the five best plays
        elif self.difficulty == 2:
            discard_index = random.randrange(0, 5)
        # Yeet two random cards into the crib at easy difficulty
        else:
            discard_index = random.randrange(0, len(best_discards))
        discard = best_discards[discard_index]['discard']
        self.hand.cards = [card for card in self.hand.cards if card not in discard]
        return discard

    @staticmethod
    def get_peg_play(set_message, available_cards, pegging_count, opponent_go, played_cards):
        play_card = [
            card.num_rank for card in available_cards.cards if card.num_rank + pegging_count <= 31]
        if len(play_card) > 0:
            return play_card[0]
        else:
            return -1

    # Analyze a hand of 6 cards and determine the mathematically optimal discards
    def get_best_discards(self, dealer):
        # Create a Deck object to represent all the potential upcards
        deck_remainder = Deck()
        deck_remainder.cards = set(self.hand.cards).symmetric_difference(deck_remainder.cards)
        deck_remainder.cards = [
            card for card in deck_remainder.cards if card not in self.hand.cards]
        # Two cards must be discarded, leaving us with a 4-card hand to be analyzed
        potential_hands = list(Hand(hand)
                               for hand in combinations(self.hand.cards, 4))
        # Get stats about how each hand performs and how their associated discards are expected to play in the crib
        all_hands = []
        for hand in potential_hands:
            # Count the hand with each upcard
            upcard_counts = []
            for upcard in deck_remainder.cards:
                hand.upcard = upcard
                upcard_counts.append((upcard, hand.count()))
            # Calculate all the stats we need for the hand
            hand_info = {}
            counts = [count[1] for count in upcard_counts]
            # The two cards that aren't in this potential hand are the cards we discarded
            hand_info['discard'] = [
                card for card in self.hand.cards if card not in hand.cards]
            hand_info['avg'] = mean(counts)
            hand_info['crib_points'] = self.expected_crib_points(
                hand_info['discard'], dealer)
            if dealer:
                hand_info['net_points'] = hand_info['avg'] + \
                    hand_info['crib_points']
            else:
                hand_info['net_points'] = hand_info['avg'] - \
                    hand_info['crib_points']
            # Store which particular upcards lead to the min/max scores
            hand_info['max'] = [(Card(), 0)]
            hand_info['min'] = [(Card(), 100)]
            for count in upcard_counts:
                if count[1] > hand_info['max'][0][1]:
                    hand_info['max'] = [count]
                elif count[1] == hand_info['max'][0][1]:
                    hand_info['max'].append(count)
                if count[1] < hand_info['min'][0][1]:
                    hand_info['min'] = [count]
                elif count[1] == hand_info['min'][0][1]:
                    hand_info['min'].append(count)
            hand_info['std_dev'] = pstdev(counts)
            # Reset the upcard before storing
            hand.upcard = Card()
            hand_info['hand'] = hand
            # Add all of the hand's info to the list of hands
            all_hands.append(hand_info)
        # Sort the hands by total net expected points
        all_hands = sorted(
            all_hands, key=lambda x: x['net_points'], reverse=True)
        # Return the list of discards
        return all_hands

    # Determine the expected number of points that a given discard will give to the crib
    # For now, this is implemented via a lookup table created from publicly available data
    # If I can ever figure out a way to calculate it dynamically myself without an unacceptable
    # performance hit, I'll do so. For now, this will have to do
    @staticmethod
    def expected_crib_points(discards, dealer=True):
        # Initialize lookup tables for estimated crib points by discard for both dealer and pone
        DEALER_TABLE = {1: [5.2, 4.4, 4.6, 5.2, 5.2, 3.7, 3.7, 3.7, 3.3, 3.3, 3.5, 3.3, 3.3],
                        2: [4.4, 5.8, 6.9, 4.6, 5.2, 3.9, 3.9, 3.7, 3.7, 3.6, 3.8, 3.6, 3.6],
                        3: [4.6, 6.9, 5.9, 5, 5.9, 3.8, 3.8, 3.9, 3.7, 3.6, 3.9, 3.7, 3.7],
                        4: [5.2, 4.6, 5, 5.5, 6.3, 3.9, 3.7, 3.9, 3.6, 3.4, 3.7, 3.5, 3.5],
                        5: [5.2, 5.2, 5.9, 6.3, 8.5, 6.4, 5.8, 5.3, 5.1, 6.3, 6.7, 6.4, 6.3],
                        6: [3.7, 3.9, 3.8, 3.9, 6.4, 5.6, 4.9, 4.6, 4.9, 3, 3.2, 3, 2.9],
                        7: [3.7, 3.9, 3.8, 3.7, 5.8, 4.9, 5.8, 6.4, 4, 3.1, 3.3, 3.1, 3.1],
                        8: [3.7, 3.7, 3.9, 3.9, 5.3, 4.6, 6.4, 5.3, 4.5, 3.7, 3.3, 3.1, 3],
                        9: [3.3, 3.7, 3.7, 3.6, 5.1, 4.9, 4, 4.5, 4.9, 4.1, 3.7, 2.8, 2.8],
                        10: [3.3, 3.6, 3.6, 3.4, 6.3, 3, 3.1, 3.7, 4.1, 4.6, 4.3, 3.3, 2.7],
                        11: [3.5, 3.8, 3.9, 3.7, 6.7, 3.2, 3.3, 3.3, 3.7, 4.3, 5.1, 4.5, 3.8],
                        12: [3.3, 3.6, 3.7, 3.5, 6.4, 3, 3.1, 3.1, 2.8, 3.3, 4.5, 4.5, 3.4],
                        13: [3.3, 3.6, 3.7, 3.5, 6.3, 2.9, 3.1, 3, 2.8, 2.7, 3.8, 3.4, 4.4]}
        PONE_TABLE = {1: [5.4, 4.5, 4.7, 5.3, 5.5, 4.4, 4.3, 4.4, 4.1, 3.9, 4.2, 3.9, 3.9],
                      2: [4.5, 5.7, 6.7, 4.8, 5.5, 4.6, 4.5, 4.4, 4.3, 4.1, 4.4, 4.1, 4.1],
                      3: [4.7, 6.7, 6, 5.4, 6, 4.4, 4.5, 4.5, 4.3, 4.2, 4.5, 4.2, 4.1],
                      4: [5.3, 4.8, 5.4, 5.7, 6.5, 4.7, 4.3, 4.4, 4.3, 4, 4.3, 4, 4],
                      5: [5.5, 5.5, 6, 6.5, 7.4, 6.6, 6.1, 5.6, 5.5, 6.4, 6.7, 6.4, 6.4],
                      6: [4.4, 4.6, 4.4, 4.7, 6.6, 6.2, 5.8, 5.4, 5.5, 3.9, 4.1, 3.8, 3.8],
                      7: [4.3, 4.5, 4.5, 4.3, 6.1, 5.8, 6.2, 6.7, 4.8, 3.9, 4.2, 3.9, 3.9],
                      8: [4.4, 4.4, 4.5, 4.4, 5.6, 5.4, 6.7, 5.8, 5.3, 4.5, 4.1, 3.9, 3.8],
                      9: [4.1, 4.3, 4.3, 4.3, 5.5, 5.5, 4.8, 5.3, 5.5, 4.8, 4.4, 3.7, 3.7],
                      10: [3.9, 4.1, 4.2, 4, 6.4, 3.9, 3.9, 4.5, 4.8, 5.1, 5, 4.1, 3.5],
                      11: [4.2, 4.4, 4.5, 4.3, 6.7, 4.1, 4.2, 4.1, 4.4, 5, 5.5, 5, 4.4],
                      12: [3.9, 4.1, 4.2, 4, 6.4, 3.8, 3.9, 3.9, 3.7, 4.1, 5, 5, 4],
                      13: [3.9, 4.1, 4.1, 4, 6.4, 3.8, 3.9, 3.8, 3.7, 3.5, 4.4, 4, 4.8]}
        if dealer:
            return DEALER_TABLE[discards[0].num_rank][discards[1].num_rank - 1]
        else:
            return PONE_TABLE[discards[0].num_rank][discards[1].num_rank - 1]
