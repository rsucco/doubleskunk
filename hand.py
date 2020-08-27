from card import Card
from score import Score
from deck import Deck
from itertools import chain, combinations
from statistics import mean, pstdev
from multiprocessing import Pool, cpu_count
from sys import maxsize


class Hand:
    def __init__(self, cards=[], is_crib=False, upcard=Card()):
        self.cards = cards
        self.upcard = upcard
        self.is_crib = is_crib

    def __str__(self):
        return ', '.join(str(card) for card in sorted(self.allCards(), key=lambda card: card.num_rank) if card.num_rank != 0)

    # Return all of the cards of the hand plus the upcard as a single list of Cards
    def allCards(self):
        return chain(self.cards, [self.upcard])

    # Draw a single card and add it to the hand
    def draw_card(self, card):
        self.cards.append(card)

    # Remove the indicated card from the hand
    def discard(self, card):
        self.cards.remove(card)

    # Count all of the scores in the hand
    def count(self, verbose=False):
        scores = {'15s': self.count_15s(),
                  'pairs': self.count_pairs(),
                  'runs': self.count_runs(),
                  'flush': self.count_flush(),
                  'nibs': self.count_nibs()}
        total_score = 0
        for score_type in scores.values():
            if len(score_type) > 0:
                for score in score_type:
                    total_score += score.points
        if verbose:
            running_score = 0
            if len(scores['15s']) > 0:
                for i, fifteen in enumerate(scores['15s']):
                    running_score += 2
                    print('15 for ' + str(running_score) + ':')
                    print(fifteen)
            if len(scores['pairs']) > 0:
                for pair in scores['pairs']:
                    running_score += 2
                    print('Pair for ' + str(running_score) + ':')
                    print(pair)
            if len(scores['runs']) > 0:
                for run in scores['runs']:
                    running_score += run.points
                    run_length = str(run.points)
                    print(run_length + '-card run for ' +
                          str(running_score) + ':')
                    print(run)
            if len(scores['flush']) > 0:
                flush_size = str(scores['flush'][0].points)
                running_score += int(flush_size)
                print(flush_size + '-card flush for ' +
                      str(running_score) + ':')
                # There can only be one flush, so it will always be a list size of one
                print(scores['flush'][0])
            if len(scores['nibs']) > 0:
                running_score += 1
                print('Nibs for ', running_score, ':')
                # You can only have nibs once, list size will be one
                print(scores['nibs'][0])
            print('\nTotal score:', total_score)
        return total_score

    # Each distinct combination of cards that adds up to 15 is worth 2 points
    def count_15s(self):
        fifteens = set()
        # Check every unique combination of cards to see if they sum to 15
        for i in range(2, 6):
            card_combos = combinations(self.allCards(), i)
            for combo in card_combos:
                if sum((card.value for card in combo)) == 15:
                    # Store the combination as a Score object
                    fifteens.add(Score(combo, 2))
        return fifteens

    # A pair is 2 of a kind for 2 points, pair royal is 3 of a kind of 6 points, and pair double royal is 4 of a kind for 12
    def count_pairs(self):
        pairs = set()
        # Iterate through every combination of two cards. If they match, they're a pair
        card_combos = combinations(self.allCards(), 2)
        for combo in card_combos:
            if combo[0].rank == combo[1].rank:
                pairs.add(Score(combo, 2))
        return pairs

    def count_runs(self):
        runs = set()
        for i in range(5, 2, -1):
            card_combos = list(combinations(self.allCards(), i))
            for combo in card_combos:
                # Sort the combination of cards based on numerical rank
                sorted_combo = sorted(combo, key=lambda card: card.num_rank)
                # If it's a run, every card will be followed by the next card in the list, with the obvious exception of the last card
                if all((sorted_combo[j + 1].follows(sorted_combo[j]) for j in range(len(sorted_combo) - 1))):
                    run = Score(sorted_combo, i)
                    # Make sure the run isn't a partial copy of a longer run
                    # There's no point in checking if the run is five cards or if there aren't any other runs
                    if i == 5 or len(runs) == 0 or not any((run.cards.issubset(other_run.cards) for other_run in runs)):
                        runs.add(run)
        return runs

    # A flush is five cards in the same suit (in the hand or the crib) or four cards not including the upcard (in the hand only)
    def count_flush(self):
        flush_suit = self.cards[0].suit
        # If any card is a different suit than the first one, there can't be a flush
        for card in self.cards:
            if card.suit != flush_suit:
                return []
        # Five card flush if the upcard also matches
        if self.upcard.suit == flush_suit:
            return [Score(self.allCards(), 5)]
        # Four card flushes can't be scored in a crib
        if not self.is_crib:
            return [Score(self.cards, 4)]
        else:
            return []

    # 'His nibs', or 'a jack' is a jack in the hand of the same suit as the upcard. This can stack with a flush.
    def count_nibs(self):
        for card in self.cards:
            if card.rank == 'J' and card.suit == self.upcard.suit:
                return [Score((card, self.upcard), 1)]
        return []

    # Analyze a hand of 6 or 5 (for 3-player) hands and determine the mathematically optimal discards
    def best_discard(self, dealer, verbose=False):
        if len(self.cards) <= 4:
            raise Exception("Can only analyze best discard for full hands")
        # Create a Deck to represent all the potential upcards
        deck_remainder = Deck()
        deck_remainder.cards = [
            card for card in deck_remainder.cards if card not in self.cards]
        # Two cards must be discarded, leaving us with a 4-card hand to be analyzed
        potential_hands = list(Hand(hand)
                               for hand in combinations(self.cards, 4))
        all_hands = []

        # Get stats about how each hand performs with each potential upcard
        # Currently I'm storing more data than is necessary for the analysis I've written
        # I'll either trim the fat or elaborate on the analysis later
        # TODO Clean this mess up and add crib to the calculations
        for hand in potential_hands:
            # The two cards that aren't in this potential hand are the cards we discarded
            discard = [card for card in self.cards if card not in hand.cards]
            upcard_counts = []
            # Count the hand with each upcard
            for upcard in deck_remainder.cards:
                hand.upcard = upcard
                upcard_counts.append((upcard, hand.count()))
            hand_info = {}
            counts = [count[1] for count in upcard_counts]
            hand_info['avg'] = mean(counts)
            hand_info['max'] = [(Card(), 0)]
            hand_info['min'] = [(Card(), maxsize)]
            # Store which particular upcards lead to the min/max scores
            for count in upcard_counts:
                if count[1] > hand_info['max'][0][1]:
                    hand_info['max'] = [count]
                elif count[1] == hand_info['max'][0][1]:
                    hand_info['max'].append(count)
                if count[1] < hand_info['min'][0][1]:
                    hand_info['min'] = [count]
                elif count[1] == hand_info['min'][0][1]:
                    hand_info['min'].append(count)
            hand_info['std_dev'] = pstdev(counts)
            # Reset the upcard before storing
            hand.upcard = Card()
            hand_info['hand'] = hand
            all_hands.append(hand_info)
        all_hands = sorted(all_hands, key=lambda x: x['avg'], reverse=True)
        if verbose:
            for hand in all_hands:
                discard = [
                    card for card in self.cards if card not in hand['hand'].cards]
                print('Discard:', ', '.join(str(card) for card in discard))
                print('Your hand:', hand['hand'])
                if dealer:
                    dealer_str = '(including potential points in your crib): '
                else:
                    dealer_str = '(including net negative points given to opponent\'s crib): '
                # TODO fix the stats
                dealer_str = ': '
                print('Expected points ' +
                      dealer_str + '{:.2f}'.format(hand['avg']))
                max_cards = ', '.join([str(card[0]) for card in hand['max']])
                max_hit_odds = '(' + \
                    '{:.2f}'.format(len(hand['max']) / 46 * 100) + '% odds)'
                print('Maximum possible points (with ' +
                      max_cards + '):', hand['max'][0][1], max_hit_odds)

                min_cards = ', '.join([str(card[0]) for card in hand['min']])
                min_hit_odds = '(' + \
                    '{:.2f}'.format(len(hand['min']) / 46 * 100) + '% odds)'
                print('Minimum possible points (with ' +
                      min_cards + '):', hand['min'][0][1], min_hit_odds)
                print('Standard deviation: ' +
                      '{:.2f}'.format(hand['std_dev']))
                print('\n--------\n')
                # print('Expected points for your hand: ' +
                #       '{:.2f}'.format(hand[3]))
        return all_hands
