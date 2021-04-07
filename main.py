from game import *
from helper import format_hand_for_write
import random


def main():

    # TODO write code to output game as json so i can look it
    """
    Hand1
        -Score
        -Bets
        -Trick1
            -Play1: Card, Stats from search?
            -Play2: Card
            -Play3: Card
            -Play4: Card
    """
    game = {}
    hand_count = 0
    trick_count = 0
    play_count = 0
    ss = SpadesState(Player.north)
    while ss.GetMoves():
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
