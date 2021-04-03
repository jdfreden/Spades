from Types.types import *
from game import *

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
    #while not ss.isOver():
     #   print(ss)
      #  ss.DoMove(random.choice(ss.GetMoves()))
    while ss.GetMoves():
        print(ss)
        if ss.playerToMove == Player.north:
            m = ISMCTS(rootstate = ss, itermax = 10, verbose = False)
        else:
            m = ISMCTS(rootstate = ss, itermax = 5, verbose = False)

        print("Best Move: " + str(m) + "\n")
        ss.DoMove(m)

    print(ss.GetResult2(Player.north))

if __name__ == "__main__":
    random.seed(123)
    main()
