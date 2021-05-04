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

    def test_updatefrombets(self):
        random.seed(123)
        ss = SpadesGameState(Player.north)
        pt = ProbabiltyTable(4, 52, 4)

        for p in Player:
            pt.setupPlayer(ss.playerHands, p)

        ss.bets[Player.south] = 0
        pt.updateFromBets(ss.bets, Player.north)
        pt.updateFromBets(ss.bets, Player.east)

        self.assertAlmostEqual(0, pt[Player.north, Player.south, Card(Suit.spade, 14)])
        self.assertAlmostEqual(0, pt[Player.east, Player.south, Card(Suit.spade, 14)])
        self.assertAlmostEqual(.5, pt[Player.north, Player.east, Card(Suit.spade, 14)])
        # pt.printPlayersView(Player.north)
        ss.bets[Player.west] = 0
        pt.updateFromBets(ss.bets, Player.north)
        self.assertAlmostEqual(0, pt[Player.north, Player.west, Card(Suit.spade, 14)])

    def test_updatefromdiscards(self):
        random.seed(123)
        ss = SpadesGameState(Player.north)
        pt = ProbabiltyTable(4, 52, 4)

        for p in Player:
            pt.setupPlayer(ss.playerHands, p)

        m = random.choice(ss.GetMoves())
        ss.DoMove(m)
        m = random.choice(ss.GetMoves())
        ss.DoMove(m)
        m = random.choice(ss.GetMoves())
        ss.DoMove(m)
        m = random.choice(ss.GetMoves())
        ss.DoMove(m)

        pt.updateFromDiscards(Player.north, ss.discards)
        self.assertAlmostEqual(0, pt[Player.north, Player.east, Card(Suit.diamond, 9)])
        self.assertAlmostEqual(0, pt[Player.north, Player.west, Card(Suit.diamond, 9)])

    def test_updateSuit(self):
        random.seed(123)
        ss = SpadesGameState(Player.north)
        pt = ProbabiltyTable(4, 52, 4)

        for p in Player:
            pt.setupPlayer(ss.playerHands, p)


        pt.updateSuit(Player.north, Player.east, Suit.spade)

        self.assertEqual(0, pt[Player.north, Player.east, Card(Suit.spade, 14)])
        self.assertEqual(0, pt[Player.north, Player.east, Card(Suit.spade, 4)])

        print(pt.printPlayersView(Player.north))
        self.assertAlmostEqual(.500, pt[Player.north, Player.west, Card(Suit.spade, 14)])

        pt.updateSuit(Player.west, Player.east, Suit.spade)

        self.assertEqual(0, pt[Player.west, Player.east, Card(Suit.spade, 14)])
        self.assertEqual(0, pt[Player.west, Player.east, Card(Suit.spade, 4)])
