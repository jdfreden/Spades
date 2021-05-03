import random
from unittest import TestCase

from Game import SpadesGameState
from Types.types import *


class TestProbabiltyTable(TestCase):
    def test_setup(self):
        random.seed(123)
        ss = SpadesGameState(Player.north)
        pt = ProbabiltyTable(4, 52, 4)
        for p in Player:
            pt.setupPlayer(ss.playerHands, p)

        self.assertEqual(1.0, pt[Player.north, Player.north, Card(Suit.heart, 13)])
        self.assertEqual(0, pt[Player.north, Player.north, Card(Suit.club, 2)])

        self.assertAlmostEqual(0.333, pt[Player.north, Player.east, Card(Suit.club, 2)], 3)
        # ss.bets[Player.east] = 0
        # ss.bets[Player.west] = 0
        # pt.updateFromBets(ss.bets, Player.north)
        # pt.updateSuit(Player.north, Player.east, Suit.heart)
        # print(pt.printPlayersView(Player.north))

        m = random.choice(ss.GetMoves())
        print(m)
        ss.DoMove(m)
        m = random.choice(ss.GetMoves())
        print(m)
        ss.DoMove(m)
        m = random.choice(ss.GetMoves())
        print(m)
        ss.DoMove(m)
        m = random.choice(ss.GetMoves())
        print(m)
        ss.DoMove(m)

        pt.updateFromDiscards(Player.north, ss.discards)
        print(pt.printPlayersView(Player.north))

    def test_updatefrombets(self):
        random.seed(123)
        ss = SpadesGameState(Player.north)
        pt = ProbabiltyTable(4, 52, 4)

        for p in Player:
            pt.setupPlayer(ss.playerHands, p)
        #pt.printPlayersView(Player.north)
        ss.bets[Player.east] = 0

        pt.updateFromBets(ss.bets, Player.north)
        pt.printPlayersView(Player.north)

