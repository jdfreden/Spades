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

        state.playerHands[Player.north] = [Card(Suit.spade, 2), Card(Suit.spade, 14), Card(Suit.diamond, 2),
                                           Card(Suit.club, 2)]
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

    # TODO: Write tests from DoMove

    def test_scorehand(self):
        # Cases to think about make and miss in each
        #   1. Player bets a non-zero and non-13 amount
        #   2. Player bets 0 (NIL)
        #   3. Player bets 13 (Shoot the moon)
        random.seed(123)
        state1 = SpadesGameState(Player.north)

        # 1 Make
        state1.bets[Player.north] = 1
        state1.tricksTaken[Player.north] = 3

        # 1 Miss
        state1.bets[Player.east] = 5
        state1.tricksTaken[Player.east] = 1

        # 2 Make
        state1.bets[Player.south] = 0
        state1.tricksTaken[Player.south] = 0

        # 2 Miss
        state1.bets[Player.west] = 0
        state1.tricksTaken[Player.west] = 1

        # Tests for 1 and 2
        points, bags = state1.scoreHand()
        self.assertEqual(12, points[Player.north])
        self.assertEqual(2, bags[Player.north])

        self.assertEqual(-50, points[Player.east])
        self.assertEqual(0, bags[Player.east])

        self.assertEqual(100, points[Player.south])
        self.assertEqual(0, bags[Player.south])

        self.assertEqual(-100, points[Player.west])
        self.assertEqual(1, bags[Player.west])

        # Change North/East bet and trick to test 3
        # 3 Make
        state1.bets[Player.north] = 13
        state1.tricksTaken[Player.north] = 13

        # 3 Miss
        state1.bets[Player.east] = 13
        state1.tricksTaken[Player.east] = 1

        points, bags = state1.scoreHand()

        self.assertEqual(260, points[Player.north])
        self.assertEqual(0, bags[Player.north])

        self.assertEqual(-130, points[Player.east])
        self.assertEqual(0, bags[Player.east])

    def test_domove(self):
        random.seed(123)
        state1 = SpadesGameState(Player.north)

        for p in Player:
            state1.playerHands[p] = state1.playerHands[p][:5]

        # Everyone follows suit
        state1.DoMove(Card(Suit.diamond, 9))

        self.assertEqual([Card(Suit.club, 5), Card(Suit.club, 12), Card(Suit.diamond, 10), Card(Suit.spade, 6)],
                         state1.playerHands[Player.east])

        state1.DoMove(Card(Suit.diamond, 8))
        state1.DoMove(Card(Suit.diamond, 4))
        state1.DoMove(Card(Suit.diamond, 12))

        self.assertEqual(1, state1.tricksTaken[Player.north])
        self.assertEqual(Player.north, state1.playerToMove)
        self.assertFalse(state1.trumpBroken)

        # Break Trump this round
        state1.DoMove(Card(Suit.heart, 13))
        state1.DoMove(Card(Suit.spade, 6))

        self.assertTrue(state1.trumpBroken)

        state1.DoMove(Card(Suit.heart, 4))
        state1.DoMove(Card(Suit.heart, 10))

        self.assertEqual(1, state1.tricksTaken[Player.north])
        self.assertEqual(1, state1.tricksTaken[Player.east])
        self.assertEqual(Player.east, state1.playerToMove)
        self.assertTrue(state1.trumpBroken)

        # end the hand and the game

        for p in Player:
            state1.playerHands[p] = state1.playerHands[p][:1]

        for p in Player:
            if p != Player.north:
                state1.DoMove(state1.GetMoves()[0])
        state1.bets = {Player.north: 1, Player.east: 1, Player.south: 1, Player.west: 0}
        state1.NSscore[0] = 400
        state1.DoMove(state1.GetMoves()[0])

        self.assertEqual(0, state1.tricksInRound)
