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

    # Deal two 6-card hands properly
    def deal_hands(self) -> Dict[str, List[Card]]:
        hands = {'dealer': self.cards[:12:2], 'pone': self.cards[1:13:2]}
        self.cards = self.cards[12:]
        return hands
