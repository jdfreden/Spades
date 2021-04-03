import enum


class Suit(enum.Enum):
    spade = 1
    club = 2
    heart = 3
    diamond = 4


class Player(enum.Enum):
    north = 1
    east = 2
    south = 3
    west = 4


class Card:
    def __init__(self, suit, val):
        assert 2 <= val <= 14
        self.suit = suit
        self.val = val

    def __str__(self):
        out = ""
        num = ""
        sui = ""

        if self.val < 11:
            num = str(self.val)
        elif self.val == 11:
            num = "J"
        elif self.val == 12:
            num = "Q"
        elif self.val == 13:
            num = "K"
        else:
            num = "A"

        if self.suit == Suit.spade:
            sui = "S"
        elif self.suit == Suit.club:
            sui = "C"
        elif self.suit == Suit.heart:
            sui = "H"
        else:
            sui = "D"

        out = num + "-" + sui
        return out

    def __eq__(self, other):
        return self.suit == other.suit and self.val == other.val

    def __repr__(self):
        return str(self)
