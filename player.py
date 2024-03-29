from hand import Hand
from card import Card
from deck import Deck
from types import SimpleNamespace
from itertools import combinations, chain
from statistics import pstdev, mean
from colorama import Style
import traceback
import copy
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
            'Enter number between 4 and 32 or press enter for random cut.', append_msg=True)
        while True:
            try:
                cut = input()
                cut = int(cut)
                if 4 <= cut <= 32:
                    return cut
                else:
                    raise ValueError
            except ValueError:
                return random.randint(4, 32)

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
        def get_suit(check_suit):
            if check_suit in SUIT_CHARS:
                return check_suit
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
            return num_rank, suit

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
    def select_discards(self, set_message, dealer, opponent_score, num_cards=2, opponent='Opponent'):
        # Update UI
        if num_cards == 2:
            cards_text = 'two cards'
        else:
            cards_text = 'one card'
        base_messages = ['You can use the numbers 2-10 as well as the letters A, T, J, Q, and K.',
                         '',
                         'If you want to specify, you can include the first letter of the suit:',
                         Card.SPADES + ', ' + Card.HEARTS + ', ' + Card.CLUBS + ', or ' + Card.DIAMONDS,
                         '',
                         'If you don\'t care which suit is discarded, you don\'t need to include it.']
        if dealer:
            set_message(
                Style.BRIGHT + 'Your deal.' + Style.RESET_ALL,
                'Enter ' + cards_text + ' for your crib. (Spacing between them is optional)')
        else:
            set_message(
                Style.BRIGHT + opponent + '\'s deal.' + Style.RESET_ALL,
                'Enter ' + cards_text + ' for ' + opponent.lower() + '\'s crib. (Spacing is optional)')
        set_message(*base_messages, append_msg=True)
        discards = []
        while True:
            try:
                discard_input = self.get_card_input(num_cards)
                if num_cards == 1:
                    discard_input = [discard_input]
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
                            'Invalid input. Enter ' + cards_text + ' for your crib. (Spacing is optional)']
                else:
                    msgs = [Style.BRIGHT + opponent + '\'s deal.' + Style.RESET_ALL,
                            Style.BRIGHT + 'Invalid input.' + Style.RESET_ALL +
                            ' Enter ' + cards_text + ' for ' + opponent.lower() + '\'s crib. (Spacing is optional)']
                msgs.extend(base_messages[:4])
                msgs.extend(['', 'Example:  \'' + self.hand.cards[0].rank + self.hand.cards[0].suit + self.hand.cards[
                    -1].rank + '\' for ' + str(
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
                         'You can use the numbers 2-10 as well as the letters A, T, J, Q, and K.', '',
                         'Available cards: ' + str(available_cards)]
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
                        # Make sure the card they entered exists in our hand and is a legal play
                        if discard_input[0] in [card.num_rank for card in available_cards.cards] and \
                                Card(discard_input[0]).value + pegging_count <= 31:
                            return discard_input[0]
                        else:
                            raise ValueError
                    except (ValueError, IndexError):
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
        self.known_cards = []

    @staticmethod
    def cut_deck(*args):
        return random.randint(4, 32)

    def print_message(self, *message):
        if self.verbose:
            print(*message)

    # Selects and returns a list of the discards and removes them from its Hand object
    def select_discards(self, set_message, dealer, opponent_score, num_cards=2):
        # Get best discards, sorted by highest expected net points
        best_discards = self.get_best_discards(dealer)
        # Play more recklessly if justified by the score
        # The dealer scores 16 points on average betwixt pegging, hand, and crib
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
        self.known_cards = copy.copy(discard)
        self.hand.cards = [card for card in self.hand.cards if card not in discard]
        return discard

    def get_peg_play(self, set_message, available_cards, pegging_count, opponent_go, played_cards):
        # Get remaining cards in the deck. All cards played or seen so far are excluded
        excluded_cards = list(chain(list(chain(*played_cards)), self.known_cards, self.hand.cards, [self.hand.upcard]))
        deck = Deck()
        remaining_cards = {i: 0 for i in range(1, 14)}
        # Suit doesn't matter, so convert the list of cards to a frequency distribution for easier processing
        for card in deck.cards:
            if card not in excluded_cards:
                remaining_cards[card.num_rank] += 1
        # A card is considered playable if its counting value plus the current count doesn't exceed 31
        playable_cards = [card for card in available_cards.cards if card.value + pegging_count <= 31]
        opponent_hand_size = 8 - len(list(chain(*played_cards))) - len(available_cards.cards)
        self.print_message('playable', ' '.join(str(card) for card in playable_cards))
        self.print_message('played so far this round', ' '.join(str(card) for card in played_cards[-1]), '\n--------\n')
        self.print_message('remaining', remaining_cards)
        # If no cards are playable, return -1 for a go
        if len(playable_cards) == 0:
            return -1
        # If only one card is playable then there's no sense analyzing it
        elif len(playable_cards) == 1:
            return playable_cards[0].num_rank
        # Assign a weight to each playable card based on various factors if more than one is playable
        else:
            play_weights = self.get_pegging_weights(playable_cards, played_cards, remaining_cards, pegging_count,
                                                    opponent_hand_size)
            # Make the best play on hard difficulty
            if self.difficulty == 3:
                return_index = 0
            # Make a decent play on medium difficulty
            elif self.difficulty == 2:
                # This is safe because we never have list of play weights with a length less than 2
                return_index = random.randint(0, 1)
            # Play whatever feels groovy on easy difficulty
            else:
                return_index = random.randrange(0, len(play_weights))
            return play_weights[return_index].num_rank

    def get_pegging_weights(self, playable_cards, played_cards, remaining_cards, pegging_count, opponent_hand_size):
        # Get the cards played so far this round
        round_cards = played_cards[-1]
        self.print_message('opponent hand size', opponent_hand_size, '\n')

        # Calculate probability that opponent has a particular card
        def opponent_card_probability(card, by_value=False):
            total_remaining_cards = sum(remaining_cards.values())
            if card.num_rank < 10 or not by_value:
                num_cards_remaining = remaining_cards[card.num_rank]
            # If calculating by value, face cards go with 10's
            else:
                num_cards_remaining = sum(remaining_cards[i] for i in range(10, 14))
            # Get the probability that any individual remaining card IS the one in question
            individual_probability = num_cards_remaining / total_remaining_cards
            # Calculate the probability that NONE of the cards in the hand are the card in question
            probability_of_none = (1 - individual_probability) ** opponent_hand_size
            # Invert it and return, since we want the probability that at least one card IS the card in question
            return 1 - probability_of_none

        # Initialize weights dictionary
        play_weights = {card: 0.0 for card in playable_cards}
        # Analyze the cards. I decided on a heuristic approach here. A brute-force approach would
        # provide marginally better results, but is very computationally expensive to do in Python
        # Also, the heuristic approach is arguably a lot more fun to write and easier to follow
        for card in playable_cards:
            self.print_message('analyzing', card)
            other_playable_cards = [other_card for other_card in playable_cards if other_card is not card]
            new_count = pegging_count + card.value
            new_cards = copy.copy(round_cards)
            new_cards.append(card)
            self.print_message('new count', new_count)
            self.print_message('new cards', ' '.join(str(other_card) for other_card in new_cards), '\n')

            # Calculate opponent 15 or 31 probability, if applicable
            self.print_message('analyzing 15s and 31s')
            if new_count in range(5, 15) or new_count in range(21, 31):
                if new_count < 15:
                    needed_value = 15 - new_count
                else:
                    needed_value = 31 - new_count
                play_weights[card] -= 2 * opponent_card_probability(Card(needed_value), True)
                self.print_message('opponent 15 or 31 potential with', needed_value, play_weights[card])

            # Set up 15's and 31's if able
            # This is determined by checking if the value of the current count plus the value of the card plus the
            # value of ten card (the most common opponent play) is equal to 15 or 31
            if any(new_count + other_card.value + 10 in {15, 31} for other_card in other_playable_cards):
                # 2 points for 15 or 31, multiplied by the probability of the opponent playing a 10
                play_weights[card] += 2 * opponent_card_probability(Card(10), True)
                self.print_message('probability of opponent 10 card', opponent_card_probability(Card(10), True))
                self.print_message('set up for 15 or 31', play_weights[card])
            # Take counts of 15 or 31 if offered
            elif new_count in {15, 31}:
                play_weights[card] += 2
                self.print_message('15 or 31', play_weights[card])

            # Weight for a pair, pair royal, or pair double royal if offered
            self.print_message('\nanalyzing pairs')
            pair = False
            for i in range(min(len(new_cards), 4), 1, -1):
                # Check the last i cards for an i-sized pair, starting with 4 (if possible) and going down to 2
                candidate_pair = Hand(new_cards[-i:]).count_pairs(i)
                if len(candidate_pair) > 0:
                    # Weight for the number of points that will be scored
                    play_weights[card] += candidate_pair[0].points
                    self.print_message(str(i) + ' of a kind', play_weights[card])
                    # Weight for potential opponent counter (if there's room), which can't happen to a 4 of a kind
                    if i != 4 and new_count + card.value <= 31:
                        self.print_message('probability of opponent', card.rank, ' ', opponent_card_probability(card))
                        play_weights[card] -= ((i + 1) ** 2 - (i + 1)) * opponent_card_probability(card)
                        self.print_message(str(i + 1) + ' of a kind opponent counter', play_weights[card])
                    pair = True
                    break
            # If there's no pair, take potential pairs into consideration
            if not pair:
                # Account for opponent pair potential, but only if they have room to score a pair
                if new_count + card.value <= 31:
                    play_weights[card] -= 2 * opponent_card_probability(card)
                    self.print_message('opponent pair potential with', card.rank, play_weights[card])
                # If we have a pair in hand, playing one of those is a good way to get set up for a pair royal
                # The only exception is if the count is too high for us to make a pair royal
                if sum(other_card.num_rank == card.num_rank for other_card in playable_cards) > 1 and \
                        card.value * 2 + new_count <= 31:
                    play_weights[card] += 6 * opponent_card_probability(card)
                    # Note: I believe weighting for a potential opponent pair double royal is unnecessary
                    # It's incredibly unlikely and a pair royal is always the right decision to take in pegging,
                    # so I'm not worried about it compromising the integrity of the weighting
                    self.print_message('pair royal potential', play_weights[card])

            # Weight for a run
            self.print_message('\nanalyzing runs')
            if len(new_cards) >= 3:
                for i in range(len(new_cards), 2, -1):
                    candidate_run = Hand(
                        new_cards[-i:]).count_runs()
                    # Check if a run was found and that its score matches what we're looking for
                    if len(candidate_run) > 0 and candidate_run[0].points == i:
                        play_weights[card] += i
                        self.print_message(i, 'card run', play_weights[card])
                        break

            # Weight for potential opponent run
            if len(new_cards) >= 2:
                for i in range(len(new_cards) + 1, 2, -1):
                    for remaining_card_rank, num in remaining_cards.items():
                        remaining_card = Card(remaining_card_rank)
                        # Don't worry about cards that would put the count over 31
                        if remaining_card.value + new_count > 31:
                            continue
                        # Combine the new card with the currently played cards and count runs
                        hypothetical_cards = copy.copy(new_cards)
                        hypothetical_cards.append(remaining_card)
                        candidate_run = Hand(hypothetical_cards[-i:]).count_runs()
                        # Check if the given opponent play would result in a run and that it's the right size
                        if len(candidate_run) > 0 and candidate_run[0].points == len(hypothetical_cards):
                            play_weights[card] -= candidate_run[0].points * opponent_card_probability(remaining_card)
                            self.print_message('opponent', i, 'card run potential with', remaining_card, play_weights[card])
                            # If we can counter the potential run, we'll either get 1 or 0 net points
                            for other_card in other_playable_cards:
                                if other_card.value + remaining_card.value + new_count <= 31:
                                    counter_cards = copy.copy(hypothetical_cards)
                                    counter_cards.append(other_card)
                                    found_counter = False
                                    for j in range(len(counter_cards), 2, -1):
                                        counter_run = Hand(counter_cards[-j:]).count_runs()
                                        if any(run.points == j for run in counter_run):
                                            play_weights[card] += j * opponent_card_probability(remaining_card)
                                            self.print_message(j, 'card counter run', play_weights[card])
                                            found_counter = True
                                            break
                                    if found_counter:
                                        break

            # Weight for opponent and self go potential
            self.print_message('\nanalyzing gos')
            # Get the value of the smallest card in our hand
            smallest_card_value = min(other_card.value for other_card in other_playable_cards)
            self.print_message('smallest card in hand', smallest_card_value)
            # Get the value of the smallest card the opponent could play to force a go from us
            # If we'd be able to play our smallest card if the opponent said go, then the smallest card that the
            # opponent can play to force a go from us is any card such that the total count of the opponent play and
            # our response would be over 31
            if smallest_card_value + new_count <= 31:
                smallest_opponent_go_card = 32 - new_count - smallest_card_value
            # If this is the last card we could play regardless of opponent's play, then the smallest go card is an ace
            else:
                smallest_opponent_go_card = 1
            if smallest_opponent_go_card in range(1, 11) and smallest_opponent_go_card + new_count < 31:
                self.print_message('smallest card for opponent go', smallest_opponent_go_card)
                num_go_cards = 0
                self.print_message('opponent go cards ')
                for num_rank, num_remaining in remaining_cards.items():
                    opponent_card = Card(num_rank)
                    if opponent_card.value >= smallest_opponent_go_card and opponent_card.value + new_count < 31:
                        self.print_message(opponent_card)
                        num_go_cards += num_remaining
                self.print_message('')
                self.print_message('number of remaining cards', sum(remaining_cards.values()))
                self.print_message('number of go cards', num_go_cards)
                if num_go_cards > 1:
                    opponent_go_probability = (1 - num_go_cards / sum(remaining_cards.values())) ** opponent_hand_size
                    self.print_message('odds of opponent having a go card', opponent_go_probability)
                    play_weights[card] -= opponent_go_probability
                    self.print_message('opponent go potential with', smallest_opponent_go_card, '-', 30 - new_count, play_weights[card])
            # If the new count is greater than 21, weight for the odds that the opponent can't make a play
            if new_count > 21 and new_count != 31:
                # Get the value of the largest playable card that the opponent could have
                largest_opponent_playable_card = 31 - new_count
                num_playable_cards = 0
                self.print_message('opponent playable cards ')
                for num_rank, num_remaining in remaining_cards.items():
                    opponent_card = Card(num_rank)
                    if opponent_card.value <= largest_opponent_playable_card:
                        self.print_message(opponent_card)
                        num_playable_cards += num_remaining
                self.print_message('')
                self.print_message('number of remaining cards', sum(remaining_cards.values()))
                self.print_message('total playable cards', num_playable_cards)
                self_go_probability = 1 - (num_playable_cards / sum(remaining_cards.values()))
                self.print_message('odds of opponent not having a playable card', self_go_probability)
                play_weights[card] += self_go_probability
                self.print_message('self go potential', play_weights[card])
                # If the opponent giving us a go would result in a pair, weight accordingly
                if any(other_card.num_rank == card.num_rank for other_card in other_playable_cards if
                       other_card.value + new_count <= 31):
                    play_weights[card] += 2 * self_go_probability
                    self.print_message('pair potential if opponent says go', play_weights[card])
                # If the opponent giving us a go would result in a 31, weight accordingly
                if any(other_card.value + new_count == 31 for other_card in other_playable_cards):
                    play_weights[card] += 2 * self_go_probability
                    self.print_message('31 potential if opponent says go', play_weights[card])

            self.print_message('\n-----------\n')
        # All else being equal, play the highest card
        if any(other_playable_card.num_rank == card.num_rank for other_playable_card in other_playable_cards):
            max_weight = max(play_weights.values())
            highest_card = max([high_card for high_card in play_weights.keys() if play_weights[high_card] == max_weight])
            play_weights[highest_card] += 0.01
            self.print_message('high card tiebreaker adds 0.01 to', highest_card)
        self.print_message('play weights:')
        for weight in play_weights.items():
            self.print_message(str(weight[0]), weight[1])
        return sorted(play_weights, key=play_weights.get, reverse=True)

    # Analyze a hand of 5 or 6 cards and determine the mathematically optimal discards
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
        if len(discards) == 2:
            if dealer:
                return DEALER_TABLE[discards[0].num_rank][discards[1].num_rank - 1]
            else:
                return PONE_TABLE[discards[0].num_rank][discards[1].num_rank - 1]
        else:
            # If only discarding one card, use the average value of the applicable row in the table
            if dealer:
                return sum(DEALER_TABLE[discards[0].num_rank]) / len(DEALER_TABLE[discards[0].num_rank])
            else:
                return sum(PONE_TABLE[discards[0].num_rank]) / len(PONE_TABLE[discards[0].num_rank])
