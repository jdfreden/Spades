import random
from copy import deepcopy

from Types.types import *


# This is code copied from https://gist.github.com/kjlubick/8ea239ede6a026a61f4d
# This code is meant be be subclassed for the specific game
class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement ISMCTS in any imperfect information game,
        although they could be enhanced and made quicker, for example by using a
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1, 2, ..., self.numberOfPlayers.
    """

    def __init__(self):
        self.numberOfPlayers = 2
        self.playerToMove = 1

    def GetNextPlayer(self, p):
        """ Return the player to the left of the specified player
        """
        return (p % self.numberOfPlayers) + 1

    def Clone(self):
        """ Create a deep clone of this game state.
        """
        st = GameState()
        st.playerToMove = self.playerToMove
        return st

    def CloneAndRandomize(self, observer):
        """ Create a deep clone of this game state, randomizing any information not visible to the specified observer player.
        """
        return self.Clone()

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """
        self.playerToMove = self.GetNextPlayer(self.playerToMove)

    def GetMoves(self):
        """ Get all possible moves from this state.
        """
        raise NotImplementedError()

    def GetResult(self, player):
        """ Get the game result from the viewpoint of player.
        """
        raise NotImplementedError()

    def __repr__(self):
        """ Don't need this - but good style.
        """
        pass


class SpadesState(GameState):
    def __init__(self, dealer):
        self.numberOfPlayers = 4
        self.tricksInRound = 13
        self.NSscore = [0, 0]
        self.EWscore = [0, 0]
        self.trumpSuit = Suit.spade

        self.dealer = dealer
        self.playerToMove = self.GetNextPlayer(self.dealer)
        self.currentTrick = []

        self.playerHands = {p: [] for p in Player}
        self.tricksTaken = {}

        self.discards = []
        self.bets = {p: 0 for p in Player}

        self.Deal()

    def Clone(self):
        st = SpadesState(self.dealer)
        st.playerToMove = self.playerToMove
        st.tricksInRound = self.tricksInRound
        st.NSscore = self.NSscore
        st.EWscore = self.EWscore
        st.playerHands = deepcopy(self.playerHands)
        st.currentTrick = deepcopy(self.currentTrick)
        st.trumpSuit = self.trumpSuit
        st.tricksTaken = deepcopy(self.tricksTaken)
        st.dealer = self.dealer
        st.discards = deepcopy(self.discards)
        st.bets = deepcopy(self.bets)

        return st

    def CloneAndRandomize(self, observer):
        st = self.Clone()

        seenCards = st.playerHands[observer] + [card for (player, card) in st.currentTrick]
        unseenCards = [card for card in st.GetCardDeck() if card not in seenCards]

        random.shuffle(unseenCards)
        for p in Player:
            if p != observer:
                numCards = len(self.playerHands[p])
                st.playerHands[p] = unseenCards[:numCards]
                unseenCards = unseenCards[numCards:]

        return st

    def GetCardDeck(self):
        return [Card(suit, val) for suit in Suit for val in range(2, 14 + 1)]

    def Bet(self, player):
        # Logic for giving bets
        # will fill this in later. Now just returning numbers
        if player == Player.north:
            self.bets[player] = 2
        elif player == Player.east:
            self.bets[player] = 1
        elif player == Player.south:
            self.bets[player] = 3
        else:
            self.bets[player] = 6

    def Deal(self):
        self.discards = []
        self.currentTrick = []
        self.tricksTaken = {p: 0 for p in Player}

        deck = self.GetCardDeck()
        random.shuffle(deck)
        for p in Player:
            self.playerHands[p] = deck[:self.tricksInRound]
            deck = deck[self.tricksInRound:]
            self.Bet(p)
        # Todo: Add Betting logic here. probably in the form of a function call giving the hand and score

    def GetNextPlayer(self, p):
        if p == Player.north:
            return Player.east
        elif p == Player.east:
            return Player.south
        elif p == Player.south:
            return Player.west
        else:
            return Player.north

    def DoMove(self, move):
        self.currentTrick.append((self.playerToMove, move))

        self.playerHands[self.playerToMove].remove(move)

        self.playerToMove = self.GetNextPlayer(self.playerToMove)

        if any(True for (player, card) in self.currentTrick if player == self.playerToMove):
            (leader, leadCard) = self.currentTrick[0]
            suitedPlays = [(player, card.val) for (player, card) in self.currentTrick if card.suit == leadCard.suit]
            trumpPlays = [(player, card.val) for (player, card) in self.currentTrick if card.suit == self.trumpSuit]
            sortedPlays = self._sortTrick(suitedPlays, trumpPlays)

            trickWinner = sortedPlays[-1][0]

            self.tricksTaken[trickWinner] += 1
            self.discards += [card for (player, card) in self.currentTrick]
            print(str(trickWinner) + " Wins")
            print(self.currentTrick)
            print("--------------------------------------------")
            self.currentTrick = []
            self.playerToMove = trickWinner

            if not self.playerHands[self.playerToMove]:
                self._score()
                if self.GetResult(Player.north) != 0:
                    self.tricksInRound = 0
                    print(self.GetResult(Player.north))
                self.Deal()

    def _score(self):
        # This does not take into account going NIL
        points = {p: 0 for p in Player}
        bags = {p: 0 for p in Player}

        for p in Player:
            if self.tricksTaken[p] >= self.bets[p]:
                bag = self.tricksTaken[p] - self.bets[p]
                bags[p] = bag
                points[p] = self.bets[p] * 10 + bag
            else:
                points[p] = self.bets[p] * -10

        self.NSscore[0] = self.NSscore[0] + points[Player.north] + points[Player.south]
        self.EWscore[0] = self.EWscore[0] + points[Player.east] + points[Player.west]
        self.NSscore[1] = self.NSscore[1] + bags[Player.north] + bags[Player.south]
        self.EWscore[1] = self.EWscore[1] + bags[Player.east] + bags[Player.west]

        if self.NSscore[1] >= 10:
            self.NSscore[0] -= 100
            self.NSscore[1] -= 10
        if self.EWscore[1] >= 10:
            self.EWscore[0] -= 100
            self.EWscore[1] -= 10

    def _sortTrick(self, suit, trump):
        suit.sort(key=lambda x: x[1])
        trump.sort(key=lambda x: x[1])
        return suit + trump

    def GetMoves(self):
        hand = self.playerHands[self.playerToMove]

        if self.currentTrick == []:
            return hand
        else:
            (leader, leadCard) = self.currentTrick[0]
            cardsInSuit = [card for card in hand if card.suit == leadCard.suit]
            if cardsInSuit != []:
                return cardsInSuit
            else:
                return hand

    def GetResult2(self, player):
        if player == Player.north or player == Player.south:
            return self.NSscore, self.EWscore
        else:
            return self.EWscore, self.NSscore

    def GetResult(self, player):
        if player == Player.north or player == Player.south:
            if self.NSscore[0] >= 400:
                return 1
            elif self.NSscore[0] < 400 and self.EWscore[0] < 400:
                return 0
            else:
                return -1
        else:
            if self.EWscore[0] >= 400:
                return 1
            elif self.NSscore[0] < 400 and self.EWscore[0] < 400:
                return 0
            else:
                return -1

    def isOver(self):
        return self.GetResult(Player.north) != 0

    def __repr__(self):
        """ Return a human-readable representation of the state
        """
        result = "%s: " % self.playerToMove
        result += ",".join(str(card) for card in self.sortHand(self.playerToMove))
        result += " | Tricks: %i" % self.tricksTaken[self.playerToMove]
        result += " | Trump: %s" % self.trumpSuit
        result += " | Trick: ["
        result += ",".join(("%s:%s" % (player, card)) for (player, card) in self.currentTrick)
        result += "]"
        result += " | Score: " + str(self.GetResult2(self.playerToMove)[0]) + " - " + str(
            self.GetResult2(self.playerToMove)[1])
        return result

    # this function is only meant to make printing hands easier to look at
    # Sort cards by value in arbitrary suit order
    #     spade = 1
    #     club = 2
    #     heart = 3
    #     diamond = 4
    def sortHand(self, player):
        sp = [card for card in self.playerHands[player] if card.suit == Suit.spade]
        cl = [card for card in self.playerHands[player] if card.suit == Suit.club]
        he = [card for card in self.playerHands[player] if card.suit == Suit.heart]
        di = [card for card in self.playerHands[player] if card.suit == Suit.diamond]
        sp.sort(key = lambda x: x.val)
        cl.sort(key = lambda x: x.val)
        he.sort(key = lambda x: x.val)
        di.sort(key = lambda x: x.val)

        return sp + cl + he + di
