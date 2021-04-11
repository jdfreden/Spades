from unittest import TestCase
from Game import *
import random


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

    def test_getmoves(self):
        # Cases to think about:
        #   1 Leader when spades has not been broken
        #   2 Leader when spades has been broken
        #   3 Leader when spades has not been broken and only have spades to play
        #   4 Follower that has to follow suit
        #   5 Follower that is out of the follow suit
        random.seed(123)
        state = SpadesGameState(Player.west)
        self.assertEqual(state.playerToMove, Player.north)
        self.assertFalse(state.trumpBroken)

        state.playerHands[Player.north] = [Card(Suit.spade, 2), Card(Suit.spade, 14), Card(Suit.diamond, 2),
                                           Card(Suit.club, 2)]
        moves = state.GetMoves()

        # 1
        self.assertEqual([Card(Suit.diamond, 2), Card(Suit.club, 2)], moves)

        # 2
        state.trumpBroken = True
        moves = state.GetMoves()
        self.assertEqual([Card(Suit.spade, 2), Card(Suit.spade, 14), Card(Suit.diamond, 2), Card(Suit.club, 2)], moves)

        # 3
        state.trumpBroken = False
        state.playerHands[Player.north] = [Card(Suit.spade, 2), Card(Suit.spade, 14)]
        moves = state.GetMoves()
        self.assertEqual([Card(Suit.spade, 2), Card(Suit.spade, 14)], moves)

        state.playerHands[Player.north] = [Card(Suit.spade, 2), Card(Suit.spade, 14), Card(Suit.diamond, 2), Card(Suit.club, 2)]
        state.playerHands[Player.east] = [Card(Suit.spade, 3), Card(Suit.diamond, 3), Card(Suit.heart, 3)]
        state.playerToMove = Player.east

        # 4
        state.currentTrick.append((Player.north, Card(Suit.diamond, 2)))
        moves = state.GetMoves()
        self.assertEqual([Card(Suit.diamond, 3)], moves)

        # 5
        state.currentTrick = []
        state.currentTrick.append((Player.north, Card(Suit.club, 2)))
        moves = state.GetMoves()
        self.assertEqual([Card(Suit.spade, 3), Card(Suit.diamond, 3), Card(Suit.heart, 3)], moves)

