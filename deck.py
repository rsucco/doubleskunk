from card import Card
import random


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    # Instantiate a standard 52-card deck
    def reset(self):
        self.cards = []
        for value in range(1, 14):
            # Give the correct rank to ace, jack, queen, and king
            if value == 1:
                rank = 'A'
            elif value == 11:
                rank = "J"
            elif value == 12:
                rank = "Q"
            elif value == 13:
                rank = "K"
            else:
                rank = str(value)
            # Face cards still only count as 10 points
            if value > 10:
                value = 10
            for suit in ['c', 's', 'h', 'd']:
                card = Card(rank, value, suit)
                self.cards.append(card)

    # Shuffle the deck
    def shuffle(self):
        random.shuffle(self.cards)

    # Deal card(s) from the deck
    def deal_card(self, num=1):
        deal_cards = self.cards[0:num]
        self.cards = self.cards[num:]
        return deal_cards
