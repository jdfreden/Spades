import random

import pickle

from Game import *
from Types.types import *
import numpy as np


def card_to_int(card):
    return (13 * card.suit) + (card.val - 2)


def clean_info(info_entry):
    ret_list = []

    ph = info_entry[0]
    tricks = info_entry[1]

    for p in Player:


        bits = np.zeros(52)
        for c in ph[p]:
            bits[card_to_int(c)] = 1
        ret_list.append((tricks, bits))
    return ret_list


def main():
    num_hands = 500
    info = []
    i = 1
    ss = SpadesGameState(random.randint(0, 3))
    while i <= num_hands:
        for p in Player:
            b = np.random.poisson(4)
            if b > 13:
                b = 13
            ss.bets[p] = b
        starting_hands = ss.playerHands
        while ss.GetMoves():
            # print(ss)

            if ss.playerToMove == Player.north:
                m = ISMCTS(rootstate=ss, itermax=100, verbose=0)
            else:
                m = ISMCTS(rootstate=ss, itermax=100, verbose=0)

            # print("Best Move: " + str(m) + "\n")

            if len(ss.playerHands[Player.north]) + len(ss.playerHands[Player.east]) + \
                    len(ss.playerHands[Player.south]) + len(ss.playerHands[Player.west]) == 1:
                ss.DoMove(m)
                print("Hand" + str(i) + " Done!")
                i += 1

                info.append((starting_hands, ss.tricksTakenpast))
                break
            ss.DoMove(m)

    #print(info)

    clean_info_list = []
    for l in info:
        clean_info_list += clean_info(l)
    with open("pickled_output2.bin", mode='wb') as bf:
        pickle.dump(clean_info_list, bf)


if __name__ == "__main__":
    main()
