from card import Card
from typing import Dict, List
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

    # Deal two 6-card hands or three 5-card hands
    def deal_hands(self, num_players):
        if num_players == 2:
            hands = [self.cards[:12:2], self.cards[1:13:2]]
            self.cards = self.cards[12:]
        elif num_players == 3:
            hands = [self.cards[:13:3], self.cards[1:14:3], self.cards[2:15:3]]
            self.cards = self.cards[15:]
        return hands

    # Deal one card (for three-player cribs)
    def deal_card(self):
        return self.cards.pop(0)
