# This is a very simple Python 2.7 implementation of the Information Set Monte Carlo Tree Search algorithm.
# The function ISMCTS(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a
# state.GetRandomMove() or state.DoRandomRollout() function.
#
# An example GameState classes for Knockout Whist is included to give some idea of how you
# can write your own GameState to use ISMCTS in your hidden information game.
#
# Written by Peter Cowling, Edward Powley, Daniel Whitehouse (University of York, UK) September 2012 - August 2013.
#
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
#
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai
# Also read the article accompanying this code at ***URL HERE***

import random
from math import sqrt, log

from helper import *
from Types.types import *
from betting import *


# TODO: When there is only one card to play skip the iterations and just play the card

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


def _sortTrick(suit, trump):
    suit.sort(key=lambda x: x[1])
    trump.sort(key=lambda x: x[1])
    return suit + trump


class SpadesState(GameState):
    def __init__(self, dealer):
        super().__init__()
        self.betting_tab = table_1_mod
        self.numberOfPlayers = 4
        self.tricksInRound = 13
        self.NSscore = [0, 0]
        self.EWscore = [0, 0]
        self.trumpSuit = Suit.spade

        self.dealer = dealer
        self.playerToMove = self.GetNextPlayer(self.dealer)
        self.currentTrick = []
        self.trumpBroken = False

        self.playerHands = {p: [] for p in Player}
        self.tricksTaken = {}

        self.discards = []
        self.bets = {p: 0 for p in Player}
        self.scoreChange = {"NS": [0, 0], "EW": [0, 0]}

        self.Deal()

    def Clone(self):
        st = SpadesState(self.dealer)
        st.playerToMove = self.playerToMove
        st.tricksInRound = self.tricksInRound
        st.NSscore = deepcopy(self.NSscore)
        st.EWscore = deepcopy(self.EWscore)
        st.playerHands = deepcopy(self.playerHands)
        st.currentTrick = deepcopy(self.currentTrick)
        st.trumpSuit = self.trumpSuit
        st.tricksTaken = deepcopy(self.tricksTaken)
        st.dealer = self.dealer
        st.discards = deepcopy(self.discards)
        st.bets = deepcopy(self.bets)
        st.trumpBroken = self.trumpBroken
        st.betting_tab = deepcopy(self.betting_tab)
        st.scoreChange = deepcopy(self.scoreChange)

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

    # TODO: Finish betting scheme
    def Bet(self, player):
        previous = {k: v for k, v in self.bets.items() if v >= 0}
        bet = []
        spade_tricks = 0
        for suit in Suit:
            sub = list(filter(lambda x: x.suit == suit, self.playerHands[player]))
            if suit != Suit.spade:
                bet.extend(side_suit_high(self.betting_tab, sub))
            else:
                spade_tricks = spade_betting(sub)
        bet = np.asarray(bet).sum()
        analyse_previous(previous, bet)
        self.bets[player] = round(bet) + spade_tricks

    def Deal(self):
        self.discards = []
        self.currentTrick = []
        self.tricksTaken = {p: 0 for p in Player}
        self.bets = {p: -1 for p in Player}
        deck = self.GetCardDeck()
        random.shuffle(deck)
        for p in Player:
            self.playerHands[p] = deck[:self.tricksInRound]
            deck = deck[self.tricksInRound:]
            self.Bet(p)

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

        if move.suit == Suit.spade and not self.trumpBroken:
            self.trumpBroken = True

        self.playerHands[self.playerToMove].remove(move)

        self.playerToMove = self.GetNextPlayer(self.playerToMove)

        if any(True for (player, card) in self.currentTrick if player == self.playerToMove):
            (leader, leadCard) = self.currentTrick[0]
            suitedPlays = [(player, card.val) for (player, card) in self.currentTrick if card.suit == leadCard.suit]
            trumpPlays = [(player, card.val) for (player, card) in self.currentTrick if card.suit == self.trumpSuit]
            sortedPlays = _sortTrick(suitedPlays, trumpPlays)

            trickWinner = sortedPlays[-1][0]

            self.tricksTaken[trickWinner] += 1
            self.discards += [card for (player, card) in self.currentTrick]
            self.currentTrick = []
            self.playerToMove = trickWinner

            if not self.playerHands[self.playerToMove]:
                points, bags = self.score()
                self._updateScore(points, bags)
                if self.NSscore[0] >= 400 or self.EWscore[0] >= 400:
                    self.tricksInRound = 0
                self.Deal()

    def score(self):
        points = {p: 0 for p in Player}
        bags = {p: 0 for p in Player}

        for p in Player:
            if self.bets[p] == 0:
                if self.tricksTaken[p] == 0:
                    points[p] = 100
                else:
                    points[p] = -100
                    bags[p] = self.tricksTaken[p]
            else:
                if self.tricksTaken[p] >= self.bets[p]:
                    bag = self.tricksTaken[p] - self.bets[p]
                    bags[p] = bag
                    points[p] = self.bets[p] * 10 + bag
                else:
                    points[p] = self.bets[p] * -10
        return points, bags

    def _updateScore(self, points, bags):
        self.scoreChange["NS"][0] = points[Player.north] + points[Player.south]
        self.scoreChange["NS"][1] = bags[Player.north] + bags[Player.south]
        self.scoreChange["EW"][0] = points[Player.east] + points[Player.west]
        self.scoreChange["EW"][1] = bags[Player.east] + bags[Player.west]

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

    def _allSpades(self, player):
        for c in self.playerHands[self.playerToMove]:
            if c.suit != Suit.spade:
                return False
        return True

    def GetMoves(self):
        hand = self.playerHands[self.playerToMove]

        if not self.currentTrick:
            # if all cards are spades and trump is not broken set trumpbroken to true and procede
            if not self.trumpBroken and self._allSpades(self.playerToMove):
                self.trumpBroken = True

            if not self.trumpBroken:
                return [c for c in hand if c.suit != Suit.spade]
            else:
                return hand
        else:
            (leader, leadCard) = self.currentTrick[0]
            cardsInSuit = [card for card in hand if card.suit == leadCard.suit]
            if cardsInSuit:
                return cardsInSuit
            else:
                return hand

    def GetResult2(self, player):
        if player == Player.north or player == Player.south:
            return self.NSscore, self.EWscore
        else:
            return self.EWscore, self.NSscore

    """
        Use this formula:
        [(Sp - 10 * Bp) - (So - 10 * Bo)] / c
        where c is a normalizing constant such that this returns a value [-0.5, 0.5]
        c = 260?
    """

    def GetResult(self, player):
        c = 130
        NS = self.scoreChange["NS"][0]
        EW = self.scoreChange["EW"][0]
        NSb = self.scoreChange["NS"][1]
        EWb = self.scoreChange["EW"][1]

        if player == Player.north or player == Player.south:
            res = ((NS - 10 * NSb) - (EW - 10 * EWb)) / c
        else:
            res = ((EW - 10 * EWb) - (NS - 10 * NSb)) / c

        # print(res)
        return res

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
        sp.sort(key=lambda x: x.val)
        cl.sort(key=lambda x: x.val)
        he.sort(key=lambda x: x.val)
        di.sort(key=lambda x: x.val)

        return sp + cl + he + di


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
    """

    def __init__(self, move=None, parent=None, playerJustMoved=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.avails = 1
        self.playerJustMoved = playerJustMoved  # the only part of the state that the Node needs later

    def GetUntriedMoves(self, legalMoves):
        """ Return the elements of legalMoves for which this node does not have children.
        """

        # Find all moves for which this node *does* have children
        triedMoves = [child.move for child in self.childNodes]

        # Return all moves that are legal but have not been tried yet
        return [move for move in legalMoves if move not in triedMoves]

    # TODO (WISH): Later in the game should the parameter be tuned for more exploitation?
    def UCBSelectChild(self, legalMoves, exploration=0.7):
        """ Use the UCB1 formula to select a child node, filtered by the given list of legal moves.
            exploration is a constant balancing between exploitation and exploration, with default value 0.7 (approximately sqrt(2) / 2)
        """

        # Filter the list of children by the list of legal moves
        legalChildren = [child for child in self.childNodes if child.move in legalMoves]

        # Get the child with the highest UCB score
        s = max(legalChildren,
                key=lambda c: float(c.wins) / float(c.visits) + exploration * sqrt(log(c.avails) / float(c.visits)))

        # Update availability counts -- it is easier to do this now than during backpropagation
        for child in legalChildren:
            child.avails += 1

        # Return the child selected above
        return s

    def AddChild(self, m, p):
        """ Add a new child node for the move m.
            Return the added child node
        """
        n = Node(move=m, parent=self, playerJustMoved=p)
        self.childNodes.append(n)
        return n

    def Update(self, terminalState):
        """ Update this node - increment the visit count by one, and increase the win count by the result of terminalState for self.playerJustMoved.
        """
        self.visits += 1
        if self.playerJustMoved is not None:
            # scores, bags = terminalState.score() # the state get dealt again before being able to score it so this doesnt work
            self.wins += terminalState.GetResult(self.playerJustMoved)

    def __repr__(self):
        return "[M:%s W/V/A: %4i/%4i/%4i]" % (self.move, self.wins, self.visits, self.avails)

    def TreeToString(self, indent):
        """ Represent the tree as a string, for debugging purposes.
        """
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
            s += c.TreeToString(indent + 1)
        return s

    def IndentString(self, indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s


def ISMCTS(rootstate, itermax, verbose=False):
    """ Conduct an ISMCTS search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
    """

    rootnode = Node()

    for i in range(itermax):
        # print(i)
        node = rootnode

        # Determinize
        state = rootstate.CloneAndRandomize(rootstate.playerToMove)

        # Select
        while state.GetMoves() != [] and node.GetUntriedMoves(
                state.GetMoves()) == []:  # node is fully expanded and non-terminal
            node = node.UCBSelectChild(state.GetMoves())
            state.DoMove(node.move)

        # Expand
        untriedMoves = node.GetUntriedMoves(state.GetMoves())
        if untriedMoves:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(untriedMoves)
            player = state.playerToMove
            state.DoMove(m)
            node = node.AddChild(m, player)  # add child and descend tree

        # Simulate

        # while state.GetMoves():  # while state is non-terminal
        #    state.DoMove(random.choice(state.GetMoves()))

        # Implement this
        while state.GetMoves():  # while state is non-terminal
            if len(state.playerHands[Player.north]) + len(state.playerHands[Player.east]) + len(
                    state.playerHands[Player.south]) + len(state.playerHands[Player.west]) == 1:
                state.DoMove(random.choice(state.GetMoves()))
                break
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node is not None:  # backpropagate from the expanded node and work back to the root node
            node.Update(state)
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if verbose:
        # TODO (WISH): write some kind of code to be able interactively interact with a given tree structure [vis-network, javascript]
        print(rootnode.TreeToString(0))
    else:
        print(rootnode.ChildrenToString())

    return max(rootnode.childNodes, key=lambda c: c.visits).move  # return the move that was most visited
