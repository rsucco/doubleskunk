from card import Card
from score import Score
from deck import Deck
from hand import Hand
from player import Player, HumanPlayer, AIPlayer
from message import Message
from colorama import Fore, Back, Style, init
from os import system, name
from sys import exit
from time import sleep
import traceback


class Game:
    BOARD_SPACE = Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + ' '

    def __init__(self, num_players=1, difficulty=3, debug=False):
        # Initialize colorama to enable styled terminal output on Windows
        init()
        # 2-person games and 2-AI games are only for testing right now
        self.players = []
        if num_players == 0:
            self.players.append(AIPlayer(difficulty))
            self.players.append(AIPlayer(difficulty))
        elif num_players == 1:
            self.players.append(HumanPlayer())
            self.players.append(AIPlayer(difficulty, debug))
        elif num_players == 2:
            self.players.append(HumanPlayer())
            self.players.append(HumanPlayer())
        self.difficulty = difficulty
        self.messages = [Message()]
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
            if self.players[0].peg_at(121):
                return Style.RESET_ALL + Style.DIM + \
                    Back.LIGHTYELLOW_EX + Style.BRIGHT + Fore.BLACK + '⬤ ' + Style.RESET_ALL
            elif self.players[1].peg_at(121):
                return Style.RESET_ALL + Style.DIM + \
                    Back.LIGHTYELLOW_EX + Style.BRIGHT + Fore.WHITE + '⬤ ' + Style.RESET_ALL
            else:
                return Style.RESET_ALL + Style.DIM + Back.LIGHTYELLOW_EX + Style.BRIGHT + Fore.BLACK + '⭕' + Style.RESET_ALL
        # Proper background colors for
        if player == self.players[0]:
            render_str = Style.RESET_ALL + Style.DIM + \
                Back.LIGHTRED_EX + Style.BRIGHT + Fore.BLACK
        elif player == self.players[1]:
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
                render_strs[0] += self.render_board_hole(i, self.players[0])
                render_strs[2] += self.render_board_hole(i, self.players[1])
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
                render_strs[0] += self.render_board_hole(i, self.players[0])
                render_strs[1] += '══'
                render_strs[2] += self.render_board_hole(i, self.players[1])
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
            render_strs[0] += VERT + self.BOARD_SPACE * \
                5 + VERT + self.BOARD_SPACE
            render_strs[1] += VERT + self.BOARD_SPACE * 2 + \
                self.render_board_hole(
                    121) + self.BOARD_SPACE + VERT + self.BOARD_SPACE
            render_strs[2] += VERT + self.BOARD_SPACE * \
                5 + VERT + self.BOARD_SPACE
            # Render the scores
            for i in range(119, 59, -1):
                if i == 119:
                    render_strs[0] += '║'
                    render_strs[1] += '╠'
                    render_strs[2] += '║'
                render_strs[0] += self.render_board_hole(i, self.players[0])
                render_strs[1] += '══'
                render_strs[2] += self.render_board_hole(i, self.players[1])
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
            padded_hand = Message(str(self.players[0].hand))
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
            Message(str(self.upcard)).center(8) + '║'
        render_strs[3] += '     ╙────────╜'
        return render_strs

    def render_ui_score(self, render_strs, player):
        render_strs[0] += '     ╓──────────╖'
        render_strs[1] += '     ║ P' + str(player + 1) + ' Score ║'
        render_strs[2] += '     ║   ' + \
            str(self.players[player].score).center(5) + '  ║'
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
        for i in range(2):
            render_strs = self.render_ui_score(render_strs, i)
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
            print(self.players[1].hand)
            print('CRIB:')
            print(self.crib)

    # Can be used directly or passed as a callback to player objects so they can write to the UI
    def set_message(self, *messages, **kwargs):
        # If the append_msg argument is passed, use it
        try:
            if kwargs['append_msg']:
                append_msg = True
            else:
                insert_msg = False
        # If the kwarg wasn't included, make it false
        except Exception:
            append_msg = False
        # Do the same for insert_msg
        try:
            if kwargs['insert_msg']:
                insert_msg = True
            else:
                insert_msg = False
        except Exception:
            insert_msg = False
        messages_list = list(Message(message) for message in messages)
        if append_msg:
            self.messages.extend(messages_list)
        elif insert_msg:
            messages_list.extend(self.messages)
            self.messages = messages_list
        else:
            self.messages = messages_list
        self.draw_game()

    # Have both players cut to determine who deals (low card deals)
    def get_dealer(self):
        self.set_message(
            'Cut to determine dealer. Low card deals; ace is low.')
        # Keep cutting until we have a winner
        while True:
            self.deck.shuffle()
            p1_cut = self.deck.cards[self.players[0].cut_deck(
                self.set_message)]
            p2_cut = p1_cut
            # Make sure they don't accidentally cut the exact same card
            # TODO Fix this to have player 2 cut the remainder of the deck after player 1's cut rather than cutting the entire deck twice
            while p2_cut == p1_cut:
                p2_cut = self.deck.cards[self.players[1].cut_deck(
                    self.set_message)]
            cut_message = 'Player 1 cuts ' + \
                str(p1_cut) + '. Player 2 cuts ' + str(p2_cut) + '.'
            if p1_cut.num_rank < p2_cut.num_rank:
                self.set_message(
                    cut_message, 'Player 1 wins the deal. Press enter to continue.')
                input()
                return 0
            elif p2_cut.num_rank < p1_cut.num_rank:
                self.set_message(
                    cut_message, 'Player 2 wins the deal. Press enter to continue.')
                input()
                return 1
            else:
                self.set_message(cut_message + ' Cut is tied. Cut again.',
                                 'Enter number between 4 and 36 or press enter for random cut.')

    # Shuffle the deck and deal
    def deal_hands(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.upcard = Card()
        hands = self.deck.deal_hands()
        self.players[self.dealer].hand = Hand(hands['dealer'])
        self.players[1 - self.dealer].hand = Hand(hands['pone'])

    # Get discards from both players to the crib
    def get_discards(self):
        self.crib = Hand(is_crib=True)
        # Get discards from the players
        self.crib.cards.extend(self.players[0].select_discards(
            self.set_message, self.dealer == 0))
        self.crib.cards.extend(self.players[1].select_discards(
            self.set_message, self.dealer == 1))
        self.draw_game()

    # Cut the deck to get the upcard
    def get_upcard(self):
        self.set_message('Cut the deck to determine shared cut card.')
        self.upcard = self.deck.cards.pop(
            self.players[1 - self.dealer].cut_deck(self.set_message))
        self.set_message('Player ' + str(self.dealer + 1) + ' cuts ' +
                         str(self.upcard) + '. Press enter to continue.')
        if self.upcard.rank == 'J':
            self.players[self.dealer].add_points(2)
            self.set_message('Player ' + str(self.dealer + 1) +
                             ' scores 2 points for heels.', append_msg=True)
        input()
        self.players[0].hand.upcard = self.players[1].hand.upcard = self.crib.upcard = self.upcard
        self.draw_game()

    # Do pegging phase until all cards are gone
    def pegging(self):
        return

    # Count hands
    def count_hands(self):
        for i in [1 - self.dealer, self.dealer]:
            scores = {'15s': self.players[i].hand.count_15s(),
                      'pairs': self.players[i].hand.count_pairs(),
                      'runs': self.players[i].hand.count_runs(),
                      'flush': self.players[i].hand.count_flush(),
                      'nibs': self.players[i].hand.count_nibs()}
            running_score = 0
            message = [
                'Player ' + str(i + 1) + '\'s hand: ' + str(self.players[i].hand), '']
            if len(scores['15s']) > 0:
                for fifteen in scores['15s']:
                    running_score += 2
                    message.append('15 for ' + str(running_score) + ':')
                    message.append(str(fifteen))
            if len(scores['pairs']) > 0:
                for pair in scores['pairs']:
                    running_score += 2
                    message.append('Pair for ' + str(running_score) + ':')
                    message.append(str(pair))
            if len(scores['runs']) > 0:
                for run in scores['runs']:
                    running_score += run.points
                    run_length = str(run.points)
                    message.append(run_length + '-card run for ' +
                                   str(running_score) + ':')
                    message.append(str(run))
            if len(scores['flush']) > 0:
                flush_size = str(scores['flush'][0].points)
                running_score += int(flush_size)
                message.append(flush_size + '-card flush for ' +
                               str(running_score) + ':')
                # There can only be one flush, so it will always be a list size of one
                message.append(str(scores['flush'][0]))
            if len(scores['nibs']) > 0:
                running_score += 1
                message.append('Nibs for ' + str(running_score) + ':')
                # You can only have nibs once, list size will be one
                message.append(str(scores['nibs'][0]))
            print(i)
            print(self.dealer)
            print(running_score)
            self.players[i].add_points(running_score)
            message.append(Style.BRIGHT + 'Total score: ' +
                           str(running_score) + Style.RESET_ALL)
            message.append('')
            message.append('Press enter to continue.')
            self.set_message(*message)
            input()

    # The high-level flow of the cribbage game happens here
    def play(self):
        # Cut the deck to determine who deals
        self.dealer = self.get_dealer()
        # Play until
        while self.players[0].score < 121 and self.players[1].score < 121:
            self.deal_hands()
            self.get_discards()
            self.get_upcard()
            # TODO pegging
            self.count_hands()
            # Switch dealer
            self.dealer = 1 - self.dealer
            # TODO count_crib


# Jump right into the part I'm currently testing
def jumpToTest():
    game = Game(1, 3, True)
    game.dealer = 1
    cards = [Card(11, 's'),
             Card(4, 's'),
             Card(5, 's'),
             Card(6, 'd')]
    game.players[0].hand = Hand(cards)
    cards = [Card(3, 'c'),
             Card(2, 'c'),
             Card(1, 'c'),
             Card(4, 'c')]
    game.players[1].hand = Hand(cards)
    cards = [Card(7, 'h'),
             Card(8, 'h'),
             Card(9, 'h'),
             Card(10, 'h')]
    game.players[0].hand.upcard = game.players[1].hand.upcard = game.upcard = Card(
        10, 's')
    game.count_hands()
    exit()


num_players = input('Enter 1 or 2 for number of players (default 1):')
if num_players == '2':
    num_players = 2
    difficulty = 0
elif num_players == 'test':
    jumpToTest()
else:
    num_players = 1
try:
    difficulty = input(
        'Enter 1 for easy difficulty, 2 for medium, 3 for hard (default 2):')
    debug = False
    if difficulty[-1] == 'D':
        verify = input(
            'Did you mean to enable debug mode? y/n (default n):')[0].lower()
        if verify == 'y':
            debug = True
        difficulty = int(difficulty[0])
except Exception:
    difficulty = 2
    debug = False


game = Game(num_players, difficulty, debug)
game.play()
