from unittest import TestCase
from Game import *


class TestSpadesGameState(TestCase):
    def test_clone(self):
        state1 = SpadesGameState(Player.north)
        self.assertEqual(state1.playerToMove, Player.east, "Intial player to move is incorrect")

        state1.NSscore = [100, 0]
        state1.EWscore = [13, 3]
        state1.playerHands[Player.north] = [Card(Suit.spade, 14)]
        state1.playerHands[Player.west] = [Card(Suit.club, 3)]

        state1_copy = state1.Clone()

        self.assertEqual(state1_copy.NSscore, state1.NSscore)
        self.assertEqual(state1_copy.EWscore, state1.EWscore)
        self.assertEqual(state1_copy.playerHands[Player.north], state1.playerHands[Player.north])
        self.assertEqual(state1_copy.playerHands[Player.west], state1.playerHands[Player.west])
        self.assertEqual(state1_copy.playerHands[Player.south], state1.playerHands[Player.south])

        # Change the state of state1 to make sure they are not linked
        state1.NSscore = [100, 1]
        self.assertEqual(state1.NSscore, [100, 1])
        self.assertEqual(state1_copy.NSscore, [100, 0])

    def test_get_card_deck(self):
        self.fail()

    def test_deal(self):
        self.fail()
