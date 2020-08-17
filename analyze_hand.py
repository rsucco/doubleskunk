from deck import Deck
from hand import Hand
from card import Card
from score import Score
from time import time

dontstop = ''
print(len(dontstop))
while len(dontstop) < 1:
    from os import system
    system('clear')
    deck = Deck()
    deck.shuffle()
    cards = []
    hand = Hand(deck.deal_card(6))
    print("Dealt cards: ")
    print(Score(hand.cards, 0), '\n-----------\n')
    start = time()
    print('Best discards if the crib is yours:')
    print('-------\n')
    hand.best_discard(True, True)
    print('\n***********\n')
    print('Best discards if the crib is your opponent\'s: ')
    print('-------\n')
    hand.best_discard(False, True)
    end = time()
    print('Completed analysis in',
          "{:.2f}".format(end - start), "seconds.")
    dontstop = input("Stop? Enter a char")
