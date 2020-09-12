from src.doubleskunk.card import Card
from src.doubleskunk.score import Score
from itertools import chain, combinations
import copy


class Hand:
    def __init__(self, cards=None, is_crib=False, upcard=Card()):
        if cards is None:
            cards = []
        self.cards = cards
        self.upcard = upcard
        self.is_crib = is_crib

    def __str__(self):
        return ' '.join(str(card) for card in sorted(self.cards, key=lambda card: card.num_rank) if card.num_rank != 0)

    def __copy__(self):
        return Hand(copy.copy(self.cards), self.is_crib, copy.copy(self.upcard))

    # Return all of the cards of the hand plus the upcard as a single list of Cards
    def all_cards(self):
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

    # Count the entire hand and return just the score
    def count(self):
        count_methods = [self.count_15s, lambda: self.count_pairs(2), lambda: self.count_pairs(3),
                         lambda: self.count_pairs(4), self.count_runs, self.count_flush, self.count_nibs]
        scores = []
        for method in count_methods:
            results = method()
            if len(results) > 0:
                scores.extend(results)
        if len(scores) > 0:
            return sum([score.points for score in scores])
        else:
            return 0

    # Each distinct combination of cards that adds up to 15 is worth 2 points
    def count_15s(self):
        fifteens = set()
        # Check every unique combination of cards to see if they sum to 15
        for i in range(2, 6):
            card_combos = combinations(self.all_cards(), i)
            for combo in card_combos:
                if sum((card.value for card in combo)) == 15:
                    # Store the combination as a Score object
                    fifteens.add(Score(combo, 2))
        return fifteens

    # A pair is 2 of a kind for 2 points
    def count_pairs(self, pair_size=2, exclude_duplicates=True):
        pairs = set()
        # 2 of a kind for 2, 3 of a kind for 6, 4 of a kind for 12
        points = pair_size ** 2 - pair_size
        # Iterate through every combination of two cards. If they match, they're a pair
        card_combos = combinations(self.all_cards(), pair_size)
        for combo in card_combos:
            # All cards in the combo must be the same rank
            # Don't bother checking for partial duplicates if told not to or if it's a four of a kind
            # Otherwise, make sure that the total number of cards in the hand of the pair's rank is the same as the size of the combo
            if all([card.rank == combo[0].rank for card in combo]) and \
                    (not exclude_duplicates or pair_size == 4 or sum([card.rank == combo[0].rank for card in self.all_cards()]) == pair_size):
                pairs.add(Score(combo, points))
        return list(pairs)

    # A run is 3 to 5 cards where the numerical ranks of the cards occur in sequence
    def count_runs(self):
        runs = set()
        for i in range(len(list(self.all_cards())), 2, -1):
            card_combos = list(combinations(self.all_cards(), i))
            for combo in card_combos:
                # Sort the combination of cards based on numerical rank
                sorted_combo = sorted(combo, key=lambda card: card.num_rank)
                # If it's a run, every card will be followed by the next card in the list,
                # with the obvious exception of the last card
                if all((sorted_combo[j + 1].follows(sorted_combo[j]) for j in range(len(sorted_combo) - 1))):
                    run = Score(sorted_combo, i)
                    # Make sure the run isn't a partial copy of a longer run
                    # There's no point in checking if there aren't any other runs yet
                    if len(runs) == 0 or not any((run.cards.issubset(other_run.cards) for other_run in runs)):
                        runs.add(run)
        return list(runs)

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
            flush = [Score(self.all_cards(), 5)]
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
