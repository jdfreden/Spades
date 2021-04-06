import numpy as np

# This betting scheme is inspired by 'Bidding in Spades' by Cohensius et al.

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
table_1_mod = np.asarray([[0, 0, 0],  # 0
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
                          [0.227, 0, 0]])  # 11


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
