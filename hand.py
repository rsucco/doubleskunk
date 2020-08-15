from card import Card
from itertools import chain


class Hand:
    def __init__(self, cards=None, is_crib=False):
        self.cards = []
        self.upcard = Card()
        self.is_crib = is_crib
        for card in cards:
            self.cards.append(card)

    def draw_card(self, card):
        self.cards.append(card)

    def count(self, verbose=False):
        return

    def count_15s(self, verbose=False):
        return

    # A pair is 2 of a kind for 2 points, pair royal is 3 of a kind of 6 points, and pair double royal is 4 of a kind for 12
    def count_pairs(self, verbose=False):
        pairs = {}
        score = 0
        # Check each card against each other card. If the ranks match, they're a pair
        for card in chain(self.cards, [self.upcard]):
            for match_card in chain(self.cards, [self.upcard]):
                if match_card != card and match_card.rank == card.rank:
                    # Track the number of cards in each pair separately to determine pairs royal and double royal
                    if card.rank not in pairs:
                        pairs[card.rank] = set()
                    # Update the set to avoid counting the same card multiple times
                    pairs[card.rank].update((card, match_card))
        for pair in pairs.items():
            num_cards = len(pair[1])  # 2/3/4 of a kind
            if num_cards == 2:
                if verbose:
                    print("Pair of " + pair[0] + "'s for 2:")
                score += 2
            elif num_cards == 3:
                if verbose:
                    print("Pair royal of " + pair[0] + "'s for 6:")
                score += 6
            elif num_cards == 4:
                if verbose:
                    print("Double pair royal of " + pair[0] + "'s for 12:")
                score += 12
            if verbose:
                print(', '.join(str(card) for card in pair[1]))
        return score

    def count_runs(self, verbose=False):
        return

    # A flush is five cards in the same suit (in the hand or the crib) or four cards not including the upcard (in the hand only)
    def count_flush(self, verbose=False):
        flush_suit = self.cards[0].suit
        # If any card is a different suit than the first one, there can't be a flush
        for card in self.cards:
            if card.suit != flush_suit:
                if verbose:
                    print("No flush")
                return 0
        # Five card flush if the upcard also matches
        if self.upcard.suit == flush_suit:
            if verbose:
                print("5 card flush for 5:")
                print(', '.join(str(card)
                                for card in chain(self.cards, [self.upcard])))
            return 5
        # Four card flushes can't be scored in a crib
        if not self.is_crib:
            if verbose:
                print("4 card flush for 4:")
                for card in self.cards:
                    print(card, end=" ")
                print("")
            return 4
        else:
            if verbose:
                print("No flush")
            return 0

    # 'His nibs', or 'a jack' is a jack in the hand of the same suit as the upcard. This can stack with a flush.
    def count_nibs(self, verbose=False):
        for card in self.cards:
            if card.rank == 'J' and card.suit == self.upcard.suit:
                if verbose:
                    print("Nibs for 1:")
                    print(card, self.upcard)
                return 1
        if verbose:
            print("No nibs")
        return 0
