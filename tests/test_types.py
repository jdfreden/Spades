import random
from unittest import TestCase

from Game import SpadesGameState
from Types.types import *


class TestProbabiltyTable(TestCase):
    def test_setup(self):
        random.seed(123)
        ss = SpadesGameState(Player.north)
        pt = ProbabiltyTable(4, 52, 4)

        pt.setup(ss.playerHands)
        self.assertEqual(1.0, pt[Player.north, Player.north, Card(Suit.heart, 13)])
        self.assertEqual(0, pt[Player.north, Player.north, Card(Suit.club, 2)])

        self.assertAlmostEqual(0.333, pt[Player.north, Player.east, Card(Suit.club, 2)], 3)









