from sys import exit
from card import Card
from score import Score
from deck import Deck
from hand import Hand
from player import Player, HumanPlayer, AIPlayer
from colorama import Fore, Back, Style, init
from os import system, name
from re import compile
from time import sleep
import traceback


class Game:
    SPADES = str(f'{Fore.LIGHTYELLOW_EX}[s]pades ♠{Style.RESET_ALL}')
    HEARTS = str(f'{Fore.RED}[h]earts ♥{Style.RESET_ALL}')
    CLUBS = str(f'{Fore.GREEN}[c]lubs ♣{Style.RESET_ALL}')
    DIAMONDS = str(f'{Fore.BLUE}[d]iamonds ♦{Style.RESET_ALL}')
    BOARD_SPACE = Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + ' '

    # Subclass for printing messages containing unicode characters with correct space justification
    class Message:
        def __init__(self, message=''):
            self.message = message
            self.length = len(message)

        def bare_str(self):
            # Regex to strip color formatting
            REGEX = compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
            bare_str = REGEX.sub('', self.message)
            # Convert to ASCII to get rid of the unicode characters
            bare_str = bare_str.encode('ascii', errors='replace')
            return bare_str

        # Generate string left justified, taking ANSI codes and unicode into account
        def ljust(self, width):
            padded_str = self.message
            if len(self.bare_str()) < width:
                for i in range(width - len(self.bare_str()) - 2):
                    padded_str += ' '
            return padded_str

        # Generate string centered, taking ANSI codes and unicode into account
        def center(self, width):
            padded_str = self.message
            if len(self.bare_str()) < width:
                # Handle odd numbers
                if (width - len(self.bare_str())) % 2 != 0:
                    padded_str += ' '
                else:
                    padded_str = ' ' + padded_str + ' '
                for i in range(0, width - len(self.bare_str()) - 2, 2):
                    padded_str = ' ' + padded_str + ' '
            return padded_str

    def __init__(self, num_players=1, difficulty=3, debug=False):
        # Initialize colorama to enable styled terminal output on Windows
        init()
        # 2-person games and 2-AI games are only for testing right now
        if num_players == 0:
            self.player1 = AIPlayer(difficulty)
            self.player2 = AIPlayer(difficulty)
        elif num_players == 1:
            self.player1 = HumanPlayer()
            self.player2 = AIPlayer(difficulty, debug)
        elif num_players == 2:
            self.player1 = HumanPlayer()
            self.player2 = HumanPlayer()
        self.difficulty = difficulty
        self.messages = [self.Message()]
        self.debug = debug
        self.deck = Deck()
        self.crib = Hand()
        self.upcard = Card()

    # Clear the screen with the appropriate terminal command for the system
    def clear(self):
        # Don't clear the screen in debug mode. This helps with debugging because it enables scrollback to see snapshots of game state change
        if not self.debug:
            if name == 'nt':
                system('cls')
            else:
                system('clear')

    # Render the top of a score section
    def render_board_top(self, starting_point=1):
        render_str = Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK
        if starting_point == 1:
            render_str += '  ╓────╖  '
        else:
            render_str += '  ╓─────╖ '
        for i in range(60):
            if i == 0:
                render_str += '╓'
            elif i == 59:
                render_str += '────╖  '
            elif i % 5 == 0:
                render_str += '──╥'
            else:
                render_str += '──'
        render_str += Style.RESET_ALL
        return render_str

    # Render the bottom of a score section
    def render_board_bottom(self, starting_point=1):
        render_str = Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK
        if starting_point == 1:
            render_str += '  ╙────╜  '
        else:
            render_str += '  ╙─────╜ '
        for i in range(60):
            if i == 0:
                render_str += '╙'
            elif i == 59:
                render_str += '────╜  '
            elif i % 5 == 0:
                render_str += '──╨'
            else:
                render_str += '──'
        render_str += Style.RESET_ALL
        return render_str

    # Render a hole with or without a peg for a given score number and player
    def render_board_hole(self, score, player=None):
        # Hole 121 needs special handling since either player's peg can go there
        if score == 121:
            if self.player1.peg_at(121):
                return Style.RESET_ALL + Style.DIM + \
                    Back.LIGHTYELLOW_EX + Style.BRIGHT + Fore.BLACK + '⬤ ' + Style.RESET_ALL
            elif self.player2.peg_at(121):
                return Style.RESET_ALL + Style.DIM + \
                    Back.LIGHTYELLOW_EX + Style.BRIGHT + Fore.WHITE + '⬤ ' + Style.RESET_ALL
            else:
                return Style.RESET_ALL + Style.DIM + Back.LIGHTYELLOW_EX + Style.BRIGHT + Fore.BLACK + '⭕' + Style.RESET_ALL
        # Proper background colors for
        if player == self.player1:
            render_str = Style.RESET_ALL + Style.DIM + \
                Back.LIGHTRED_EX + Style.BRIGHT + Fore.BLACK
        elif player == self.player2:
            render_str = Style.RESET_ALL + Style.DIM + \
                Back.LIGHTGREEN_EX + Style.BRIGHT + Fore.WHITE
        else:
            render_str = Style.RESET_ALL + Style.DIM + Back.LIGHTYELLOW_EX
        if player.peg_at(score):
            render_str += '⬤ ' + Style.RESET_ALL
        else:
            render_str += Style.BRIGHT + Fore.BLACK + '⭕' + Style.RESET_ALL
        return render_str

    # Render the score section of the board
    def render_board_score(self, starting_point=1):
        # Verticle separator character constant
        VERT = Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + '║'
        # Separate strings for each line of the score
        render_strs = [self.BOARD_SPACE * 2,
                       self.BOARD_SPACE * 2, self.BOARD_SPACE * 2]

        # Render holes -1 through 60
        if starting_point == 1:
            # Render the starting line
            render_strs[0] += VERT
            render_strs[1] += Style.BRIGHT + \
                Back.LIGHTYELLOW_EX + Fore.BLACK + '╠════╣  '
            render_strs[2] += VERT
            for i in [-1, 0]:
                render_strs[0] += self.render_board_hole(i, self.player1)
                render_strs[2] += self.render_board_hole(i, self.player2)
            render_strs[0] += Style.BRIGHT + \
                Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + '║  '
            render_strs[2] += Style.BRIGHT + \
                Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + '║  '
            # Render the scores
            for i in range(1, 61):
                # Left side
                if i == 1:
                    render_strs[0] += '║'
                    render_strs[1] += '╠'
                    render_strs[2] += '║'
                render_strs[0] += self.render_board_hole(i, self.player1)
                render_strs[1] += '══'
                render_strs[2] += self.render_board_hole(i, self.player2)
                # Right side
                if i == 60:
                    render_strs[0] += VERT + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                    render_strs[1] += '╣' + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                    render_strs[2] += VERT + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                # Separators
                elif i % 5 == 0:
                    render_strs[0] += VERT
                    render_strs[1] += '╬'
                    render_strs[2] += VERT

        # Render holes 61-121
        else:
            # Render the finish line
            render_strs[0] += Style.BRIGHT + \
                Back.LIGHTYELLOW_EX + Fore.BLACK + '║     ║ '
            render_strs[1] += Style.BRIGHT + Back.LIGHTYELLOW_EX + Fore.BLACK + '║  ' + \
                self.render_board_hole(121) + \
                Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + ' ║ '
            render_strs[2] += Style.BRIGHT + \
                Back.LIGHTYELLOW_EX + Fore.BLACK + '║     ║ '
            # Render the scores
            for i in range(119, 59, -1):
                if i == 119:
                    render_strs[0] += '║'
                    render_strs[1] += '╠'
                    render_strs[2] += '║'
                render_strs[0] += self.render_board_hole(i, self.player1)
                render_strs[1] += '══'
                render_strs[2] += self.render_board_hole(i, self.player2)
                # Right side
                if i == 60:
                    render_strs[0] += VERT + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                    render_strs[1] += '╣' + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                    render_strs[2] += VERT + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                # Left side
                elif i == 90:
                    render_strs[0] += VERT
                    render_strs[1] += 'S'
                    render_strs[2] += VERT
                # Vertical separators
                elif i % 5 == 0:
                    render_strs[0] += VERT
                    render_strs[1] += '╬'
                    render_strs[2] += VERT
        return render_strs

    def render_ui_messages(self, messages, width=80, margin_left=10):
        render_strs = []
        render_strs.append(
            ' ' * margin_left + '╓' + '─' * (width) + '╖')
        for message in messages:
            render_strs.append(' ' * margin_left + '║ ' +
                               message.ljust(width) + ' ║')
        render_strs.append(
            ' ' * margin_left + '╙' + '─' * (width) + '╜')
        return render_strs

    def render_ui_hand(self, render_strs, player=1, width=25, margin_left=35):
        if player == 1:
            padded_hand = self.Message(str(self.player1.hand))
        render_strs[0] += ' ' * margin_left + '╓' + '─' * (width) + '╖'
        render_strs[1] += ' ' * margin_left + '║' + \
            'Your hand'.center(width) + '║'
        render_strs[2] += ' ' * margin_left + '║' + \
            padded_hand.center(width) + '║'
        render_strs[3] += ' ' * margin_left + '╙' + '─' * (width) + '╜'
        return render_strs

    def render_ui_upcard(self, render_strs):
        render_strs[0] += '     ╓────────╖'
        render_strs[1] += '     ║ Upcard ║'
        render_strs[2] += '     ║' + \
            self.Message(str(self.upcard)).center(8) + '║'
        render_strs[3] += '     ╙────────╜'
        return render_strs

    def render_ui_score(self, render_strs, player):
        render_strs[0] += '     ╓──────────╖'
        if player == 1:
            render_strs[1] += '     ║Your Score║'
            render_strs[2] += '     ║   ' + \
                str(self.player1.score).center(5) + '  ║'
        else:
            render_strs[1] += '     ║ AI Score ║'
            render_strs[2] += '     ║   ' + \
                str(self.player2.score).center(5) + '  ║'
        render_strs[3] += '     ╙──────────╜'
        return render_strs

    # Draw the board based on current scores
    def draw_board(self):
        print()
        # Row 1
        print(Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK +
              '          0                    10                    20                    30                    40                    50                    60  ' + Style.RESET_ALL)
        print(self.render_board_top(1))
        for score_str in self.render_board_score(1):
            print(score_str)
        print(self.render_board_bottom(1))

        # Row 2
        print(self.render_board_top(61))
        for score_str in self.render_board_score(61):
            print(f'{score_str}')
        print(self.render_board_bottom(61))
        print(Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK +
              '         120                   110                   100                   90                    80                    70                    60  ' + Style.RESET_ALL)

    # Draw the informational UI
    def draw_ui(self):
        print()
        render_strs = ['', '', '', '']
        render_strs = self.render_ui_hand(render_strs)
        render_strs = self.render_ui_upcard(render_strs)
        render_strs = self.render_ui_score(render_strs, 1)
        render_strs = self.render_ui_score(render_strs, 2)
        for render_str in render_strs:
            print(render_str)
        render_strs = self.render_ui_messages(self.messages, 103, 20)
        for render_str in render_strs:
            print(render_str)

    # Draw the game interface
    def draw_game(self):
        self.clear()
        self.draw_board()
        self.draw_ui()
        if self.debug:
            debug_msg = []
            print('\n--------------\nDEBUG:')
            print('WHOLE DECK:')
            print(Hand(self.deck.cards))
            print('OPPONENT HAND:')
            print(self.player2.hand)
            print('CRIB:')
            print(self.crib)

    def set_message(self, *messages):
        self.messages = list(self.Message(message) for message in messages)
        self.draw_game()

    # Have both players cut to determine who deals (low card deals)
    def get_dealer(self):
        self.set_message('Cut to determine dealer. Low card deals; ace is low.',
                         'Enter number between 4 and 36 or press enter for random cut.')
        # Keep cutting until we have a winner
        while True:
            self.deck.shuffle()
            p1_cut = self.deck.cards[self.player1.cut_deck()]
            p2_cut = p1_cut
            # Make sure they don't accidentally cut the exact same card
            # TODO Fix this to have player 2 cut the remainder of the deck after player 1's cut rather than cutting the entire deck twice
            while p2_cut == p1_cut:
                p2_cut = self.deck.cards[self.player2.cut_deck()]
            cut_message = 'Player 1 cuts ' + \
                str(p1_cut) + '. Player 2 cuts ' + str(p2_cut) + '.'
            if p1_cut.num_rank < p2_cut.num_rank:
                self.set_message(
                    cut_message, 'Player 1 wins the deal. Press enter to continue.')
                input()
                return 1
            elif p2_cut.num_rank < p1_cut.num_rank:
                self.set_message(
                    cut_message, 'Player 2 wins the deal. Press enter to continue.')
                input()
                return 2
            else:
                self.set_message(cut_message + ' Cut is tied. Cut again.',
                                 'Enter number between 4 and 36 or press enter for random cut.')

    # Shuffle the deck and deal
    def deal_hands(self):
        self.deck = Deck()
        self.deck.shuffle()
        hands = self.deck.deal_hands()
        if self.dealer == 1:
            self.player1.hand = Hand(hands['dealer'])
            self.player2.hand = Hand(hands['pone'])
        else:
            self.player2.hand = Hand(hands['dealer'])
            self.player1.hand = Hand(hands['pone'])

    # Get discards from both players to the crib
    def get_discards(self):
        # Update UI
        base_messages = ['You can use the numbers 2-10 as well as A, T, J, Q, and K',
                         '',
                         'If you want to specify, you can include the first letter of the suit:',
                         self.SPADES + ', ' + self.HEARTS + ', ' + self.CLUBS + ', or ' + self.DIAMONDS,
                         '',
                         'If you don\'t care which suit is discarded, you don\'t need to include it.']
        messages = base_messages.copy()
        if self.dealer == 1:
            messages.insert(0,
                            'Your deal. Enter two cards for your crib. (Spacing between them is optional)')
        else:
            messages.insert(0,
                            'Computer\'s deal. Enter two cards for the computer\'s crib. (Spacing between them is optional)')
        self.set_message(*messages)
        self.crib = Hand(is_crib=True)
        # Get discards from the players until they provide valid ones
        while True:
            try:
                self.crib.cards.extend(self.player1.select_discards())
                self.crib.cards.extend(self.player2.select_discards())
                self.draw_game()
                if len(self.crib.cards) == 4:
                    break
                else:
                    raise Exception
            except Exception:
                # Print the traceback if in debug mode so it can be seen in scrollback
                if self.debug:
                    traceback.print_exc()
                messages = base_messages.copy()
                messages.insert(0,
                                'Invalid input. Enter two cards for your crib, separated by a space.')
                self.set_message(*messages)
                continue

    # Cut the deck to get the upcard
    def get_upcard(self):
        if self.dealer == 1:
            self.upcard = self.deck.cards.pop(self.player2.cut_deck())
            self.set_message('Computers cuts ' +
                             str(self.upcard) + '. Press enter to continue.')
            input()
        else:
            self.set_message('Cut the deck to determine shared cut card.',
                             'Enter number between 4 and 36 or press enter for random cut.')
            self.upcard = self.deck.cards.pop(self.player1.cut_deck())
            self.set_message('You cut ' + str(self.upcard) +
                             '. Press enter to continue.')
            input()

        self.draw_game()

    # The flow of the cribbage game happens here
    def play(self):
        # Cut the deck to determine who deals
        self.dealer = self.get_dealer()

        while self.player1.score < 121 and self.player2.score < 121:
            self.deal_hands()
            self.get_discards()
            self.get_upcard()
            break


# Jump right into the part I'm currently testing
# game = Game(1, 3, True)
# game.dealer = 1
# game.deal_hands()
# cards = [Card(10, 's'),
#          Card(12, 's'),
#          Card(13, 's'),
#          Card(10, 'd'),
#          Card(12, 'd'),
#          Card(13, 'c')]
# game.player1.hand.cards = cards
# game.get_discards()
# game.get_upcard()


# exit()


debug = False
num_players = input('Enter 1 or 2 for number of players (default 1):')
if num_players == '2':
    num_players = 2
    difficulty = 0
else:
    num_players = 1
try:
    difficulty = input(
        'Enter 1 for easy difficulty, 2 for medium, 3 for hard (default 2):')
    if difficulty[-1] == 'D':
        verify = input(
            'Did you mean to enable debug mode? y/n (default n):')[0].lower()
        if verify == 'y':
            debug = True
    if difficulty == '1' or difficulty == '3':
        difficulty = int(difficulty[0])
    else:
        raise Exception
except Exception:
    difficulty = 2
    debug = False


game = Game(num_players, difficulty, True)
game.play()
