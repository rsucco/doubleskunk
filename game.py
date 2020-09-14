from card import Card
from deck import Deck
from hand import Hand
from player import HumanPlayer, AIPlayer
from message import Message
from colorama import Fore, Back, Style, init
from os import system, name
from typing import List
import copy
import itertools


# noinspection PyBroadException
class Game:
    BOARD_SPACE = Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + ' '

    def __init__(self, num_players=1, difficulty=3, debug=False):
        # Initialize colorama to enable styled terminal output on Windows
        init()
        # 2-person games and 2-AI games are only for testing right now
        self.players = []
        if num_players == 0:
            self.players.append(
                AIPlayer(self.player_victory, 0, difficulty=difficulty, verbose=debug))
            self.players.append(
                AIPlayer(self.player_victory, 1, difficulty=difficulty, verbose=debug))
        elif num_players == 1:
            self.players.append(HumanPlayer(self.player_victory, 0))
            self.players.append(
                AIPlayer(self.player_victory, 1, difficulty=difficulty, verbose=debug))
        elif num_players == 2:
            self.players.append(HumanPlayer(self.player_victory, 0))
            self.players.append(HumanPlayer(self.player_victory, 1))
        self.difficulty = difficulty
        self.messages = [Message()]
        self.debug = debug
        self.deck = Deck()
        self.crib = Hand()
        self.upcard = Card()
        self.pegging_cards = []
        self.pegging_count = -1
        self.dealer = -1
        self.pone = -1

    # Clear the screen with the appropriate terminal command for the system
    def clear(self):
        # Don't clear the screen in debug mode. This helps with debugging because it enables scrollback to see snapshots of game state change
        if not self.debug:
            if name == 'nt':
                system('cls')
            else:
                system('clear')

    # Render the top of a score section
    @staticmethod
    def render_board_top(starting_point=1) -> List[str]:
        render_str = Style.BRIGHT + Back.LIGHTYELLOW_EX + \
            Style.DIM + Fore.BLACK + '  ╓─────╖ '
        for i in range(60):
            if i == 0:
                render_str += '╓'
            elif i == 59:
                render_str += '─────╖  '
            elif i % 5 == 0:
                render_str += '───╥'
            else:
                render_str += '──'
        render_str += Style.RESET_ALL
        return render_str

    # Render the bottom of a score section
    @staticmethod
    def render_board_bottom(starting_point=1) -> List[str]:
        render_str = Style.BRIGHT + Back.LIGHTYELLOW_EX + \
            Style.DIM + Fore.BLACK + '  ╙─────╜ '
        for i in range(60):
            if i == 0:
                render_str += '╙'
            elif i == 59:
                render_str += '─────╜  '
            elif i % 5 == 0:
                render_str += '───╨'
            else:
                render_str += '──'
        render_str += Style.RESET_ALL
        return render_str

    # Render a hole with or without a peg for a given score number and player
    def render_board_hole(self, score, player=None):
        # Hole 121 needs special handling since either player's peg can go there
        if score == 121:
            if self.players[0].peg_at(121) or self.players[1].peg_at(121):
                return Style.RESET_ALL + Style.DIM + \
                    Back.LIGHTYELLOW_EX + Style.BRIGHT + Fore.BLACK + ' ●'
            else:
                return Style.RESET_ALL + Style.DIM + Back.LIGHTYELLOW_EX + Style.BRIGHT + Fore.BLACK + ' ○'
        # Proper background colors for both players
        if player == self.players[0]:
            render_str = Style.RESET_ALL + Style.DIM + \
                Back.LIGHTRED_EX + Style.BRIGHT + Fore.BLACK
        elif player == self.players[1]:
            render_str = Style.RESET_ALL + Style.DIM + \
                Back.LIGHTGREEN_EX + Style.BRIGHT + Fore.BLACK
        else:
            render_str = Style.RESET_ALL + Style.DIM + Back.LIGHTYELLOW_EX
        # Different unicode characters for if a peg is in the hole or not
        if player.peg_at(score):
            render_str += ' ●'
        else:
            render_str += ' ○'
        return render_str

    # Render the score section of the board
    def render_board_score(self, starting_point=1):
        # Vertical separator character constant
        VERT = Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + '║'
        # Separate strings for each line of the score
        render_strs = [self.BOARD_SPACE * 2,
                       self.BOARD_SPACE * 2, self.BOARD_SPACE * 2]

        # Render holes -1 through 60
        if starting_point == 1:
            # Render the starting line
            render_strs[0] += VERT
            render_strs[1] += Style.BRIGHT + \
                Back.LIGHTYELLOW_EX + Fore.BLACK + '╠═════╣ '
            render_strs[2] += VERT
            for i in [-1, 0]:
                render_strs[0] += self.render_board_hole(i, self.players[0])
                render_strs[2] += self.render_board_hole(i, self.players[1])
            render_strs[0] += ' ' + VERT + self.BOARD_SPACE
            render_strs[2] += ' ' + VERT + self.BOARD_SPACE
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
                    render_strs[0] += ' ' + VERT + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                    render_strs[1] += '═╣' + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                    render_strs[2] += ' ' + VERT + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                # Separators
                elif i % 5 == 0:
                    render_strs[0] += ' ' + VERT
                    render_strs[1] += '═╬'
                    render_strs[2] += ' ' + VERT

        # Render holes 61-121
        else:
            # Render the finish line
            render_strs[0] += VERT + self.BOARD_SPACE * \
                5 + VERT + self.BOARD_SPACE
            render_strs[1] += VERT + self.BOARD_SPACE + \
                self.render_board_hole(
                    121) + self.BOARD_SPACE * 2 + VERT + self.BOARD_SPACE
            render_strs[2] += VERT + self.BOARD_SPACE * \
                5 + VERT + self.BOARD_SPACE
            # Render the scores
            for i in range(119, 59, -1):
                # Left side
                if i == 119:
                    render_strs[0] += '║'
                    render_strs[1] += '╠'
                    render_strs[2] += '║'
                render_strs[0] += self.render_board_hole(i, self.players[0])
                render_strs[1] += '══'
                render_strs[2] += self.render_board_hole(i, self.players[1])
                # Right side
                if i == 60:
                    render_strs[0] += ' ' + VERT + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                    render_strs[1] += '═╣' + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                    render_strs[2] += ' ' + VERT + self.BOARD_SPACE + \
                        self.BOARD_SPACE + Style.RESET_ALL
                # Skunk line
                elif i == 90:
                    render_strs[0] += ' ' + VERT
                    render_strs[1] += '═S'
                    render_strs[2] += ' ' + VERT
                # Vertical separators
                elif i % 5 == 0:
                    render_strs[0] += ' ' + VERT
                    render_strs[1] += '═╬'
                    render_strs[2] += ' ' + VERT
        return render_strs

    @staticmethod
    def render_ui_messages(messages, width=80, margin_left=10):
        render_strs = [' ' * margin_left + '╓' + '─' * width + '╖']
        for message in messages:
            render_strs.append(' ' * margin_left + '║ ' +
                               message.ljust(width) + ' ║')
        render_strs.append(
            ' ' * margin_left + '╙' + '─' * width + '╜')
        return render_strs

    def render_ui_hand(self, render_strs, player, width=25, margin_left=35):
        padded_hand = Message(str(self.players[player].hand))
        render_strs[0] += ' ' * margin_left + '╓' + '─' * width + '╖'
        render_strs[1] += ' ' * margin_left + '║' + \
            'Your hand'.center(width) + '║'
        render_strs[2] += ' ' * margin_left + '║' + \
            padded_hand.center(width) + '║'
        render_strs[3] += ' ' * margin_left + '╙' + '─' * width + '╜'
        return render_strs

    def render_ui_upcard(self, render_strs):
        render_strs[0] += '     ╓────────╖'
        render_strs[1] += '     ║ Upcard ║'
        render_strs[2] += '     ║' + \
            Message(str(self.upcard)).center(8) + '║'
        render_strs[3] += '     ╙────────╜'
        return render_strs

    def render_ui_score(self, render_strs, player):
        if player == 0:
            player_start = Fore.RED
        else:
            player_start = Fore.GREEN
        render_strs[0] += '     ╓──────────╖'
        render_strs[1] += '     ║ ' + player_start + 'P' + \
            str(player + 1) + ' Score' + Style.RESET_ALL + ' ║'
        render_strs[2] += '     ║   '
        if player == self.dealer:
            render_strs[2] += Back.LIGHTBLACK_EX + Style.BRIGHT
        render_strs[2] += str(self.players[player].score).center(5) + \
            Style.RESET_ALL + '  ║'
        render_strs[3] += '     ╙──────────╜'
        return render_strs

    def render_ui_pegging(self):
        # Construct the cards piece of the interface
        card_strs = []
        # Generate a separate line for each sequence of pegging cards
        offset = ''
        for sequence in self.pegging_cards:
            card_str = offset + ' '.join(str(card) for card in sequence)
            card_strs.append(Message(str(card_str)))
            offset += '   ' * len(sequence)
        # Make height at least 2
        for i in range(2 - len(card_strs)):
            card_strs.append(Message(''))
        # The messages rendering already makes a nice box around it, so no need to reinvent the wheel here
        card_strs = self.render_ui_messages(card_strs, 27, 27)
        # Construct the pegging count
        count_strs = [Message(' Count:'), Message(
            '   ' + str(self.pegging_count))]
        count_strs = self.render_ui_messages(count_strs, 10, 50)
        # Combine them and return the result
        render_strs = [card + count for card,
                       count in itertools.zip_longest(card_strs, count_strs, fillvalue='')]
        return render_strs

    # Draw the board based on current scores
    def draw_board(self):
        print()
        # Row 1
        print(Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + ' ' * 10 +
              '0                      10                      20                      30                      40       '
              '               50                      60  ' + Style.RESET_ALL)
        print(self.render_board_top(1))
        for score_str in self.render_board_score(1):
            print(score_str)
        print(self.render_board_bottom(1))

        # Row 2
        print(self.render_board_top(61))
        for score_str in self.render_board_score(61):
            print(f'{score_str}')
        print(self.render_board_bottom(61))
        print(Style.BRIGHT + Back.LIGHTYELLOW_EX + Style.DIM + Fore.BLACK + ' ' * 9 +
              '120                     110                     100                     90                      80     '
              '                 70                      60  ' + Style.RESET_ALL)

    # Draw the informational UI
    def draw_ui(self):
        print()
        render_strs = ['', '', '', '']
        render_strs = self.render_ui_hand(render_strs, 0)
        render_strs = self.render_ui_upcard(render_strs)
        for i in range(2):
            render_strs = self.render_ui_score(render_strs, i)
        for render_str in render_strs:
            print(render_str)
        # Print pegging UI if in the pegging phase
        if self.pegging_count > -1:
            render_strs = self.render_ui_pegging()
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
                append_msg = False
        # If the kwarg wasn't included, make it false
        except Exception:
            append_msg = False
        messages_list = list(Message(message) for message in messages)
        if append_msg:
            self.messages.extend(messages_list)
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
            #  TODO Fix this to have player 2 cut the remainder of the deck after player 1's cut rather than cutting the entire deck twice
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
                self.set_message(cut_message + ' Cut is tied. Cut again.')

    # Shuffle the deck and deal
    def deal_hands(self):
        self.deck.reset()
        self.deck.shuffle()
        self.crib = Hand()
        self.upcard = Card()
        hands = self.deck.deal_hands()
        self.players[self.dealer].hand = Hand(hands['dealer'])
        self.players[self.pone].hand = Hand(hands['pone'])

    # Get discards from both players to the crib
    def get_discards(self):
        self.crib = Hand(self.players[0].select_discards(
            self.set_message, self.dealer == 0, self.players[1].score), is_crib=True)
        self.crib.cards.extend(self.players[1].select_discards(
            self.set_message, self.dealer == 1, self.players[0].score))
        self.draw_game()

    # Cut the deck to get the upcard
    def get_upcard(self):
        self.set_message('Cut the deck to determine shared cut card.')
        self.upcard = self.deck.cards.pop(
            self.players[self.pone].cut_deck(self.set_message))
        self.set_message('Player ' + str(self.pone + 1) + ' cuts ' +
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
        # Copy the pegging hands so we can discard cards from them without affecting the actual hands before the count
        pegging_hands = [copy.copy(player.hand) for player in self.players]
        player_up = self.pone
        # Set variables so the UI will start rendering the pegging interface
        self.pegging_count = 0
        # List of lists of cards, can't use the Hand class because it sorts the cards in its __str__(), but we want to track sequential order
        self.pegging_cards = [[]]
        # Track whether either player has said 'go' so far this round
        go = [False, False]
        # Update the rounds counter and add another list for the pegging UI
        rounds_played = 0

        # Keep pegging as long as at least 1 player has cards
        while any([len(hand.cards) > 0 for hand in pegging_hands]):
            # Make sure the current player hasn't said go already and that they have cards
            if not go[player_up] and len(pegging_hands[player_up].cards) > 0:
                # Get pegging input from either a human or AI player
                # Passing it the set_message callback, available cards, the pegging count, the 'go' status of the opponent, and cards played so far
                peg_input = self.players[player_up].get_peg_play(
                    self.set_message, pegging_hands[player_up], self.pegging_count, go[1 - player_up], self.pegging_cards)
                print(peg_input)
            # If the player has said go, skip their turn
            else:
                go[player_up] = True
                player_up = 1 - player_up
                continue

            # Player objects will return -1 for a go
            if peg_input == -1:
                already_said = go[player_up]
                go[player_up] = True
                # If both players have said go, then the last one to say it scores a point
                if all(go):
                    self.players[player_up].add_points(1)
                    self.set_message(
                        'Player ' + str(player_up + 1) +
                        ' scores 1 point for a go.')
                elif not already_said:
                    self.set_message(
                        'Player ' + str(player_up + 1) + ' says \'go\'!')
            # If it's not a go, it's the numerical rank of the card to play. Suit doesn't matter for this phase
            else:
                # Remove the played card from the temporary pegging hand and append it to the played pegging cards list
                peg_card = pegging_hands[player_up].discard(peg_input)
                self.pegging_cards[rounds_played].append(peg_card)
                self.set_message('Player ' + str(player_up + 1) +
                                 ' plays ' + str(peg_card))
                # Update the pegging count
                self.pegging_count += peg_card.value

                # Check for scores
                scores = []
                score = 0

                # Check for a run
                if len(self.pegging_cards[rounds_played]) >= 3:
                    # Count the last N cards for an N card run, but don't allow card 0 along with cards 2 and 3 to make a run
                    for i in range(len(self.pegging_cards[rounds_played]), 2, -1):
                        candidate_run = Hand(
                            self.pegging_cards[rounds_played][-i:]).count_runs()
                        # Check if a run was found and that its score matches what we're looking for
                        if len(candidate_run) > 0 and candidate_run[0].points == i:
                            scores.append('Player ' + str(player_up + 1) + ' scores ' + str(
                                i) + ' points for a ' + str(i) + '-card run' + '!' * (i - 2))
                            score += i
                            # If one was, break, since we only want one
                            break

                # Check for 2, 3, or 4 of a kind
                if len(self.pegging_cards[rounds_played]) >= 2:
                    # Start with the largest possible pair and work down. Don't allow duplicates, so break if we find something
                    for i in range(min(len(self.pegging_cards[rounds_played]), 4), 1, -1):
                        candidate_pair = Hand(
                            self.pegging_cards[rounds_played][-i:]).count_pairs(i)
                        if len(candidate_pair) > 0:
                            pair = candidate_pair[0]
                            msg = 'Player ' + \
                                str(player_up + 1) + ' scores ' + \
                                str(pair.points) + \
                                ' points for a '
                            if i == 2:
                                msg += 'pair.'
                            elif i == 3:
                                msg += 'pair royal!!!'
                            elif i == 4:
                                msg += 'pair double royal!!!!!!'
                            scores.append(msg)
                            score += pair.points
                            break

                # A count equal to 15 is worth 2 points
                if self.pegging_count == 15:
                    score += 2
                    scores.append('Player ' + str(player_up + 1) +
                                  ' scores 2 points for 15.')

                # 31 scores 2 points and starts a new round without a go
                if self.pegging_count == 31:
                    score += 2
                    scores.append('Player ' + str(player_up + 1) +
                                  ' scores 2 points for 31.')
                # Last card scores 1 point if it's not 31
                elif not any([len(hand.cards) > 0 for hand in pegging_hands]):
                    score += 1
                    scores.append('Player ' + str(player_up + 1) +
                                  ' scores 1 point for last card.')
                # If the player played their last card and the opponent will have to say go, give them a go
                elif len(pegging_hands[player_up].cards) == 0 and \
                        not any([card.value + self.pegging_count <= 31 for card in pegging_hands[1 - player_up].cards]):
                    score += 1
                    scores.append('Player ' + str(player_up + 1) +
                                  ' scores 1 point for a go.')
                    go = [True, True]
                # Print scores for the play and add points if there were any
                if len(scores) > 0:
                    self.players[player_up].add_points(score)
                    self.set_message(*scores, append_msg=True)
            self.set_message('Press enter to continue.', append_msg=True)
            input()
            # Reset for the next round if both players either have an empty hand or have said go, or if the count is 31
            if all([len(hand.cards) == 0 or go[i] for i, hand in enumerate(pegging_hands)]) or self.pegging_count == 31:
                self.pegging_cards.append([])
                self.pegging_count = 0
                rounds_played += 1
                # If a player has no cards, make sure their go status is True, otherwise reset
                go = [len(hand.cards) == 0 for hand in pegging_hands]
            # Next player is up
            player_up = 1 - player_up
        # Reset the pegging count UI state
        self.pegging_count = -1
        self.pegging_cards = []

    # Count a hand, displaying information about the count in the UI
    def count_hand(self, hand):
        scores = {'15s': hand.count_15s(),
                  'pairs': hand.count_pairs(2),
                  'pair_royal': hand.count_pairs(3),
                  'pair_double_royal': hand.count_pairs(4),
                  'runs': hand.count_runs(),
                  'flush': hand.count_flush(),
                  'nibs': hand.count_nibs()}
        running_score = 0
        message = []
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
        if len(scores['pair_royal']) > 0:
            for pair_royal in scores['pair_royal']:
                running_score += 6
                message.append('Pair royal for ' + str(running_score) + ':')
                message.append(str(pair_royal))
        if len(scores['pair_double_royal']) > 0:
            for pair_double_royal in scores['pair_double_royal']:
                running_score += 12
                message.append('Pair double royal for ' +
                               str(running_score) + ':')
                # There can only be one pair double royal in a hand
                message.append(str(pair_double_royal))
        if len(scores['runs']) > 0:
            for run in scores['runs']:
                running_score += run.points
                run_length = str(run.points)
                message.append(run_length + '-card run for ' +
                               str(running_score) + ':')
                message.append(str(run))
        if len(scores['flush']) > 0:
            running_score += scores['flush'][0].points
            message.append(str(scores['flush'][0].points) + '-card flush for ' +
                           str(running_score) + ':')
            # There can only be one flush, so it will always be a list size of one
            message.append(str(scores['flush'][0]))
        if len(scores['nibs']) > 0:
            running_score += 1
            message.append('Nibs for ' + str(running_score) + ':')
            # You can only have nibs once, list size will be one
            message.append(str(scores['nibs'][0]))
        message.append('')
        message.append(Style.BRIGHT + 'Total score: ' +
                       str(running_score) + Style.RESET_ALL)
        self.set_message(*message, append_msg=True)
        return running_score

    # Show the counts of the hands and the crib
    def show_hands(self):
        for i in [self.pone, self.dealer]:
            # Display the hand before counting it
            self.set_message('Player ' + str(i + 1) +
                             '\'s hand: ' + str(self.players[i].hand) + ' [' + str(self.upcard) + ']')
            # Tally up the hand and give the player their points
            self.players[i].add_points(self.count_hand(self.players[i].hand))
            # set_message will refresh the UI to show updated scores
            self.set_message('Press enter to continue.', append_msg=True)
            input()
        # Same as above, but for the crib
        self.set_message('Player ' + str(self.dealer + 1) +
                         '\'s crib: ' + str(self.crib) + ' [' + str(self.upcard) + ']')
        self.players[self.dealer].add_points(self.count_hand(self.crib))
        self.set_message('Press enter to continue.', append_msg=True)
        input()

    # Callback method for player object to call as soon as it wins. This makes handling small frequent victory checks easier
    def player_victory(self, player_num):
        # Check for skunk (opponent scores fewer than 90 points), double skunk (fewer than 60), or triple skunk (30)
        if self.players[1 - player_num].score < 30:
            self.set_message('Player ' + str(player_num + 1) + ' utterly crushes player ' +
                             str(1 - player_num + 1) + '\'s spirit with a TRIPLE SKUNK!!!!')
        elif self.players[1 - player_num].score < 60:
            self.set_message('Player ' + str(player_num + 1) +
                             ' pulls an absolute power move with a DOUBLE SKUNK!!!')
        elif self.players[1 - player_num].score < 90:
            self.set_message('Player ' + str(player_num + 1) +
                             ' asserts their dominance with a SKUNK!!')
        else:
            self.set_message('Player ' + str(player_num + 1) + ' wins!')
        input()
        exit()

    # The high-level flow of the cribbage game happens here
    def play(self):
        # Cut the deck to determine who deals
        self.dealer = self.get_dealer()
        self.pone = 1 - self.dealer
        # Play until
        while self.players[0].score < 121 and self.players[1].score < 121:
            self.deal_hands()
            self.get_discards()
            self.get_upcard()
            self.pegging()
            self.show_hands()
            # Switch dealer and pone
            self.dealer = self.pone
            self.pone = 1 - self.dealer
