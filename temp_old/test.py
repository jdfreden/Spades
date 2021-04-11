from temp_old.game import *
from temp_old.helper import *

import random
import numpy as np

"""
Spades:
    Ace
    King
    Jack
    6
    2
Hearts:
    Ace
    Queen
Clubs:
    King
    9
    5
    4
    3
Diamonds
    Queen
"""
n = [Card(Suit.spade, 14),
     Card(Suit.spade, 13),
     Card(Suit.spade, 11),
     Card(Suit.spade, 6),
     Card(Suit.spade, 2),
     Card(Suit.heart, 14),
     Card(Suit.heart, 12),
     Card(Suit.club, 13),
     Card(Suit.club, 9),
     Card(Suit.club, 5),
     Card(Suit.club, 4),
     Card(Suit.club, 3),
     Card(Suit.diamond, 12)]

hands = {p: [] for p in Player}

hands[Player.north] = n

deck = SpadesState(Player.north).GetCardDeck()

deck = [card for card in deck if card not in n]
random.shuffle(deck)
for p in Player:
    if p != Player.north:
        hands[p] = deck[:13]
        deck = deck[13:]

print(hands)


table_1 = [[0.997, 0.966, 0.817],  # 0
           [0.994, 0.942, 0.733],  # 1
           [0.990, 0.907, 0.624],  # 2
           [0.983, 0.855, 0.489],  # 3
           [0.970, 0.779, 0.350],  # 4
           [0.948, 0.678, 0.212],  # 5
           [0.915, 0.544, 0.095],  # 6
           [0.857, 0.381, 0.025],  # 7
           [0.774, 0.214, 0],  # 8
           [0.646, 0.074, 0],  # 9
           [0.462, 0, 0],  # 10
           [0.227, 0, 0]]  # 11

# rows is the number of cards the player has of a given suit
table_1_mod = [[0, 0, 0],  # 0
               [0.994, 0, 0],  # 1
               [0.990, 0.907, 0],  # 2
               [0.983, 0.855, 0.489],  # 3
               [0.970, 0.779, 0.350],  # 4
               [0.948, 0.678, 0.212],  # 5
               [0.915, 0.544, 0.095],  # 6
               [0.857, 0.381, 0.025],  # 7
               [0.774, 0.214, 0],  # 8
               [0.646, 0.074, 0],  # 9
               [0.462, 0, 0],  # 10
               [0.227, 0, 0]]  # 11

a = np.asarray(table_1_mod)


def side_suit_high(table, suitHand):
    ret = []
    for card in suitHand:
        if card.val in [12, 13, 14]:
            num_of_suit = len(suitHand)
            ret.append(table[num_of_suit][14 - card.val])
    return ret



def spade_betting(spadeHand):
    spadeHand.sort(key=lambda x: x.val, reverse=True)
    tricks = 0
    for i in range(len(spadeHand)):
        card = spadeHand[i]
        if card.val == 14:
            tricks += 1
        elif card.val in [13, 12, 11]:
            # if number of cards greater than 'card' tricks +=1
            protectors = (14 - card.val) - len(spadeHand[:i])
            if len(spadeHand[i:]) - 1 >= protectors:
                tricks += 1
    if len(spadeHand) > 4:
        tricks += len(spadeHand) - 4
    return tricks



ssh = []
for suit in Suit:
    sub = list(filter(lambda x: x.suit == suit, hands[Player.north]))
    if suit != Suit.spade:
        ssh.extend(side_suit_high(a, sub))
    else:
        print(spade_betting(sub))

ssh = np.asarray(ssh)
print(ssh.sum())

n = [Card(Suit.spade, 14),
     Card(Suit.spade, 13),
     Card(Suit.spade, 12),
     Card(Suit.spade, 11),
     Card(Suit.spade, 10),
     Card(Suit.spade, 9),
     Card(Suit.spade, 8),
     Card(Suit.spade, 7),
     Card(Suit.spade, 6),
     Card(Suit.spade, 5),
     Card(Suit.spade, 4),
     Card(Suit.spade, 3),
     Card(Suit.spade, 2)]


hands = {p: [] for p in Player}

hands[Player.north] = n

deck = SpadesState(Player.north).GetCardDeck()

deck = [card for card in deck if card not in n]
random.shuffle(deck)
for p in Player:
    if p != Player.north:
        hands[p] = deck[:13]
        deck = deck[13:]

#print(hands)

ss = SpadesState(Player.west)
ss.playerHands = hands

print(ss.GetMoves())
