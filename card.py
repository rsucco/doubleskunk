class Card:
    def __init__(self, rank='0', value=0, suit='0'):
        self.rank = rank
        self.value = value
        self.suit = suit

    def __str__(self):
        return self.rank + self.suit

    # Equality is determined by rank and suit
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))
