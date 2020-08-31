from card import Card
from score import Score
from deck import Deck
from hand import Hand
from player import Player, HumanPlayer, AIPlayer
from colorama import Fore, Back, Style, init
from os import system, name
from re import compile
from time import sleep


class Game:
    # Subclass for printing messages containing unicode characters with correct space justification
    class Message:
        def __init__(self, message=''):
            self.message = message
            self.length = len(message)

        # Generate string properly padded, taking colors and unicode into account
        def ljust(self, width):
            # Regex to strip color formatting
            REGEX = compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
            bare_str = REGEX.sub('', self.message)
            # Convert to ASCII to get rid of the unicode characters
            bare_str = bare_str.encode('ascii', errors='replace')
            # Now we can count the actual number of characters in the string and add the correct amount of padding
            padded_str = self.message
            if len(bare_str) < width:
                for i in range(width - len(bare_str)):
                    padded_str += ' '
            return padded_str

    def __init__(self, num_players=1, difficulty=3):
        # Initialize colorama to enable styled terminal output on Windows
        init()
        # 2-person games and 2-AI games are only for testing right now
        if num_players == 0:
            self.player1 = AIPlayer()
            self.player2 = AIPlayer()
        elif num_players == 1:
            self.player1 = HumanPlayer()
            self.player2 = AIPlayer()
        elif num_players == 2:
            self.player1 = HumanPlayer()
            self.player2 = HumanPlayer()
        self.difficulty = difficulty
        self.messages = [self.Message(), self.Message()]
        self.deck = Deck()
        self.crib = Hand()
        self.upcard = Card()

    # Clear the screen with the appropriate terminal command for the system
    def clear(self):
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
        # Blank board space with same background
        BOARD_SPACE = Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + ' '
        # Separate strings for each line of the score
        render_strs = [BOARD_SPACE * 2, BOARD_SPACE * 2, BOARD_SPACE * 2]

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
                    render_strs[0] += VERT + BOARD_SPACE + \
                        BOARD_SPACE + Style.RESET_ALL
                    render_strs[1] += '╣' + BOARD_SPACE + \
                        BOARD_SPACE + Style.RESET_ALL
                    render_strs[2] += VERT + BOARD_SPACE + \
                        BOARD_SPACE + Style.RESET_ALL
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
                    render_strs[0] += VERT + BOARD_SPACE + \
                        BOARD_SPACE + Style.RESET_ALL
                    render_strs[1] += '╣' + BOARD_SPACE + \
                        BOARD_SPACE + Style.RESET_ALL
                    render_strs[2] += VERT + BOARD_SPACE + \
                        BOARD_SPACE + Style.RESET_ALL
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

    def render_ui_messages(self):
        render_strs = []
        render_strs.append(
            ' ╓──────────────────────────────────────────────────────────────────────────────────╖')
        for message in self.messages:
            render_strs.append(' ║ ' + message.ljust(80) + ' ║')
        render_strs.append(
            ' ╙──────────────────────────────────────────────────────────────────────────────────╜')
        return render_strs

    def render_ui_hand(self, render_strs, player=1):
        render_strs[0] += ' ╓───────────────────────╖'
        render_strs[1] += ' ║       Your Hand       ║'
        if player == 1:
            padded_hand = self.Message(str(self.player1.hand))
            render_strs[2] += ' ║' + \
                padded_hand.ljust(23) + '║'
        render_strs[3] += ' ╙───────────────────────╜'
        return render_strs

    def render_ui_upcard(self, render_strs):
        render_strs[0] += '     ╓────────╖'
        render_strs[1] += '     ║ Upcard ║'
        render_strs[2] += '     ║' + str(self.upcard).center(8) + '║'
        render_strs[3] += '     ╙────────╜'
        return render_strs

    def render_ui_score(self, render_strs, player):
        render_strs[0] += '     ╓────────╖'
        if player == 1:
            render_strs[1] += '     ║P1 Score║'
            render_strs[2] += '     ║   ' + \
                str(self.player1.score).center(3) + '  ║'
        else:
            render_strs[1] += '     ║P2 Score║'
            render_strs[2] += '     ║   ' + \
                str(self.player2.score).center(3) + '  ║'
        render_strs[3] += '     ╙────────╜'
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
        print(Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK +
              '         120                   110                   100                   90                    80                    70                    60  ' + Style.RESET_ALL)
        print(self.render_board_top(61))
        for score_str in self.render_board_score(61):
            print(f'{score_str}')
        print(self.render_board_bottom(61))
        BOARD_SPACE = Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + ' '
        print(BOARD_SPACE * 145 + Style.RESET_ALL)

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
        render_strs = self.render_ui_messages()
        for render_str in render_strs:
            print(render_str)

    # Draw the game interface
    def draw_game(self):
        self.clear()
        self.draw_board()
        self.draw_ui()

    def set_message(self, *messages):
        self.messages = list(self.Message(message) for message in messages)
        self.messages.append(self.Message('DEBUG:'))
        self.messages.append(self.Message('WHOLE DECK:'))
        self.messages.append(self.Message(str(Hand(self.deck.cards))))
        self.messages.append(self.Message('OPPONENT HAND:'))
        self.messages.append(self.Message(str(self.player2.hand)))
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
            # TODO Fix this to have player 2 cut the remainder of the deck after player 1's cut rather than the entire deck
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

    # Deal
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

    def get_discards(self):
        if self.dealer == 1:
            SPADES = str(f'{Fore.LIGHTYELLOW_EX}[s]pades ♠{Style.RESET_ALL}')
            HEARTS = str(f'{Fore.RED}[h]earts ♥{Style.RESET_ALL}')
            CLUBS = str(f'{Fore.GREEN}[c]lubs ♣{Style.RESET_ALL}')
            DIAMONDS = str(f'{Fore.BLUE}[d]iamonds ♦{Style.RESET_ALL}')
            self.set_message(
                'Your deal. Enter two cards for your crib, separated by a space.',
                'You can use the numbers 1-13 or any of the following abbreviations:',
                'A=1, T=10, J=11, Q=12, K=13',
                '',
                'If want to specify, you can include the first letter of the suit:',
                SPADES + ', ' + HEARTS + ', ' + CLUBS + ', or ' + DIAMONDS,
                '',
                'If you don\'t care which suit is discarded, you don\'t need to specify it.')

    # The flow of the cribbage game happens here
    def play(self):
        # Cut the deck to determine who deals
        self.dealer = self.get_dealer()

        while self.player1.score < 121 and self.player2.score < 121:
            self.deal_hands()
            self.get_discards()
            input()
            break


game = Game(1)
game.play()
