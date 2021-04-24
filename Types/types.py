import enum
import numpy as np


class Suit(enum.IntEnum):
    spade = 0
    club = 1
    heart = 2
    diamond = 3


class Player(enum.IntEnum):
    north = 0
    east = 1
    south = 2
    west = 3


def prettifySuit(suit):
    if suit == Suit.spade:
        sui = "S"
    elif suit == Suit.club:
        sui = "C"
    elif suit == Suit.heart:
        sui = "H"
    else:
        sui = "D"

    return sui


def prettifyValue(val):
    if val < 11:
        num = str(val)
    elif val == 11:
        num = "J"
    elif val == 12:
        num = "Q"
    elif val == 13:
        num = "K"
    else:
        num = "A"
    return num


class Card:
    def __init__(self, suit, val):
        assert 2 <= val <= 14
        self.suit = suit
        self.val = val

    def __str__(self):
        out = ""
        num = ""
        sui = ""
        num = prettifyValue(self.val)
        sui = prettifySuit(self.suit)
        out = num + "-" + sui
        return out

    def __eq__(self, other):
        return self.suit == other.suit and self.val == other.val

    def __repr__(self):
        return str(self)


class ProbabiltyTable:
    """
    Class holding the probablity table for hand inference. This is meant to be an interior class of SpadesGameState.
    Table is indexed as [depth][row][column].
    """

    def __init__(self, rows, cols, depth):
        """
        Constructor for the probability table.
        :param rows: Number of players, Indexed with the Player Enum
        :param cols: Number of cards being played, Should always be 52. Indexed by card (13 * suit) + (val - 2)
        :param depth: Number of players, Indexed with the Player Enum
        """

        self.rows = rows
        self.cols = cols
        self.depth = depth
        self.table = np.zeros((depth, rows, cols))

    def setup(self, hands):
        for players_view in Player:
            for of_player in Player:
                if players_view == of_player:
                    # set cards in hand to 1 else 0
                    for c in hands[players_view]:
                        self[players_view, of_player, c] = 1
                else:
                    for i in range(52):
                        if self[players_view, players_view, i] != 1:
                            self[players_view, of_player, i] = 1 / 3

    def updateFromBets(self, bets, player):
        for k in bets.keys():
            if k != player and bets[k] != -1:
                if bets[k] == 0:
                    aceSpadeProb = self[player, k, Card(Suit.spade, 14)]
                    self[player, k, Card(Suit.spade, 14)] = 0
                    for upk in bets.keys():
                        if upk != player and upk != k:
                            self[player, upk, Card(Suit.spade, 14)] += (aceSpadeProb / 2)

    def __repr__(self):
        return str(self.table)

    def __getitem__(self, item):
        if type(item[2]) is Card:
            idx = (item[2].suit * 13) + (item[2].val - 2)
            return self.table[item[0]][item[1]][idx]
        return self.table[item[0]][item[1]][item[2]]

    def __setitem__(self, key, value):
        if type(key[2]) is Card:
            idx = (key[2].suit * 13) + (key[2].val - 2)
        else:
            idx = key[2]

        self.table[key[0]][key[1]][idx] = value

    def printPlayersView(self, player):
        s = " "
        poss_vals = list(range(2, 15))
        for i in poss_vals:
            v = prettifyValue(i)
            s = s + v.center(7, " ")

        s = s + "\n"

        for other_player in Player:
            for suit in Suit:
                s = s + prettifySuit(suit)
                for i in poss_vals:
                    idx = (13 * suit) + (i - 2)
                    prob = str(round(self[player, other_player, idx] * 100))

                    if prob == "100":
                        prob = "#"
                    if prob == "0":
                        prob = "-"

                    s = s + prob.center(7, " ")
                if suit == Suit.club:
                    s = s + str(other_player)
                s = s + "\n"

            s = s + "\n"

        print(s)
