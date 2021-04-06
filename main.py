from Types.types import *
from game import *

import random


def main():
    ss = SpadesState(Player.north)
    print(ss.bets)
    while ss.GetMoves():
        #print(ss.GetMoves())
        print(ss)
        if ss.playerToMove == Player.north or ss.playerToMove == Player.south:
            m = ISMCTS(rootstate = ss, itermax = 100, verbose = False)
        else:
            m = ISMCTS(rootstate = ss, itermax = 5, verbose = False)

        print("Best Move: " + str(m) + "\n")
        ss.DoMove(m)

    print(ss.GetResult2(Player.north))


if __name__ == "__main__":
    random.seed(123)
    main()
