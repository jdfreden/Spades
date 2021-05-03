import enum
import numpy as np
import Game


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


class ChildSelectMode(enum.IntEnum):
    UCB = 0
    Urgency = 1


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

    def __hash__(self):
        return (self.suit * 13) + (self.val - 2)


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

    def setupPlayer(self, hands: dict, playersView: Player):
        for ofPlayer in Player:
            if playersView == ofPlayer:
                for c in hands[playersView]:
                    self[playersView, ofPlayer, c] = 1
            else:
                for i in range(52):
                    if self[playersView, playersView, i] != 1:
                        self[playersView, ofPlayer, i] = 1 / 3

    def updateFromBets(self, bets: dict, playersView: Player):
        """
        Changes the percentage of the Ace of Spades if someone bets 0
        :param bets: the betting dictionary
        :param playersView: The player that saw the bet of 0
        """
        betZero = False
        zeroBetters = []
        aceProb = 0
        for k in bets.keys():
            v = bets[k]
            if v == 0:
                zeroBetters.append(k)
                aceProb += self[playersView, k, Card(Suit.spade, 14)]
                betZero = True

        if betZero:
            for p in Player:
                if p != playersView and p not in zeroBetters:
                    self[playersView, p, Card(Suit.spade, 14)] += (aceProb / (4 - (len(zeroBetters) + 1)))

        if betZero:
            for p in zeroBetters:
                self[playersView, p, Card(Suit.spade, 14)] = 0

        print(zeroBetters)

    def updateSuit(self, playersView: Player, ofPlayer: Player, suit: Suit):
        """
        Updates prob table when someone did not follow suit
        :param playersView: Player that observed the not following
        :param ofPlayer: Player that did not follow suit
        :param suit: Lead suit
        """
        deck = [Card(suit, val) for val in range(2, 14 + 1)]

        playersProb = self[playersView, ofPlayer, :]

        for otherPlayer in Player:
            if otherPlayer != playersView and otherPlayer != ofPlayer:
                for card in deck:
                    self[playersView, otherPlayer, card] += (playersProb[card.__hash__()] / 2)

        for card in deck:
            self[playersView, ofPlayer, card] = 0

    def updateFromDiscards(self, playersView: Player, discards: list):
        for ofPlayer in Player:
            if playersView != ofPlayer:
                for card in discards:
                    self[playersView, ofPlayer, card] = 0


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
