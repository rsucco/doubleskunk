from card import Card
from score import Score
from deck import Deck
from itertools import chain, combinations
from statistics import mean, pstdev
from sys import maxsize
import copy


class Hand:
    def __init__(self, cards=[], is_crib=False, upcard=Card()):
        self.cards = cards
        self.upcard = upcard
        self.is_crib = is_crib

    def __str__(self):
        return ' '.join(str(card) for card in sorted(self.cards, key=lambda card: card.num_rank) if card.num_rank != 0)

    def __copy__(self):
        return Hand(copy.copy(self.cards), copy.copy(self.upcard), self.is_crib)

    # Return all of the cards of the hand plus the upcard as a single list of Cards
    def allCards(self):
        # Make sure the upcard has been set before returning it. Otherwise just return self.cards
        if self.upcard.suit != '0':
            return chain(self.cards, [self.upcard])
        else:
            return self.cards

    # Removes and returns a specified card from the hand
    # Raises an exception if the card doesn't exist in the hand
    def discard(self, num_rank, suit='0'):
        for card in self.cards:
            # Rank needs to match. Suit only needs to match if specified
            if num_rank == card.num_rank and (suit == '0' or suit == card.suit):
                self.cards.remove(card)
                return card
        raise Exception(str(num_rank) + ' of ' +
                        suit + ' does not exist in hand.')

    # Each distinct combination of cards that adds up to 15 is worth 2 points
    def count_15s(self):
        fifteens = set()
        # Check every unique combination of cards to see if they sum to 15
        for i in range(2, 6):
            card_combos = combinations(self.allCards(), i)
            for combo in card_combos:
                if sum((card.value for card in combo)) == 15:
                    # Store the combination as a Score object
                    fifteens.add(Score(combo, 2))
        return fifteens

    # A pair is 2 of a kind for 2 points
    def count_pairs(self, pair_size=2, exclude_duplicates=True):
        pairs = set()
        # Pair royal is 3 of a kind for 6 points
        if pair_size == 3:
            points = 6
        # Pair double royal is 4 of a kind for 12
        elif pair_size == 4:
            points = 12
        # Boring old normal pair
        else:
            points = 2
        # Iterate through every combination of two cards. If they match, they're a pair
        card_combos = combinations(self.allCards(), pair_size)
        for combo in card_combos:
            # All cards in the combo must be the same rank
            # Don't bother checking for partial duplicates if told not to or if it's a four of a kind
            # Otherwise, make sure that the total number of cards in the hand of the pair's rank is the same as the size of the combo
            if all([card.rank == combo[0].rank for card in combo]) and \
                    (not exclude_duplicates or pair_size == 4 or sum([card.rank == combo[0].rank for card in self.allCards()]) == pair_size):
                pairs.add(Score(combo, points))
        return pairs

    # A run is 3 to 5 cards where the numerical ranks of the cards occur in sequence
    def count_runs(self):
        runs = set()
        for i in range(len(list(self.allCards())), 2, -1):
            card_combos = list(combinations(self.allCards(), i))
            for combo in card_combos:
                # Sort the combination of cards based on numerical rank
                sorted_combo = sorted(combo, key=lambda card: card.num_rank)
                # If it's a run, every card will be followed by the next card in the list, with the obvious exception of the last card
                if all((sorted_combo[j + 1].follows(sorted_combo[j]) for j in range(len(sorted_combo) - 1))):
                    run = Score(sorted_combo, i)
                    # Make sure the run isn't a partial copy of a longer run
                    # There's no point in checking if there aren't any other runs yet
                    if len(runs) == 0 or not any((run.cards.issubset(other_run.cards) for other_run in runs)):
                        runs.add(run)
        return runs

    # A flush is five cards in the same suit (in the hand or the crib) or four cards not including the upcard (in the hand only)
    def count_flush(self):
        flush = []
        flush_suit = self.cards[0].suit
        # If any card is a different suit than the first one, there can't be a flush
        for card in self.cards:
            if card.suit != flush_suit:
                return flush
        # Five card flush if the upcard also matches
        if self.upcard.suit == flush_suit:
            flush = [Score(self.allCards(), 5)]
        # Four card flushes can't be scored in a crib
        if not self.is_crib:
            flush = [Score(self.cards, 4)]
        return flush

    # 'His nibs', or 'a jack' is a jack in the hand of the same suit as the upcard. This can stack with a flush.
    def count_nibs(self):
        for card in self.cards:
            if card.rank == 'J' and card.suit == self.upcard.suit:
                return [Score((card, self.upcard), 1)]
        return []

    # Analyze a hand of 6 cards and determine the mathematically optimal discards
    # TODO Move this to AIPlayer
    def best_discard(self, dealer=True, verbose=False):
        if len(self.cards) <= 5:
            raise Exception("Can only analyze best discard for 6-card hands")
        # Create a Deck object to represent all the potential upcards
        deck_remainder = Deck()
        deck_remainder.cards = [
            card for card in deck_remainder.cards if card not in self.cards]
        # Two cards must be discarded, leaving us with a 4-card hand to be analyzed
        potential_hands = list(Hand(hand)
                               for hand in combinations(self.cards, 4))

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
                card for card in self.cards if card not in hand.cards]
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
            hand_info['min'] = [(Card(), maxsize)]
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

        # Print some info if requested
        if verbose:
            for hand in all_hands:
                print('Discard:', str(Hand(hand['discard'])))
                print('Your hand:', hand['hand'])
                if dealer:
                    net_points_str = 'Expected net points (including potential points in your crib): '
                    crib_points_str = 'Expected value of your crib: '
                else:
                    net_points_str = 'Expected net points (including points against you given to opponent\'s crib): '
                    crib_points_str = 'Expected value of opponent\'s crib: '
                print(net_points_str + '{:.2f}'.format(hand['net_points']))
                print('Expected value of your hand: ' +
                      '{:.2f}'.format(hand['avg']))
                print(crib_points_str + str(hand['crib_points']))
                # Do some string manipulation to make the max and min points look snazzy
                max_cards = ', '.join([str(card[0]) for card in hand['max']])
                max_hit_odds = '(' + \
                    '{:.2f}'.format(len(hand['max']) / 46 * 100) + '% odds)'
                print('Maximum possible points for your hand (with ' +
                      max_cards + '):', hand['max'][0][1], max_hit_odds)
                min_cards = ', '.join([str(card[0]) for card in hand['min']])
                min_hit_odds = '(' + \
                    '{:.2f}'.format(len(hand['min']) / 46 * 100) + '% odds)'
                print('Minimum possible points for your hand (with ' +
                      min_cards + '):', hand['min'][0][1], min_hit_odds)
                print('Standard deviation of your hand\'s expected score (the higher the number, the greater the variance): ' +
                      '{:.2f}'.format(hand['std_dev']))
                print('\n--------\n')

        # Return the list of discards
        return all_hands

    # Determine the expected number of points that a given discard will give to the crib
    # For now, this is implemented via a lookup table created from publically available data
    # If I can ever figure out a way to calculate it dynamically myself without an unacceptable performance hit, I'll do so
    # For now, this will have to do
    def expected_crib_points(self, discards, dealer=True):
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
