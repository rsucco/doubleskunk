from card import Card
import random


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    # Instantiate a standard 52-card deck
    def reset(self):
        self.cards = []
        for num_rank in range(1, 14):
            for suit in ['c', 's', 'h', 'd']:
                card = Card(num_rank, suit)
                self.cards.append(card)

    # Shuffle the deck
    def shuffle(self):
        random.shuffle(self.cards)

    # Deal card(s) from the deck
    def deal_card(self, num=1):
        deal_cards = self.cards[0:num]
        self.cards = self.cards[num:]
        return deal_cards
