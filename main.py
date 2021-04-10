from game import *
from helper import *
import random


def main(keep_output = False):
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
    hand = "Hand " + str(hand_count)
    plays = []

    ss = SpadesState(Player.north)
    while ss.GetMoves():
        print(ss)

        if keep_output:
            if len(ss.playerHands[ss.GetNextPlayer(ss.dealer)]) == 13:
                stat = format_hand_for_write(ss)
                hand_count += 1
                hand = "Hand: " + str(hand_count)
                game[hand] = stat

        if ss.playerToMove == Player.north:
            m = ISMCTS(rootstate=ss, itermax=1000, verbose=False)
        else:
            m = ISMCTS(rootstate=ss, itermax=5, verbose=False)

        if keep_output:
            plays.append((m, clean_player(ss.playerToMove)))

        print("Best Move: " + str(m) + "\n")
        ss.DoMove(m)

        if keep_output:
            if not ss.currentTrick:
                trick_count += 1
                trick = "Trick " + str(trick_count)
                game[hand][trick] = plays
                plays = []

    print(str(ss.NSscore) + str(ss.EWscore))


if __name__ == "__main__":
    random.seed(123)
    main(False)
