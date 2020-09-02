class Score:
    def __init__(self, cards, points):
        self.cards = frozenset(cards)
        self.points = points

    def __str__(self):
        return ' '.join(str(card) for card in sorted(self.cards, key=lambda card: card.num_rank))

    def __hash__(self):
        return hash(self.cards) ^ hash(self.points)
