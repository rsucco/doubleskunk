from hand import Hand
import random


# Base Player class
class Player:
    def __init__(self):
        self.score = 0
        self.last_score = -1
        self.hand = Hand()

    def peg_at(self, num):
        if self.last_score == num or self.score == num:
            return True
        return False

    # Increase score and set last_score
    def add_points(self, points):
        self.last_score = self.score
        self.score += points


# Class for human player
class HumanPlayer(Player):
    def __init__(self):
        super().__init__()

    def cut_deck(self):
        while True:
            try:
                cut = input()
                cut = int(cut)
                if cut >= 4 and cut <= 36:
                    return cut
                else:
                    raise Exception
            except Exception:
                return random.randint(4, 36)

    def select_discards(self):
        input()
        discards = [self.hand.cards[0], self.hand.cards[1]]
        return discards


# Class for AI player
class AIPlayer(Player):
    def __init__(self):
        super().__init__()

    def cut_deck(self):
        return random.randint(4, 36)

    def select_discards(self):
        discards = [self.hand.cards[0], self.hand.cards[1]]
        return discards
