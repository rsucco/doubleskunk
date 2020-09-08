from colorama import Fore, Back, Style


class Card:
    SPADES = str(f'{Fore.LIGHTYELLOW_EX}[s]pades ♠{Style.RESET_ALL}')
    HEARTS = str(f'{Fore.RED}[h]earts ♥{Style.RESET_ALL}')
    CLUBS = str(f'{Fore.GREEN}[c]lubs ♣{Style.RESET_ALL}')
    DIAMONDS = str(f'{Fore.BLUE}[d]iamonds ♦{Style.RESET_ALL}')

    def __init__(self, num_rank=0, suit='0'):
        self.num_rank = num_rank
        self.suit = suit
        # Give the correct rank to ace, jack, queen, and king
        if num_rank == 1:
            self.rank = 'A'
        elif num_rank == 11:
            self.rank = 'J'
        elif num_rank == 12:
            self.rank = 'Q'
        elif num_rank == 13:
            self.rank = 'K'
        else:
            self.rank = str(num_rank)
        # Face cards still only count as 10 points
        if num_rank > 10:
            self.value = 10
        else:
            self.value = num_rank

    # String representation should be snazzy, and str should only be used for terminal UI stuff
    def __str__(self):
        # Spades yellow, hearts red, clubs green, diamonds blue
        card_str = ''
        if self.suit == 's':
            card_str = str(
                f'{Fore.LIGHTYELLOW_EX}{self.rank}♠{Style.RESET_ALL}')
        elif self.suit == 'h':
            card_str = str(
                f'{Fore.RED}{self.rank}♥{Style.RESET_ALL}')
        elif self.suit == 'c':
            card_str = str(
                f'{Fore.GREEN}{self.rank}♣{Style.RESET_ALL}')
        elif self.suit == 'd':
            card_str = str(
                f'{Fore.BLUE}{self.rank}♦{Style.RESET_ALL}')
        return card_str

    # Equality is determined by rank and suit
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    # Less than is determined by rank
    def __lt__(self, other):
        return self.num_rank() < other.num_rank()

    # Rank and suit are enough to make the object unique
    def __hash__(self):
        return hash((self.rank, self.suit))

    def __copy__(self):
        return Card(self.num_rank, self.suit)

    def follows(self, other):
        if self.num_rank == other.num_rank + 1:
            return True
        else:
            return False
