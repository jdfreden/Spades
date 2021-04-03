from Types.types import *
from game import SpadesState

import random


def main():
    ss = SpadesState(Player.north)
    # print(ss.playerHands[Player.east][0])
    # print(ss.playerHands[Player.south][0])
    # print(ss.playerHands[Player.west][0])
    # print(ss.playerHands[Player.north][9])
    #
    # ss.DoMove(Card(Suit.diamond, 9))
    # ss.DoMove(Card(Suit.club, 8))
    # ss.DoMove(Card(Suit.diamond, 14))
    # ss.DoMove(Card(Suit.spade, 13))

    #print(ss)
    print(ss.bets)
    while ss.GetMoves():
        print(ss)
        ss.DoMove(random.choice(ss.GetMoves()))


if __name__ == "__main__":
    random.seed(123)
    main()
