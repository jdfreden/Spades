from Types.types import *
from game import *

import random


def main():
    ss = SpadesState(Player.north)
    # TODO: Figure out why this has stopped working after I added some of the betting logic
    print(ss.bets)
    while ss.GetMoves():
        print(ss.GetMoves())
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
